# Revisao de storyline — o processo completo, em 11 passos

> **Consolidado em 2026-08-28.** Eram 14 ficheiros em 12 pastas (uma pasta por passo),
> o que tornava impossivel procurar. O conteudo abaixo esta VERBATIM; so os cabecalhos
> `##` de separacao sao novos. O caminho antigo de cada bloco esta no seu cabecalho.

## Indice

- [`process/PANORAMA_ptBR.md`](#process-panorama-ptbr-md)
- [`process/01_arc_and_logline/arc_and_logline.md`](#process-01-arc-and-logline-arc-and-logline-md)
- [`process/02_task_choice_endorsement/task_choice_endorsement.md`](#process-02-task-choice-endorsement-task-choice-endorsement-md)
- [`process/03_cohesion_and_threads/cohesion_and_threads.md`](#process-03-cohesion-and-threads-cohesion-and-threads-md)
- [`process/04_beats_missing_and_worth_adding/beats.md`](#process-04-beats-missing-and-worth-adding-beats-md)
- [`process/05_craft_pacing_and_voice/craft_pacing_voice.md`](#process-05-craft-pacing-and-voice-craft-pacing-voice-md)
- [`process/06_honesty_under_pressure/honesty_flags.md`](#process-06-honesty-under-pressure-honesty-flags-md)
- [`process/07_recommendations_and_protect/recommendations_and_protect.md`](#process-07-recommendations-and-protect-recommendations-and-protect-md)
- [`process/08_underweighted_sides/underweighted_sides.md`](#process-08-underweighted-sides-underweighted-sides-md)
- [`process/09_application_scope_breadth/application_scope_breadth.md`](#process-09-application-scope-breadth-application-scope-breadth-md)
- [`process/10_specialist_check/specialist_check.md`](#process-10-specialist-check-specialist-check-md)
- [`process/11_full_arc_rereview/five_verdicts.txt`](#process-11-full-arc-rereview-five-verdicts-txt)
- [`process/11_full_arc_rereview/full_arc_rereview.md`](#process-11-full-arc-rereview-full-arc-rereview-md)
- [`process/README_old.md`](#process-readme-old-md)


---

## `process/PANORAMA_ptBR.md`

# Panorama da dissertação — a visão geral antes dos primeiros rascunhos

> **O que é este documento.** Você pediu a visão geral do todo antes de partirmos para os primeiros
> rascunhos. Este arquivo reúne, em português, a história completa que a dissertação conta, o estado
> de cada decisão que você já tomou, o que ainda falta o seu aval, e o caminho até o primeiro
> rascunho. Ele aponta para os arquivos de detalhe quando você quiser aprofundar. É
> meta-documentação (não é texto da dissertação), então é livre da lei de escrita; as frases do
> capítulo em si serão em inglês e só depois do seu aval.
>
> **Estado geral.** A revisão de narrativa (10 arquivos em `storyline/`) e a checagem de quatro
> especialistas (`10_specialist_check`) estão feitas. Você respondeu aos 11 itens de aval em
> `AVAL_NECESSARIA_ptBR.md`. Os seus "APROVO COM AJUSTE" trouxeram direções novas e muito boas — três
> delas geram sub-afirmações que pedem um último aval seu, reunidas em `AVAL_NECESSARIA_2_ptBR.md`.
> Fora isso, estamos prontos para começar a redigir.

---

## 1. A história em uma frase (a logline honesta)

**Pergunta de pesquisa:** *o aprendizado multitarefa (MTL) ajuda a predição de POI — próxima
categoria e próxima região — e do que depende a resposta?*

**A resposta, em uma frase:** um único modelo que prevê ao mesmo tempo *que tipo de lugar* uma pessoa
visitará em seguida e *em que região* deveria ser possível; um modelo conjunto ingênuo sobre um
embedding no nível do lugar **não** supera dois modelos dedicados (CBIC); a razão é a **representação**,
não a arquitetura de compartilhamento (CoUrb); e quando cada visita passa a ter o seu próprio vetor e
as duas tarefas passam a compartilhar **através de um tronco de atenção cruzada** — trocando informação
entre os dois fluxos por atenção, em vez de possuírem camadas ocultas em comum, com um caminho espacial
privado para a região — um único modelo **finalmente supera** os dois dedicados — categoria em todas as
bases, região em quatro de seis e não inferior (TOST, margem de dois pontos) nas outras duas (MobiWac).

> *Correção da re-revisão (auditor de honestidade): a versão anterior desta frase dizia "via atenção
> cruzada em vez de um tronco comum", o que negava o tronco compartilhado que o próprio mecanismo do
> MobiWac credita (o controle de congelamento atribui o ganho a "um tronco compartilhado mais forte";
> o GLOSSÁRIO define a pilha de atenção cruzada COMO o tronco). A forma licenciada é "compartilham
> através de um tronco de atenção cruzada, sem possuir camadas ocultas em comum". Nunca redigir o
> Cap. 1 a partir da frase antiga.*

Duas coisas tornam essa frase forte e honesta:
1. **É um arco de verdade** (null → diagnóstico → resolução), não um "propusemos X e funcionou". Isso é
   raro e valioso: a literatura de dissertações premiadas trata um null bem diagnosticado como sinal de
   excelência, não como fraqueza.
2. **A resolução é de dois fatores**, não de um. O ganho final veio de uma representação no nível do
   check-in **e** de uma topologia de compartilhamento redesenhada. Creditar só à representação
   contradiria o próprio texto do MobiWac. Essa é a regra de honestidade que atravessa tudo.

---

## 2. O arco em três atos (a espinha da coletânea)

| Ato | Artigo | O que fez | O resultado honesto | O que forçou em seguida |
|---|---|---|---|---|
| **Setup** | **CBIC** (2025, publicado) | Primeiro modelo conjunto: embedding no nível do lugar (DGI) + compartilhamento rígido | **Null honesto** — o conjunto não supera consistentemente dois dedicados, e custa mais para treinar. O artigo **levantou a hipótese** desse limite e os resultados a **sustentaram** ("lend weight to"), para aquela configuração. | Três hipóteses para o null; a dissertação testa a da representação primeiro |
| **Diagnóstico** | **CoUrb** (2026/SBRC, publicado) | Segura a arquitetura, **decompõe/enriquece a entrada** (espaço + tempo + categoria) | A categoria sobe muito — evidência de que a **representação** é a alavanca. (Comparação controlada: só a entrada mudou.) | Se enriquecer ajuda, qual o teto de enriquecer *no nível do lugar*? |
| **Resolução** | **MobiWac** (2026, submetido, sob revisão) | Representação no **nível do check-in** (Check2HGI) + modelo conjunto de atenção cruzada com caminho espacial privado | Um modelo conjunto **supera** os dois dedicados: categoria em todas as seis bases; região em 4/6 + não inferior (TOST ±2pp) nas outras duas | Resolve a pergunta; abre o trabalho futuro (next-POI, representação indutiva) |

**O mecanismo que faz o arco girar** (o coração intelectual): um lugar não tem identidade fixa entre
visitas — o mesmo café é almoço de quarta e balada de sábado, e um único vetor por lugar não pode
estar certo para os dois. É por isso que a representação no nível do lugar é o limite, e por isso
descer ao nível do check-in é a saída. Essa frase precisa aparecer cedo (na Introdução), como a
hipótese que a jornada testa.

---

## 3. A escolha das tarefas (a sua preocupação principal) — endossada

Este foi o ponto que você levantou, e a investigação confirmou que ele é mais profundo do que "não
prevemos o próximo lugar". **O par de tarefas evoluiu ao longo do arco:**

- CBIC e CoUrb: *classificação estática de categoria* + *próxima categoria*.
- MobiWac: *próxima categoria* + *próxima região*.

A constante é a **próxima categoria**; a segunda tarefa mudou de estática para próxima região. Isso
importa porque a reversão CBIC→MobiWac mudou **três** coisas ao mesmo tempo: a representação, a
topologia de compartilhamento **e** o par de tarefas. O arco credita as duas primeiras; a terceira
precisa ser dita em voz alta, senão um examinador lê um "gol contra".

**Como endossamos isso (a linha que você aprovou, com o seu ajuste):**
1. A mudança de tarefa é, em parte, um **corolário** da mudança de representação (sob uma
   representação por-visita, a tarefa estática vira a menos natural). — *Item 1, aprovado com ajuste.*
2. **Mais forte ainda (o seu ajuste):** as duas tarefas são escolhidas por **razão de literatura e de
   utilidade** — são mais presentes na literatura, têm mais uso em problemas reais, e alimentam a
   predição do **próximo lugar** (a tarefa mais citada), que seria um passo seguinte natural. Essa é a
   argumentação que dá força, e ela precisa aparecer junto com o corolário, não no lugar dele.
3. As duas tarefas são **coordenadas complementares da mesma próxima visita** (o tipo e a região), de
   modo que um único modelo prevê ambas para a próxima visita do mesmo usuário. — *Item 2, aprovado.*
4. **Não é mais fácil, é mais difícil:** a próxima região tem de centenas a milhares de classes (520 a
   8.501), contra sete da tarefa estática abandonada. — *fato desarmante, aprovado.*

O detalhe completo e verificado está em `02_task_choice_endorsement` (o corolário) e
`09_application_scope_breadth` (o além-da-mobilidade). As sub-afirmações novas do seu ajuste (a
comparação "mais presente na literatura" e o enquadramento "alimenta o próximo lugar") pedem um último
aval — estão no `AVAL_NECESSARIA_2_ptBR.md`, item N1.

---

## 4. O estado das 11 decisões (o que você já resolveu)

| # | Afirmação | Sua decisão | Estado / próximo passo |
|---|---|---|---|
| 1 | Mudança de tarefa é corolário da representação | **APROVO C/ AJUSTE** | Adotar a versão corrigida ("não natural", não "incoerente") **e** somar a razão de literatura/utilidade → sub-aval N1 |
| 2 | Categoria e região = duas coordenadas da próxima visita | **APROVO** | Escrever; enfatizar complementaridade e "difícil, não trivial" |
| 3 | Pergunta respondida sobre dois pares diferentes | **APROVO C/ AJUSTE** | Enquadrar via o **trabalho futuro do CBIC** + reviews de MTL → sub-aval N2 |
| 4 | Por que nível de check-in (o teto do vetor-por-lugar) | **APROVO** | Escrever a ponte na Introdução e/ou recap do Cap. 5 |
| 5 | Por que representação antes de arquitetura | **APROVO** (breve, 1 parágrafo) | Um parágrafo, como seguro contra a banca |
| 6 | CoUrb isola representação, não revisita MTL-vs-única | **APROVO C/ AJUSTE** | Trazer, mas **breve e com critério** (não quebrar o fluxo) — nota de redação |
| 7 | Nomear a reversão da transferência negativa | **APROVO C/ AJUSTE** | Adicionar o **porquê o MTL vence sem transferência positiva** → sub-aval N3 |
| 8 | Arco honesto como espinha da Introdução | **APROVO** | Escrever a Introdução em torno do arco |
| 9 | Subseção de recap CoUrb → MobiWac | **APROVO** | Escrever o recap na cabeça do Cap. 5 |
| 10 | Tabela-ponte na Introdução | **NÃO SEI** | **Resolvido:** não fazer tabela isolada; dobrar a lógica nos recaps (5/9) e no arco (8) — ver §5 |
| 11 | Motivar além da mobilidade | **APROVO C/ AJUSTE** | Buscar artigos externos para sustentar; **não** ficar só em mobilidade → sub-aval N1 + trabalho pendente (§6) |

**Regra que atravessa tudo (não precisa de aval, é lei):** a resolução é sempre de dois fatores; os
verbos ficam presos aos testes ("supera" só com superioridade pareada, "iguala" só com TOST ±2pp); o
AZ (0,00) nunca é promovido; conclusões do CBIC/CoUrb são datadas ("a conclusão daquele momento, para
aquela configuração").

---

## 5. Item 10 resolvido — a tabela-ponte

Você respondeu **"NÃO SEI"**, com receio de repetição e de ocupar espaço, e sem saber se é praxe. A
investigação resolve isso a seu favor: o exemplar do Viegas (defendido, mesmo orientador, mesmo
formato de coletânea) **não usa tabela-ponte** — ele usa **subseções de recap** (§4.2.4 e §5.2.1, "The
MTLnet framework"). Ou seja, a praxe do precedente mais próximo é exatamente o que você já aprovou nos
Itens 5, 6 e 9.

**Recomendação:** não fazer a tabela-ponte isolada. A lógica "o que cada artigo mudou → o que forçou"
já será carregada (a) pelo parágrafo do arco na Introdução (Item 8) e (b) pelas subseções de recap
(Itens 5, 6, 9). Isso respeita o seu receio de repetição e segue o precedente. A tabela que **fica** é
a de linhagem de modelos (DGI → HGI → MTLnet → ST-MTLNet → Check2HGI → modelo conjunto), que já existe
e é no nível dos *modelos*, não do *argumento* — não compete com o texto. **Confirme se concorda com
essa resolução** (é a única decisão sua ainda em aberto do documento original).

---

## 6. O que ainda não consegui fazer (e por quê)

**A busca de literatura além-da-mobilidade (Item 11) está parcial.** Você autorizou buscar artigos
externos para sustentar os usos além da mobilidade (recomendação, planejamento urbano, controle de
trânsito). Rodei a busca, mas:
- *(Atualizado na re-revisão)* Você restaurou a conexão do OpenAlex, mas o conector re-registrado
  ainda pede **autorização** no app (Configurações → Conectores → conectar o servidor de literatura).
  Assim que autorizado, a busca dedicada roda.
- O **arXiv** funcionou, mas devolveu sobretudo ruído ou trabalhos que **já estão no corpus**, e vários
  candidatos tentadores (predição de *fluxo de multidão* a nível de cidade, tipo ST-ResNet) são de uma
  **tarefa diferente** — densidade agregada, não a próxima região de um indivíduo. Citá-los como "por
  que a próxima região importa" seria uma conflação que um examinador de POI pega. Por isso, seguindo o
  fail-closed, **não proponho nenhuma citação externa nova ainda**.

**O que temos agora, verificado e seguro:** o material do próprio corpus (CBIC cita visão
computacional, PLN, saúde, recomendação; CBIC `basis` cita planejamento urbano; CoUrb cita
recomendação + análise de mobilidade urbana e a origem dos codificadores em ecologia/sensoriamento).
Detalhe em `09_application_scope_breadth`.

**Recomendação:** quando o OpenAlex reconectar, faço uma busca dedicada e **abro/verifico** cada
candidato antes de propor. Até lá, a problematização já pode ser redigida com o material do corpus, e
ampliada depois. Isso é o item N1 do `AVAL_NECESSARIA_2_ptBR.md`.

---

## 7. O mapa dos capítulos (onde cada movimento aprovado entra)

- **Cap. 1 — Introdução** (a redigir; maior alavancagem). Carrega: o arco como espinha (Item 8); as
  apostas além da mobilidade (Item 11); o mecanismo "mesmo lugar, visitas diferentes, mesmo vetor"
  (aprovado); a ponte "por que nível de check-in" (Item 4); o "por que representação antes de
  arquitetura" em um parágrafo (Item 5); a escolha das tarefas com razão de literatura/utilidade
  (Itens 1, 2, 11).
- **Cap. 2 — Fundamentos** (rascunhado; §2.1 e §2.5 são prosa real). Ajustes apontados pelos
  especialistas (ação sua): reconhecer a troca de par na página (§2.1/§2.5); escopar os 93% de
  predizibilidade no §2.1; migrar a frase "partição do mapa é a formulação padrão" para §2.1/§2.4;
  marcar o status "sob revisão" onde o resultado do MobiWac aparece.
- **Cap. 3 — CBIC** (reproduzido). Prefácio-cápsula-do-tempo (venue/status/o que é revisado depois).
- **Cap. 4 — CoUrb** (reproduzido, traduzido). Prefácio + a fronteira "isola representação, não
  revisita MTL-vs-única" (Item 6, breve); o "por que representação antes de arquitetura" pode morar
  aqui (Item 5).
- **Cap. 5 — MobiWac** (versão de registro). Subseção de recap CoUrb→MobiWac (Item 9); a ponte "por
  que check-in" pode morar aqui (Item 4).
- **Cap. 6 — Conclusão** (a redigir). A resposta em dois pares (Item 3); a reversão da transferência
  negativa + o porquê o MTL vence (Item 7); fecha o laço com a Introdução.

**Correções de governança (ação sua, apontadas pelos especialistas):** reconciliar o NORTH_STAR §4/§6
(ainda afirma o protocolo do CoUrb como fato) com a retração UW-3 ([VERIFICAR]); sincronizar o mapa de
citações do §2.3. Detalhe em `10_specialist_check` (resumo de ações no topo).

---

## 8. O caminho até o primeiro rascunho

1. **Você:** confirmar a resolução do Item 10 (§5) e avaliar os três sub-avais em
   `AVAL_NECESSARIA_2_ptBR.md` (N1 literatura/além-mobilidade; N2 o CBIC via trabalho futuro; N3 o
   porquê o MTL vence).
2. **Eu (quando o OpenAlex reconectar):** busca dedicada de âncoras além-da-mobilidade, abrindo e
   verificando cada uma; nada de citação de memória.
3. **Eu:** para cada afirmação aprovada, passar pelos revisores 07 (honestidade) e 14 (orientador
   adversarial) antes de virar frase.
4. **Eu:** redigir o **primeiro rascunho do Cap. 1 (Introdução)** em inglês — é o de maior alavancagem
   e onde a maioria dos movimentos aprovados mora. (Sugiro começar por ele; alternativa: os prefácios
   e recaps, que são curtos e destravam a unidade.)
5. **Eu:** rodar o portão de fatos (05/06/07) sobre a prosa nova; te devolver para o G4 (seu aval).

**Sugestão de ordem de escrita:** Introdução (Cap. 1) primeiro — ela fixa a voz e o arco que todo o
resto herda. Se preferir um começo menor e de baixo risco, os três prefácios-cápsula e as duas
subseções de recap são curtos, destravam a unidade da coletânea, e não dependem dos sub-avais
pendentes.

---

## Arquivos de detalhe (para aprofundar)

- `AVAL_NECESSARIA_ptBR.md` — os 11 itens originais com as suas decisões.
- `AVAL_NECESSARIA_2_ptBR.md` — **os três sub-avais novos** vindos dos seus ajustes (N1, N2, N3) + a
  confirmação do Item 10.
- `02_task_choice_endorsement` — a escolha das tarefas (o corolário, corrigido).
- `09_application_scope_breadth` — o além-da-mobilidade (material verificado do corpus).
- `10_specialist_check` — os quatro especialistas + o resumo de ações (o que está corrigido vs o que
  é ação sua).
- `01`…`08` — a revisão de narrativa completa (arco, coesão, beats, craft, honestidade,
  recomendações, lados subponderados).

---

## `process/01_arc_and_logline/arc_and_logline.md`

# Reconstructed arc, diff, and logline (lenses 1–2)

> Part of the storyline review. Extracted verbatim from the consolidated `STORY_REVIEW.md`
> (artifact of this project), unchanged except for the pass-2 note below. All result-claims trace to
> sources fixed in the project instructions; new frame claims are [NEEDS SIGN-OFF]; unverified
> external claims are [VERIFY].
>
> **Pass-2 revision (see `08_underweighted_sides/` UW-2, UW-4).** The logline's middle clause is
> sharpened: CoUrb does **not** show "MTL works" — its only baseline is MTLNet (both multi-task), so
> it isolates the *representation* effect and is silent on MTL-vs-single-task. And the research
> question is answered on **two different task pairs** (CBIC's static+sequential vs MobiWac's
> two-sequential). Read this section together with `02_task_choice_endorsement/`.
---

## A. The reconstructed arc, and the diff against the intended spine (lens 1)

### A.1 The story as it actually reads right now (one paragraph)

Location-based social networks record where people go as check-ins, and a service that anticipates
the next move can prepare ahead. Two coarse questions are enough for that: what type of place comes
next (the next category) and which part of the city (the next region); the exact next place is not
predicted. The natural engineering wish is one model for both, so the dissertation asks whether
multi-task learning helps this task pair and what the answer depends on. The first study (CBIC)
builds the first joint model on a place-level graph embedding with hard parameter sharing, and finds
an honest null: the joint model does not consistently beat two dedicated single-task models, and it
costs more to train. CBIC closes by naming three candidate explanations, one of which is that the
shared representation may not be rich enough. The second study (CoUrb) holds the architecture fixed
and replaces the single place-level input with decomposed spatial, temporal, and categorical
encoders; the category score rises sharply, which is read as evidence that the representation, not
the sharing architecture, is the lever. The third study (MobiWac) builds a representation at the
check-in level (Check2HGI), so each visit carries its own vector rather than each place carrying one
fixed vector, and pairs it with a redesigned joint model (a cross-attention trunk that exchanges
semantic context, plus a private spatial path for region). On that combination one joint model
finally outperforms both dedicated models: the next category on every dataset, and the next region
at four of six, with statistical non-inferiority (TOST, two-point margin) at the other two. The
payoff is stated as a corrected view, not a triumph: a published null result, its diagnosis, and its
resolution.

### A.2 Beat-by-beat map (delivered)

| Beat | Where it lives now | State |
|---|---|---|
| Context funnel (LBSN → anticipate next move → mobility-aware services) | MobiWac §1 p1 (strong); Ch.2 opener (weaker) | Exists in MobiWac's own intro; **not yet owned by a general Introduction** |
| The two tasks kept distinct; next place excluded | MobiWac §1 p2, §3; Ch.2 §2.1; GLOSSARY | Delivered and disciplined |
| The tension (sharing is not free; negative transfer) | CBIC §1; MobiWac §1 p3; Ch.2 §2.3, §2.5 | Delivered |
| Research question, bold inline | NORTH_STAR §1 only | **Spine-only** (Ch.1 undrafted) |
| The journey as the contribution (null → diagnosis → resolution) | NORTH_STAR §2 honest-arc ¶; Ch.2 §2.5 hinge | **Spine-only in the frame**; each paper tells only its own leg |
| CBIC leg: first joint model, honest null, three hypotheses | CBIC §1 + conclusion | Delivered in the source paper |
| CoUrb leg: hold architecture, enrich input, category rises | CoUrb §1 + conclusion | Delivered in the source paper; **cites MTLnet by name** (native bridge) |
| MobiWac leg: check-in representation + redesigned sharing → joint win | MobiWac §1, §2, §4, §6 | Delivered in the source paper |
| The mechanism (same place, different visit, same vector) | MobiWac §2.1; Ch.2 §2.2 map + §2.5 ("weekday lunch vs Saturday night") | Present, but **buried in Ch.5 related work / stated once in §2.5** |
| Objectives 1:1 with chapters | NORTH_STAR §6.1 | Spine-only |
| Recap subsections (Ch.4 recaps MTLnet, Ch.5 recaps both) | Planned (Viegas device) | **Not written** |
| Time-capsule prefaces (venue/status/what-later-revises) | Planned | **Not written** |
| Conclusion answering the question + limitations + future work | NORTH_STAR §6.4 | Spine-only |

### A.3 The diff — where the delivered arc drifts from the intended spine

The intended spine (NORTH_STAR §6) is sound and, where drafted, faithfully executed. The drift is
almost entirely **the drift of an unwritten frame**: the spine promises the connective tissue, but
the connective tissue is exactly the part that does not exist yet. Four specific drifts, in order of
consequence:

1. **The logline compresses a two-factor result into one factor.** The spine's headline is "the
   representation is the dominant factor." That is well-earned by CoUrb (which changed *only* the
   input and saw category rise). But the *resolution* — MobiWac — changed **both** the representation
   *and* the sharing topology (cross-attention two-stream + private spatial path replaced
   hard-sharing + FiLM), and its own text says sharing "helps instead of hurting" once the
   representation changes, with the private spatial path doing real work on region. So the delivered
   evidence is "representation dominates, *and* converting that into a joint win also required
   redesigning how the two tasks share." The spine knows this (it says "a check-in-level
   representation **and** the right sharing topology"), but the one-line logline does not, and an
   undrafted Introduction is where that flattening will happen if it is going to. This is the single
   highest-leverage narrative risk in the arc. (Detailed in F1 and D-MISSING-1.)

2. **CBIC opened three doors; the arc walks through one without saying why.** CBIC's conclusion lists
   three co-equal hypotheses for the null — subtle negative transfer, representation mismatch, and
   architectural restrictiveness — and its own future-work paragraph points *first* at the
   architecture door (soft sharing, Mixture-of-Experts). The dissertation instead walks the
   representation door first (CoUrb). That is a legitimate and, in hindsight, correct choice, but the
   spine's phrase "closes hypothesizing that the shared representation may not be rich enough — the
   thread the rest pulls" quietly promotes one of three hypotheses to *the* thread. Nowhere yet does
   the frame say *why representation before architecture*. That "why" is a missing beat, not a
   falsehood. (Detailed in D-MISSING-2.)

3. **The "cost" thread is opened and never closed as opened.** The intended intro (NORTH_STAR §6.1,
   beats 1–2) wishes for "one model … instead of one dedicated model per task" and frames MTL as
   promising "shared structure and lower cost." CBIC then reports the joint model cost *more*
   (convergence time, MFLOPs). MobiWac's joint model is *larger than the two dedicated models
   combined* (~4.2M vs 1.1M params at Alabama; the paper is scrupulous that the benefit is
   *operational* — one artifact, one forward pass — not arithmetic). So across the arc the "lower
   cost" wish is never delivered as compute savings; it is *redefined* to operational simplicity. The
   spine does not currently narrate that redefinition. If the Introduction promises lower cost and
   the Conclusion delivers "one deployable artifact (that costs more compute)," a banca member will
   read a quietly moved goalpost unless the frame owns the redefinition explicitly. (Detailed in F3
   and D-MISSING-3.)

4. **The mechanism is present but demoted.** The spine (§6.2 Ch.2 beat) wants the reader shown *why*
   a place-level vector is the limit — "the same POI, different visit, same vector." That mechanism
   exists in the corpus (MobiWac §2.1: "two visits to the same coffee shop look identical to the
   model"; Ch.2 §2.5: "cannot tell a weekday lunch from a Saturday night out"). But it currently
   lives in Chapter 5's related-work and in one synthesis sentence in §2.5. For a mechanism that is
   the pivot of the entire dissertation, it is under-placed: the reader should meet it in the
   Introduction, as the reason the journey turns. (Detailed in D-MISSING-4.)

None of these four is a contradiction of the spine; three of the four are *the spine's own nuances
that the one-line version drops*, and the fourth is a placement problem. The finding is that the arc
is intellectually complete and honest, and its risks are all concentrated in the frame chapters that
have not been written — which is exactly where a coletânea's unity is won or lost.

---

## B. The logline, and the per-chapter earn-its-clause verdict (lens 2)

### B.1 The logline

Stated in one sentence, problem → journey → payoff, within the whitelist:

> **A single model that predicts both what kind of place a person will visit next and where should be
> possible, yet a naive joint model on a place-level embedding does not beat two dedicated models
> (CBIC); the reason is the representation, not the sharing architecture (CoUrb); and once each visit
> carries its own vector and the two tasks share through cross-attention rather than a common trunk,
> one model finally outperforms both dedicated models — category everywhere, region at four of six
> datasets and non-inferior at the other two (MobiWac).**

That sentence is honest (verbs bound to their tests, AZ/AL not upgraded, the two-factor resolution
preserved) and it is a genuine problem→journey→payoff. It is long because the honest version *is*
long; a shorter version that keeps only "the representation is the bottleneck" is the tempting
flattening flagged in A.3-1. The recommendation table (G) proposes the frame keep the two-clause
resolution ("a representation built for visits, shared the right way"), not the one-clause one.

### B.2 Does each chapter earn its clause?

- **CBIC earns its clause — as the setup, and it is the arc's structural anchor.** Its clause is "a
  naive joint model does not beat two dedicated models." It delivers exactly that, and — this is the
  quiet strength of the whole dissertation — it delivers it as a *confirmed hypothesis*, not a
  disappointment: CBIC's introduction *predicts* the null ("the central hypothesis of this study is
  that a standard hard parameter-sharing MTL architecture will face significant limitations")
  before it reports it. A predicted null is the strongest possible foundation for a null→resolution
  arc (see §E.4: Lovitts and Mullins & Kiley, firsthand from the internal excellence doc, prize a
  null handled with a diagnosed mechanism and critical self-assessment). The clause is earned. The one risk is that CBIC's
  own framing attributes the null substantially to *task dissimilarity* ("static vs sequential"),
  which is a *different* diagnosis from the one the arc ultimately backs (representation richness).
  The frame must not let CBIC's task-dissimilarity language read as the arc's final word. (F4.)

- **CoUrb earns its clause, and it is the pivot — but it is also the weakest-owned clause.** Its
  clause is "the representation is the lever, not the architecture." It delivers a sharp category
  gain from an input-only change, which is the cleanest single piece of evidence in the whole arc
  for representation-dominance, because it is a true controlled comparison (same architecture, only
  the input changed). Three things weaken how the clause lands, none fatal: (a) CoUrb is
  second-authored (Vitor 2nd author/presenter), so the contribution note is load-bearing — the arc
  leans hardest on the paper the candidate did not lead; (b) CoUrb's protocol is sample-stratified,
  *not* user-disjoint (weaker than MobiWac), which the frame must flag as a limitation of the
  evidence, not hide (the spine already commits to this, and it *strengthens* the arc — the honest
  read is "even under a weaker protocol the representation effect was already visible"); (c) CoUrb
  changes *three* things at once (space + time + category encoders) and does not isolate them, so the
  clause it earns is "an enriched, decomposed representation helps," not "here is which axis of
  enrichment mattered." That is fine for the arc, but the frame should state the claim at the
  granularity the evidence supports.

- **MobiWac earns its clause and delivers the payoff — provided the payoff is stated as two-factor.**
  Its clause is "check-in-level representation + redesigned sharing → one model beats both." It
  delivers, and its claim discipline is the strongest in the corpus. The single narrative caution is
  the one in A.3-1: MobiWac's win is the joint effect of a new representation *and* a new sharing
  topology, and its own §2.1/§6 are careful about this. If the frame credits the win to
  representation alone, it *contradicts Chapter 5's own text* — a rare case where overclaiming the
  arc would also be internally inconsistent. Stated as two-factor, the clause is fully earned.

**Verdict:** all three chapters earn their clause. The logline moves forward at every step, with no
dead chapter. The one clause at risk of being *under-delivered* by the frame is CoUrb's (its role as
the controlled pivot is the most likely thing for an undrafted Introduction to under-sell), and the
one clause at risk of being *over-delivered* is MobiWac's (representation-only framing). Both risks
live in the frame, not the papers.

---

---

## `process/02_task_choice_endorsement/task_choice_endorsement.md`

# Endorsing the task choice in the storyline

> **What this file is.** The author raised a concern: the dissertation *changes the tasks it
> predicts*, and the storyline must endorse that choice well, because the honest motivation ("these
> tasks are more useful in the literature and more convergent with next-POI prediction") is currently
> under-argued and defensively phrased. This file (a) states the task choice precisely and verifies
> it against source, (b) gives the positive, service-first argumentation the frame should carry, (c)
> surfaces a load-bearing subtlety the first review missed — the task *pair* itself evolved — and
> shows how to turn it from a hidden confound into a strength, and (d) lists the verified anchors and
> the sign-off flags.
>
> **Fail-closed status.** An OpenAlex sweep for a cleaner external anchor (next-category /
> next-region as end-targets) returned only noise; it produced **no new citable reference**, so no new
> citation is proposed. Everything below is built on sources already in the corpus and verified this
> session (CBIC `sections/intro.tex`+`method.tex`; CoUrb `sections/intro.tex`+`metodology.tex`;
> MobiWac `sections/02_related.tex`+`03_problem.tex`; drafted Fundamentals `2.1`). New connective
> sentences are marked **[NEEDS SIGN-OFF]**.

---

## 1. What actually changed — verified across all three papers

The first review treated "the exact next place is not predicted" as the whole of the task-scope
story, and filed it as a clean, closed thread. That was an under-reading. Read against source, the
task *pair* evolved across the arc:

| Paper | Task 1 | Task 2 | Pair character | Source (verified this session) |
|---|---|---|---|---|
| **CBIC** | POI category classification (**static**, non-sequential) | next category (sequential) | one static + one sequential | `CBIC___MTL/sections/intro.tex` L38–42, `method.tex` L36–54 |
| **CoUrb** | POI category classification (**static**) | next category (sequential) | **same pair as CBIC** | `CoUrb_2026/src_en/sections/intro.tex` L4–5 |
| **MobiWac** | next category (sequential) | **next region** (sequential) | two sequential "next-X" tasks | `[mobiwac]/src/sections/03_problem.tex`; `02_related.tex` |

Two facts are now firsthand-verified and load-bearing:

1. **The constant is next category; the second task changed.** Across the arc, next category is
   predicted in all three papers. The companion task went from *static category classification*
   (CBIC, CoUrb) to *next region* (MobiWac). The word "region" appears in CoUrb only as the HGI
   embedding hierarchy (the POI–region and region–city infomax losses) and in geographic
   descriptions — **never as a prediction task**. Next region as a *task* is genuinely new to
   MobiWac.
2. **CBIC blamed the null partly on the static-vs-sequential dissimilarity of its own task pair.**
   CBIC's introduction asks, verbatim, "can a single, shared representation effectively serve two
   tasks with such distinct underlying characteristics?" and names the risk that "forcing a shared
   encoder to learn features for both a static and a sequential task could result in negative
   transfer." That is the dissimilarity of *category-classification (static) + next-category
   (sequential)*.

Put together: the CBIC → MobiWac reversal ("MTL finally helps") changed **three** things at once —
the representation (place-level → check-in-level), the sharing topology (hard sharing + FiLM →
cross-attention two-stream + private spatial path), **and** the task pair (one static + one
sequential → two sequential). The arc's headline credits the first two. The third is currently
invisible in the frame. This is the side of the story the concern correctly sensed was being lost.

---

## 2. Why the tasks are the right object — the positive argument (service-first)

The author's honest motivation is the correct spine, and it is *stronger* than the defensive phrasing
currently in MobiWac §3 ("not to make the task easier"). State it positively, and state it early.
The material is verified and already in the corpus; the work is assembly and placement, not new
claims.

**2.1 The two tasks are what a mobility-aware service can act on.** A service does not need the exact
next venue to be useful. It needs to know *what kind of place* the user is heading to (to prepare
content, offers, or capacity) and *which part of the city* (to place or provision resources). MobiWac
§1/§3 already frame category as intent ("what the user wants") and region as location ("where to
prepare"). This is the "useful in the literature" half of the author's motivation, and it is the
honest reason the tasks were chosen. *Frame move:* lift this into the Introduction's stakes paragraph
(recommendation G-9 in the pass-1 review), so the reader knows in Chapter 1 what the predictions buy.

**2.2 The two tasks are the coarse, learnable properties of the next visit — convergent with
next-POI, not a retreat from it.** Next place is one specific realization; category and region are
two orthogonal *coordinates* of that same next visit (its semantic type and its spatial cell). This
is the "convergent with next-POI" half of the motivation, and it is verifiable: the field's canonical
next-place systems *already compute* both signals internally — HMT-GRN predicts region to constrain a
beam search over places, and CatDM predicts category to prune the place candidate set
(`Lim2022`, `yu2020catdm`, both in MobiWac's bib and in the drafted §2.1). The dissertation's move is
to promote those two internal signals from *means* (intermediate steps toward a place) to *ends*
(the prediction targets themselves) — a stance a smaller body of work already takes for each target
alone (`zhu2022drrgnn` for region, `capanema2023poirgnn` for category). *Frame move:* the drafted
§2.1 already makes this "means → ends" argument well; the Introduction should echo its one-sentence
form so the task choice reads as a deliberate position, not an omission.

**2.3 Region over a map partition is the standard mobility formulation, not an invention.** MobiWac
§2.2 states, verifiably, that predicting over a partition of the map "is also the standard formulation
in the human-mobility literature, with a grid cell as the target [luca2021mobilitysurvey]; our
next-region task substitutes official neighborhood-scale units for grid cells." This pre-empts the
"why census tracts / mahalle?" question: the dissertation uses administratively meaningful units
instead of arbitrary grid squares, but the *task shape* (predict the next spatial cell) is
canonical. *Frame move:* keep this sentence in §2.1/§2.4 and reference it once in the Introduction.

**2.4 The choice does not make the problem easier — it makes it harder.** This is the rebuttal to the
sharpest suspicion ("you switched to easier tasks to manufacture a win"), and it is quantitative and
verified: next region has, depending on the dataset, **from a few hundred to several thousand
classes** (520 for Istanbul up to 8,501 for California), whereas the *dropped* static task had **seven**.
The task set got harder on the second task, not easier. Next place (the hardest, tens of thousands of
candidates) was dropped, but it was never in the MTL pair to begin with — CBIC and CoUrb never
predicted next place either. *Frame move:* state the class-count contrast plainly wherever the task
choice is defended; it is the single most disarming fact available.

---

## 3. The confound, and how to dissolve it honestly (the load-bearing move)

**The suspicion, stated plainly.** MTL did not help when the pair was static + sequential (CBIC).
MTL helped when the pair was sequential + sequential (MobiWac). CBIC itself blamed the static/
sequential dissimilarity. So a skeptic — a banca member is the relevant one — can argue: *the
reversal is because you made the two tasks more similar, not because you fixed the representation.*
If the frame credits the win to representation alone while quietly swapping the task pair, that reads
as a moved goalpost, and it is the kind of thing an examiner enjoys finding.

This must not be smoothed over. But it does not weaken the thesis — handled correctly, it deepens it.
There are three honest responses, and they compound.

**3.1 The strongest response: the task change is a *corollary* of the representation thesis, not an
independent knob. [NEEDS SIGN-OFF]**
The central idea of the arc is that a place has no single visit-independent identity — the same
coffee shop is a weekday lunch stop and a Saturday-night spot, and one per-place vector cannot be
right for both. Static category classification asks for one label per POI from stable,
visit-independent features, which is the least natural task to pose on top of a per-visit
representation. **[Correction, pass-2 critic — POI/mobility expert.]** An earlier draft of this file
said the static task becomes "incoherent" under a check-in representation; that overreaches. The task
does not become impossible: one can *pool* the visit vectors of a POI into a single POI vector and
classify that, which is exactly what CoUrb's own POI Encoder does (it generates the embedding per
category and remaps it to each POI). So the honest claim is weaker but still load-bearing: under a
per-visit representation the *sequential* category task (what kind of place comes next) is the natural
fit, and the static per-POI task requires an extra pooling step that discards the per-visit signal the
representation was built to carry. The coherent, natural pair under a per-visit representation is
therefore two next-visit properties — next category and its spatial companion, next region. **So the
task pair did not change independently of the
representation; it changed because the representation changed.** The task refinement is the
representation thesis applied a second time — to the definition of the problem rather than to the
encoder. Framed this way, the two-sequential-task pair is not a convenient choice that happened to
help MTL; it is the task pair the representation *forces*. This is the connective claim that turns
the confound into the arc's most intellectually satisfying beat, and it needs author sign-off before
it enters the text (it is a new framing, strongly supported by MobiWac §2.1 but not verbatim in any
source).

**3.2 The controlled evidence for representation-dominance lives in CoUrb, and is untouched by the
task switch.** CoUrb holds the task pair *fixed* (the original static + sequential pair, identical to
CBIC) and changes *only* the input representation — and category performance rises sharply. That is a
true controlled comparison: same tasks, same architecture, representation varied. So
"representation is the dominant factor" is established **on the original, dissimilar pair**, before
any task change occurs. The task switch happens later (MobiWac) and cannot retroactively explain
CoUrb's result. *This is why CoUrb is the load-bearing control of the whole dissertation*, and it is
another reason to elevate its role in the frame (pass-1 recommendation G-13). The honest logline is:
representation-dominance is proven under the hard (dissimilar) pair by CoUrb; the joint *win* is then
delivered under the pair the check-in representation naturally induces by MobiWac.

**3.3 The mechanism is measured, not assumed: the two final tasks do not conflict.** MobiWac reports
that the two tasks' training gradients are near-orthogonal on the shared trunk, so there is no
*directional* conflict for a gradient balancer to resolve — which is *why* balancers (PCGrad,
Nash-MTL) do not beat a tuned fixed weighting on this pair. **The number must travel with its source's
scope** (MobiWac `02_related.tex` L89–94): the cosine similarity "averages +0.001 across training
(four seeds each on three of our six datasets, per-dataset means within ±0.003)," it was "measured
during development on the same joint architecture (on an earlier preparation of the data)," and the
source states it is "a finding for this pair of tasks, not a general rule." Two precisions the critic
pass (MTL expert) added: (i) cosine captures *directional* conflict only — magnitude imbalance is not
measured by it, and Adam already partially normalizes that — so the honest phrasing is "no directional
conflict," not "no conflict"; (ii) near-orthogonality is evidence that negative transfer is *absent*,
but it is equally evidence against gradient-level *positive* transfer, so this supports "sharing
stopped hurting," not "the tasks teach each other." With that scope attached, this is quantitative
evidence that the two sequential tasks coexist without destructive interference, and it is a finding in its
own right (pass-1 recommendation G-10 / D-WORTH-3). It supports "sharing stops hurting" with a
measured mechanism rather than an assertion.

**3.4 What honesty still requires the frame to concede.** Even with 3.1–3.3, the dissertation does
**not** run a single controlled ablation that holds the task pair fixed while swapping to the
check-in representation *and* producing the joint win (CoUrb fixes the pair but reports category
gains, not the joint-beats-both result; MobiWac produces the joint win but on the new pair). So the
decomposition of "representation" from "task-homogeneity" in the *final win* rests on the conceptual
argument (3.1) plus the CoUrb control (3.2), not on one clean experiment. The frame should **say
this** — as a scope statement in Chapter 2 or a limitation in Chapter 6 — and can point to the
controlled ablation (check-in representation on the original static+sequential pair) as future work.
Conceding it costs nothing and removes the examiner's opening; hiding it is the only way it becomes
dangerous.

---

## 4. The endorsement, assembled (what the frame should say, in order)

A reader should meet the task choice as a *position the dissertation argues*, not a scope note. The
honest, verified sequence:

1. **Stakes (Ch.1):** a mobility-aware service acts on *what kind of place* and *which part of the
   city*; it does not need the exact venue. (§2.1 already; lift to Intro.)
2. **Convergence (Ch.1/§2.1):** category and region are two coordinates of the next visit that the
   field's next-place systems already compute internally (HMT-GRN, CatDM); the dissertation promotes
   them from means to co-equal ends (`Lim2022`, `yu2020catdm`, `zhu2022drrgnn`,
   `capanema2023poirgnn`). (§2.1 already; echo in Intro.)
3. **Not easier (§2.1/§3):** region spans hundreds to thousands of classes vs seven for the dropped
   static task; the task set got harder, and next place was never in the MTL pair. (Verified.)
4. **Standard formulation (§2.1/§2.4):** predicting over a map partition is canonical; the
   dissertation substitutes administrative units for grid cells (`luca2021mobilitysurvey`). (§2.2
   MobiWac already.)
5. **The corollary (Ch.1 arc ¶ and/or Ch.5 recap) [NEEDS SIGN-OFF]:** the task refinement follows
   from the representation thesis — a per-visit representation makes the static task incoherent, so
   the coherent pair is two next-visit properties. This is the beat that pre-empts the confound.
6. **The concession (Ch.2 scope or Ch.6 limitation):** representation and task-homogeneity are not
   separated by a single controlled ablation in the final win; CoUrb is the control that isolates
   representation on the fixed pair, and a fixed-pair ablation under the check-in representation is
   future work.

---

## 5. Verified anchors and flags

**Citable, already in the corpus, verified this session** (no new references introduced):

| Key | Supports | Where verified |
|---|---|---|
| `luca2021mobilitysurvey` | map-partition prediction is the standard mobility formulation; DL-for-mobility spans several tasks | MobiWac `02_related.tex` L45; §2.1 draft |
| `Lim2022` (HMT-GRN) | region predicted as a *means* (beam-search constraint toward place) | §2.1 draft; MobiWac bib |
| `yu2020catdm` (CatDM) | category predicted as a *means* (candidate pruning toward place) | §2.1 draft; MobiWac bib |
| `zhu2022drrgnn` | next region as an *end* target in its own right | §2.1 draft; MobiWac bib |
| `capanema2023poirgnn` | next category as an *end* target | §2.1 draft (errata-corrected key) |
| `silva2019urbancomputing`, `song2010limits`, `cho2011gowalla` | LBSN stakes + 93% predictability ceiling | §2.1 draft (song verified firsthand) |

**Sign-off flags:**
- **[NEEDS SIGN-OFF]** — §3.1 / §4-step-5: "the task refinement is a corollary of the representation
  thesis (a per-visit representation makes static category classification incoherent)." New connective
  framing. Route through AGENT_GUARDRAILS §3 (C2) + personas 07 (claim honesty) + 14 (adversarial
  advisor).
- **[NEEDS SIGN-OFF]** — §4-step-2: "category and region are two coordinates of the next visit …
  promoted from means to ends." The means→ends framing is in §2.1; the "two coordinates of one visit"
  phrasing is new connective language.
- **No [VERIFY] external flags** — the OpenAlex sweep produced no citable anchor; nothing external is
  asserted. The class-count figures (7 vs 520–8,501) must re-verify against the MobiWac source of
  truth at adaptation (N1), as with any number entering frame prose.

**Fail-closed note.** The most attractive possible move here would be to cite a survey that explicitly
canonizes "next category and next region" as the two standard coarse mobility tasks. I searched for
one and did not find a clean, openable anchor. I am therefore **not** asserting that such a consensus
exists; the argument above rests only on the verified means→ends and standard-partition claims. If
the author knows of such a survey, it can be added after opening and verifying it.

---

## `process/03_cohesion_and_threads/cohesion_and_threads.md`

# Cohesion audit and thread ledger (lens 3)

> Part of the storyline review. Extracted verbatim from the consolidated `STORY_REVIEW.md`
> (artifact of this project), unchanged except for the pass-2 note below. All result-claims trace to
> sources fixed in the project instructions; new frame claims are [NEEDS SIGN-OFF]; unverified
> external claims are [VERIFY].
>
> **Pass-2 revision.** Thread T8 ("next place not predicted") was under-graded here as a clean closed
> thread; it is re-opened as a *justification* question in `02_task_choice_endorsement/`. A new thread
> (the task pair itself evolved) is added in `08_underweighted_sides/` UW-1.
---

## C. The cohesion audit and the thread ledger (lens 3)

### C.1 Seam-by-seam audit

**The general Introduction's arc narrative — does it own the through-line?**
Cannot fully audit (undrafted), but the *plan* (NORTH_STAR §6.1, beat 4, the "honest-arc paragraph")
does own it, and owns it well: it commits to naming the negative result as a finding, the diagnosis
as the turning point, and the final model as the payoff. The risk is not the plan; it is that beat 4
is one paragraph among eight, and the through-line needs to be *the spine of the whole introduction*,
not a single paragraph inside it. The examiner-research calibration (§E.3, firsthand from the
internal excellence doc) is blunt on this: strong publication-based theses carry "linking material
between publications to contextualise and integrate each submission," and stapled compilation with no
thesis-level claim above the papers is the most-cited failure mode. Recommendation G-1 makes the arc
paragraph structural rather than one beat.

**The mandatory bridging subsections (Ch.4 recaps MTLnet, Ch.5 recaps both) — present, carrying?**
**Not written.** This is the largest single cohesion gap, and it is the documented failure mode of
the whole format ("stapled papers"). Right now the CBIC→CoUrb bridge is *native and strong* — CoUrb's
own introduction cites MTLnet by name as the baseline it improves ("MTLNet, proposed in
[silva2025mtlnet] … the question arises of whether decomposing the input …"), so the reader who
arrives at Ch.4 is carried by the paper's own words. The CoUrb→MobiWac bridge is *weaker natively*:
MobiWac §2 cites `silva2025mtlnet` ("our earlier work established this two-task setup and observed
negative transfer") but does **not** mention ST-MTLNet / the CoUrb representation finding at all — so
the "representation is the lever" pivot that MobiWac is supposed to answer is invisible in MobiWac's
own text. Without the planned recap subsection in Ch.5, a reader has no in-text bridge from CoUrb's
diagnosis to MobiWac's resolution. This is the seam most likely to show. (G-2.)

**The time-capsule prefaces (venue/status/what-later-revises) — present, keeping superseded claims
from reading as current?** **Not written.** They are essential here in a way they are not in most
coletâneas, because this arc deliberately contains superseded conclusions: CBIC's "MTL does not
help" and CoUrb's protocol are *meant* to be read as of-their-time and later revised. Without the
prefaces, a banca member reading Ch.3 cold will encounter "MTL does not deliver consistent gains" as
if it were the dissertation's position. The plan (NORTH_STAR §3 time-capsule rule, §6 prefaces) is
correct; it just has to be executed, and it is load-bearing, not decorative. (G-3.)

**The intro–conclusion loop.** Audited as a thread ledger below. The plan closes the loop (the
Conclusion beats in §6.4 map onto the Introduction beats in §6.1), but two threads the corpus opens
are currently at risk of being dropped, and one payoff risks arriving unopened.

### C.2 THREAD LEDGER (opened → closed / opened → dropped / closed → never-opened)

Threads the Introduction/Fundamentals open (per the spine + drafted §2.5) and whether the planned
Conclusion pays them off:

| # | Thread opened | Opened where | Paid off? | State |
|---|---|---|---|---|
| T1 | Does MTL help this task pair, and what does the answer depend on? | Intro §6.1 b3 (RQ); §2.5 clause set | Conclusion §6.4 "consolidated answer" | **opened → closed** (the spine's central loop; sound) |
| T2 | Is the representation the lever, not the architecture? | §2.5 clause 2; Intro arc ¶ | §6.4 representation-dominant answer | **opened → closed** (but see F1: must stay two-factor) |
| T3 | Why a place-level vector is the limit (the mechanism) | §2.2, §2.5 (once) | Not in the §6.4 beats | **opened → at risk of dropped** — mechanism never restated at the payoff (D-MISSING-4) |
| T4 | "One model instead of one per task," framed as lower cost | Intro §6.1 b1–2 | §6.4 "one forward pass, two predictions" | **opened → closed by redefinition** — cost becomes operational, not compute; redefinition currently unnarrated (F3) |
| T5 | Negative transfer as the risk MTL runs | CBIC §1; §2.3; §2.5 | §6.4 mentions region matches/wins | **opened → partially closed** — the arc shows sharing stops hurting, but never explicitly says "the negative transfer CBIC saw is gone, and here is why" (D-WORTH-1) |
| T6 | Why check-in level *specifically* (vs any richer input) | §2.2 spine, §2.5 | Implicit in Ch.5 | **opened → weakly closed** — the jump from "enrich the representation" to "go below the place" is asserted more than motivated (D-MISSING-1's twin, the pivotal jump) |
| T7 | The three CBIC hypotheses (negative transfer / representation / architecture) | CBIC conclusion | Only representation pursued | **opened → two dropped by design** — legitimate, but the frame should say the architecture door was also opened (by CoUrb holding architecture fixed, then MobiWac redesigning it) rather than leave two hypotheses hanging (D-MISSING-2) |
| T8 | Scope: next place is NOT predicted | §1.4; §2.1; MobiWac §3 | §6.2 limitation + §6.3 future work | **opened → closed** (disciplined throughout) |
| T9 | External validity beyond the US (Istanbul) | MobiWac §1, §5; §2.4 | §6.2 "single-city non-US coverage" | **opened → closed** |
| T10 | Stakes: what a mobility-aware service does with the predictions | MobiWac §1 p1, §3, §7 | §6.4 final remarks | **opened → closed in Ch.5, not yet in the frame** — the "why care" is currently strongest inside one paper (D-MISSING-3 / stakes) |

Also the reverse check — **closed → never-opened** (payoffs that arrive without a promise):

- **The region-scaling finding** (region gain grows with region count; California largest) is a real
  and interesting result delivered in MobiWac §1/§6. It is currently *not opened* by the Fundamentals
  or the planned Introduction as a question the dissertation will answer. It risks arriving in Ch.5
  as an unpromised bonus. Worth opening a thread for it in §2.4/§2.5 or the Intro (D-WORTH-2).
- **The gradient-cosine ≈ 0 mechanism test** (why balancers do not help: the two tasks' gradients are
  near-orthogonal, so there is no conflict to resolve) is a genuinely elegant sub-finding in MobiWac
  §2. It closes a thread (T5, negative transfer) that the frame barely opens. Surfacing it in §2.3
  would convert a buried result into a visible answer (D-WORTH-3).

### C.3 Does Ch.2's §2.5 hinge set up exactly the three questions Ch.3/4/5 answer?

**Yes — this is the strongest single piece of connective tissue that exists in drafted prose.** The
§2.5 hinge paragraph is well built: its three clauses map cleanly onto Ch.3 (does naive MTL help?),
Ch.4 (is the representation the lever?), Ch.5 (what does a check-in representation unlock?), and it
is disciplined about verbs (it explicitly binds "outperforms" to paired tests and does not upgrade
AZ/AL). Two refinements would make it load the arc even better, both low-cost:
(1) clause 3 currently front-loads the *result* ("outperforms … everywhere it is tested …"); it could
instead pose the *question* the way clauses 1–2 do and let Ch.5 deliver the result, keeping the hinge
a set of questions rather than a spoiler (D-WORTH-4);
(2) the mechanism sentence ("cannot tell a weekday lunch from a Saturday night out") is the best
single sentence in the drafted frame — it should be echoed in the Introduction, not spent only here
(D-MISSING-4). Net: §2.5 does its job. The gap is above it (the Introduction) and after it (the
Conclusion), not in it.

---

---

## `process/04_beats_missing_and_worth_adding/beats.md`

# Missing and worth-adding beats (lens 4)

> Part of the storyline review. Extracted verbatim from the consolidated `STORY_REVIEW.md`
> (artifact of this project), unchanged except for the pass-2 note below. All result-claims trace to
> sources fixed in the project instructions; new frame claims are [NEEDS SIGN-OFF]; unverified
> external claims are [VERIFY].

---

## D. Missing or worth-adding beats (lens 4)

Split into MISSING (the story breaks, or reads as stapled, without it) and WORTH-ADDING (enrichment).
Each names the load-bearing bridge it repairs.

### MISSING — the story is materially weaker without these

**D-MISSING-1 · The pivotal jump: "why check-in level, specifically."**
This is the single most important missing beat. The arc's logic is: CoUrb says "enrich the
representation" → MobiWac answers "go *below the place*, to the check-in." But "enrich" admits many
answers (more encoders, better graphs, sequence models, larger embeddings). Nothing in the frame yet
argues *why the specific move is downward in granularity* rather than sideways in richness. The
mechanism that justifies it exists (a place has different functions on different visits, so no
per-place vector can be right for both), but it is currently used to justify the *representation*
in the abstract, not the *specific descent to the check-in level*. Without one explicit bridging
argument — "enriching the input helped (CoUrb); but every place-level scheme, however enriched,
still assigns one vector per place; the only way past that ceiling is to represent the visit itself"
— the reader experiences Check2HGI as a rabbit from a hat. **The story breaks here** in the sense
that the arc's turn from diagnosis to resolution is the least motivated of all its joints.
*Fix:* one bridging paragraph, in the Introduction arc and/or the Ch.5 recap subsection. **[NEEDS
SIGN-OFF]** — the sentence "every place-level representation, however enriched, shares the
per-place-vector ceiling" is a new connective claim; it is strongly supported by MobiWac §2.1 but is
not verbatim in any source.

**D-MISSING-2 · Why representation before architecture (the CBIC three-door choice).**
CBIC ends with three hypotheses and points first at the *architecture* door. The dissertation walks
the *representation* door. A reader who read CBIC carefully will ask why. The honest answer is
available and good: CoUrb tested the representation door by holding the architecture fixed and saw a
large effect, which is stronger evidence for representation than anything the architecture door
produced; and MobiWac ultimately walked the architecture door too (it redesigned sharing). So the
frame can say "we tested the cheapest, most-controlled hypothesis first (change only the input), it
paid off, and the final model returned to the architecture question once the representation was
right." Without this, thread T7 leaves two named hypotheses visibly hanging. *Fix:* two or three
sentences in the Introduction arc paragraph or the Ch.4 preface. **[NEEDS SIGN-OFF]** (a new
connective claim about *why* the order of investigation).

**D-MISSING-3 · The stakes, early and concrete.**
The reader is given a concrete reason to care — but only inside MobiWac (§1 p1: caching content where
a user is heading, provisioning capacity before demand arrives; §7: the California shortlist of ten
regions out of 8,501 contains the true region 65.69% of the time). In a ~100-page document, that
stakes-setting has to happen in Chapter 1, or the reader spends the CBIC null with no felt reason to
care whether MTL works. The material exists and is already quantified and sourced; it just has to be
lifted into the frame's opening. *Fix:* fold the MobiWac §1-p1 / §3 motivation into the Introduction
context funnel. Low new-claim risk (it is reused, sourced material), but the §7 shortlist number, if
promoted to Chapter 1, must carry its convention (single-seed, four datasets) and re-verify against
the MobiWac source of truth. Mark the specific number **[VERIFY at adaptation]**.

**D-MISSING-4 · The mechanism, shown at the top, not just in Ch.5.**
Covered in A.3-4 and T3. The "same coffee shop, two visits, identical vector" mechanism is the
intellectual heart of the arc and currently lives in Chapter 5's related work plus one §2.5 sentence.
It should be shown once, concretely, in the Introduction (as the reason the journey turns) and
echoed at the Conclusion (as the thing the resolution fixed). This is placement, not new content, so
new-claim risk is low — but promoting it to the Introduction means stating it *before* Ch.5 proves
it, so it must be framed as the hypothesis the dissertation will test, not as an established fact, to
stay honest to the time-capsule rule.

### WORTH-ADDING — enrichment, the arc survives without them

**D-WORTH-1 · Name the negative-transfer reversal explicitly.**
CBIC observes negative transfer (sharing hurts one task). MobiWac shows sharing helping. The arc
implies the reversal but never says, in one sentence at the payoff, "the negative transfer the first
study saw is absent once the representation carries the visit, and here is the evidence." Closing
T5 out loud is satisfying and honest. Low cost; **[NEEDS SIGN-OFF]** as a connective claim.

**D-WORTH-2 · Open the region-scaling thread before Ch.5 delivers it.**
The "region gain grows with region count" finding (closed → never-opened, C.2) is a strong result
arriving unpromised. One clause in §2.4 or the Introduction that flags "whether the joint benefit
depends on how finely the map is partitioned" turns a bonus into an answered question.

**D-WORTH-3 · Surface the gradient-orthogonality mechanism in §2.3.**
MobiWac's finding that loss/gradient balancers do not beat a tuned fixed weighting *because the two
tasks' gradients show no directional conflict* is an honest, self-contained result. (The number and
its scope: cosine "+0.001, four seeds each on three of six datasets, measured during development on an
earlier data preparation, a finding for this pair, not a general rule" — MobiWac `02_related.tex`
L89–94; the scope must travel with the number wherever it is used, per the pass-2 MTL-expert critic.)
§2.3 currently reviews balancers (GradNorm, PCGrad, Nash-MTL, CAGrad, FAMO, Aligned-MTL) as
background. One forward-pointing sentence — "whether these balancers help this task pair is an
empirical question Chapter 5 answers" — converts a catalog into a thread. It also pre-empts the
obvious banca question "why didn't you use [balancer X]?".

**D-WORTH-4 · Make the §2.5 hinge pose clause 3 as a question, not a result.**
Covered in C.3. Keeps the hinge a set of three questions and avoids spoiling the payoff two chapters
early. Pure craft; no claim change.

**D-WORTH-5 · A one-row-per-paper "what changed / what it forced" bridge table in the Introduction.**
The excellence rubric (persona 17, dim. 2) and the compilation-thesis literature (§E.3) both prize
explicit "Chapter N showed X, which forced Y" connective tissue. A compact table — paper → what it
changed → what result → what question it forced next — in the Introduction or at the head of Ch.3
would make the arc's logic visible at a glance and directly answers the banca's "convince me this is
one dissertation, not stapled papers" (Q19). The model-lineage table already exists for the *models*;
this is its argument-level twin. Medium cost; high unity leverage.

---

---

## `process/05_craft_pacing_and_voice/craft_pacing_voice.md`

# Craft, pacing, and the one-voice seam (lens 5)

> Part of the storyline review. Extracted verbatim from the consolidated `STORY_REVIEW.md`
> (artifact of this project), unchanged except for the pass-2 note below. All result-claims trace to
> sources fixed in the project instructions; new frame claims are [NEEDS SIGN-OFF]; unverified
> external claims are [VERIFY].

---

## E. Craft, pacing, enjoyment (lens 5)

### E.1 The momentum map (where curiosity is created vs satisfied)

Reading the arc as currently constituted (paper intros/conclusions + drafted Ch.2 + spine):

- **Ch.1 (planned):** curiosity *creation* is strong in the raw material — MobiWac's opening
  (anticipate the next move, prepare ahead) is a genuine hook. Risk: if the Introduction opens on
  MTL machinery rather than on the mobility stakes, it creates curiosity about the wrong thing.
- **Ch.2 Fundamentals:** paced well for a thin chapter. §2.2 (the representation spine) and §2.5 (the
  synthesis) are the momentum peaks; §2.3/§2.4 are necessarily catalog-like but kept short. §2.5's
  hinge is the best-crafted transition in the drafted document — it visibly hands the reader to the
  papers. **This chapter does its job of building authority by the end of the literature review**,
  which the examiner research (§E.2) identifies as decisive.
- **Ch.3 CBIC:** this is the emotional *frustration* beat (the honest null), and it works because
  CBIC predicted its own null — the reader feels a hypothesis confirmed, not a failure. Momentum
  risk: without a time-capsule preface the reader may read the null as the dissertation's verdict and
  disengage ("so MTL doesn't work, why am I reading four more chapters?"). The preface is what keeps
  the frustration *productive*.
- **Ch.4 CoUrb:** the *insight* beat — the turn. This is where the reader should feel the arc pivot
  ("it was the representation all along"). The native CBIC→CoUrb bridge helps. The momentum risk is
  that CoUrb's *own* framing is modest (it presents itself as an input-engineering study on three
  states, not as the diagnostic turning point of a thesis); the frame's preface/recap has to
  *elevate* CoUrb's role, or the pivot reads flatter than it is.
- **Ch.5 MobiWac:** the *payoff*. Strongest-written of the three papers, and the "aha" lands in its
  §1 contributions and §6. Momentum risk: MobiWac is dense (six datasets, TOST, region scaling,
  shortlist analysis), and the payoff can get muffled under the machinery. The frame's job is to make
  sure the reader arrives already knowing the one question Ch.5 answers, so the density reads as
  thoroughness rather than as noise.
- **Ch.6 (planned):** the resolution restated at thesis level. If it delivers the §6.4 beats, the
  loop closes. Risk: the true "aha" (a null became a method) must be *stated as such* here, or the
  arc's emotional shape is left implicit.

**The emotional shape (setup → frustration → insight → payoff) is present and, unusually, honest** —
this dissertation has a real dramatic arc that most theses have to manufacture. The risk is not that
the shape is missing; it is that the frame chapters (which carry the shape) are undrafted, so the
shape currently lives only in the reader's ability to infer it across three separately-written
papers. **The single biggest craft win available is to let the frame narrate the emotional arc the
evidence already has.**

### E.2 Where it stalls or sags

- **§2.3 and §2.4** are the natural sag (catalog of balancers, list of metrics). They are correctly
  kept thin; the fix is not to expand them but to thread one forward-pointing sentence each (D-WORTH-3
  and D-WORTH-2) so even the catalog sections pull toward the payoff.
- **The CoUrb→MobiWac seam** is the structural sag: it is the one chapter transition with no strong
  native bridge (C.1). Reader momentum will dip crossing from Ch.4 to Ch.5 unless the recap
  subsection carries them.

### E.3 The one-voice seam verdict

Cannot be fully judged until the frame is drafted and the CoUrb translation exists, but the risk
profile is clear and specific:

- **Terminology is already well-governed** by GLOSSARY + WRITING_LAW, so the *lexical* seam (the
  usual giveaway) is defended: "next category / next region / next place," "check-in," "place
  embedding (HGI)," "the joint model" are enforced repo-wide. This is ahead of most coletâneas.
- **The three papers have visibly different registers**, and this is the real seam risk: CBIC's prose
  is the most conventional ("This dichotomy raises a critical question…"); CoUrb's is an
  input-engineering study translated from Portuguese; MobiWac's is the most disciplined and plain
  (its GLOSSARY is stricter). Read back-to-back, MobiWac will sound like a different, more careful
  author than CBIC. That is partly unavoidable (they *were* written at different times), but the
  frame chapters set the dominant voice, so if Ch.1/2/6 are written in MobiWac's register, the reader
  hears one authorial voice framing three dated artifacts — which is exactly the right effect for a
  time-capsule coletânea. **Recommendation: write the frame in MobiWac's voice** (plainest, most
  disciplined), and let the paper prefaces explicitly mark the older papers as of-their-time, so
  register drift reads as *chronology*, not as inconsistency.
- **The CoUrb translation is the sharpest single-voice risk**: a translated-from-PT chapter dropped
  among English originals is where the seam shows most. The translation-fidelity gate
  (AGENT_GUARDRAILS L5) governs claim drift; the *readability* editor (persona 15) owns the voice
  seam. This review's contribution is only to flag that CoUrb is the chapter to watch.

**Overall craft read:** where prose exists, it is good — MobiWac is genuinely well-written, §2.5 is
well-built, and the dissertation has an authentic dramatic arc that is rare and valuable. The
enjoyment risk is entirely about the *undrafted frame*: a banca member wants to keep reading a
null→diagnosis→resolution story *if the frame tells them that is what they are reading*. Right now the
story is enjoyable to someone who already knows the arc (the author) and would read as three good but
separate papers to someone who does not (a cold banca member) until the frame is written.

---

---

## `process/06_honesty_under_pressure/honesty_flags.md`

# Honesty under narrative pressure (lens 6)

> Part of the storyline review. Extracted verbatim from the consolidated `STORY_REVIEW.md`
> (artifact of this project), unchanged except for the pass-2 note below. All result-claims trace to
> sources fixed in the project instructions; new frame claims are [NEEDS SIGN-OFF]; unverified
> external claims are [VERIFY].
>
> **Pass-2 addition.** A ninth honesty flag belongs here: the research-question answer rests on two
> different task pairs (`08_underweighted_sides/` UW-4), and the frame must not present it as "same
> experiment, opposite result." See file 02 §3 for the honest resolution.
---

## F. Honesty under narrative pressure (lens 6)

Every place where a cleaner or more dramatic story would tempt a violation. For each: the temptation,
the truth, and the ruling. **Truth wins in all of them; where a stronger story needs a stronger
claim, I stop.**

**F1 · The one-factor logline (the biggest temptation in the whole arc).**
*Temptation:* "The representation is the bottleneck" is a cleaner, more quotable thesis than "the
representation is the dominant factor, and converting that into a joint win also required redesigning
how the tasks share." The one-factor version is what a punchy Introduction and a punchy Conclusion
both want.
*Truth:* CoUrb isolates the representation effect cleanly (input-only change). But MobiWac's *win* —
the payoff clause — changed both the representation and the sharing topology, and MobiWac's own text
says so (§2.1: sharing "helps instead of hurting" *on the new representation*; §4.2: the private
spatial path is what keeps region competitive). Crediting the joint win to representation alone
**contradicts Chapter 5's own text**.
*Ruling:* the frame may say "the representation is the dominant factor" as the *diagnosis* (CoUrb
earns it), but the *resolution* must be stated as two-factor. Keep the spine's own phrasing ("a
check-in-level representation **and** the right sharing topology"). Do not let the logline drop the
second factor. This is honesty *and* internal consistency — they point the same way.

**F2 · CBIC's null read as current.**
*Temptation:* the arc is more dramatic if "MTL does not help" lands hard in Ch.3. *Truth:* it is a
conclusion "of the time, for that configuration" (place-level embedding, hard sharing), later shown
configuration-specific. *Ruling:* the time-capsule preface is mandatory (WRITING_LAW §3; NORTH_STAR
§3). The drama is legitimate *only* if the preface time-indexes it. Never let a superseded claim read
as the project's position. (Also: CBIC's Nash-MTL "consistently better" predates the solver-bug
discovery — do not amplify it in the frame; NORTH_STAR §4.)

**F3 · The "lower cost" promise vs the larger joint model.**
*Temptation:* MTL's textbook selling point is efficiency; the Introduction wants to promise "one
model, lower cost." *Truth:* CBIC's joint model cost *more* (time, MFLOPs); MobiWac's joint model is
*larger than the two dedicated models combined* (~4.2M vs 1.1M params at Alabama). The honest benefit
is operational (one artifact, one forward pass), which MobiWac §4 states carefully.
*Ruling:* the frame must **not** promise compute savings. If the Introduction raises cost as
motivation, the Conclusion must close it as "operational simplicity, at higher compute," not as
"cheaper." This is thread T4; narrate the redefinition, do not hide it. A banca member will compute
the parameter ratio.

**F4 · CBIC's task-dissimilarity diagnosis vs the arc's representation diagnosis.**
*Temptation:* to make CBIC's null point cleanly at the representation (so CoUrb is its direct answer),
one could soft-pedal CBIC's own stated diagnosis. *Truth:* CBIC attributes the null substantially to
*task dissimilarity* (static vs sequential) and lists representation as one of three hypotheses. The
arc's final position is representation-richness. *Ruling:* do not retrofit CBIC's conclusion. The
honest bridge is "CBIC named three candidate causes; this dissertation tested the representation one
first (CoUrb) and it paid off" — which is true and is also a better story (it shows the research
reasoning). Reframing CBIC's emphasis after the fact would be a silent correction (AGENT_GUARDRAILS
§7); if any CBIC conclusion sentence is adjusted in the re-typeset chapter, it goes in the Appendix B
errata list, not silently.

**F5 · CoUrb's win-count and gain numbers.**
*Temptation:* use the published CoUrb numbers ("16/21", "+20–24 pp") because they are slightly larger
/ rounder. *Truth:* the internal audit recounted **15/21 strict wins + 1 technical tie** and
**+20.2…+22.0 pp**; the deck was corrected, the .tex was not. *Ruling:* the chapter uses the audited
numbers (NORTH_STAR §4; N1). This is a number-integrity flag, not strictly narrative, but it becomes
a narrative flag the moment the frame *summarizes* CoUrb's result — the summary must use the audited
figures. Any CoUrb number promoted into Ch.1/2/6 is **[VERIFY at adaptation]** against
`slides/judge_feedback.md`.

**F6 · The region verbs (the standing MobiWac law).**
*Temptation:* "one model beats both dedicated models" is cleaner than "beats on category everywhere,
beats on region at four of six, matches at the other two." *Truth:* region at AL/AZ is
non-inferiority (TOST, ±2 pp), and AZ is 0.00 — never upgraded. *Ruling:* the whitelist governs
(WRITING_LAW §3; PAPER_PLAN §3). The frame's summary sentence must carry the four-of-six split and
the "matches" verb for AL/AZ. §2.5 already does this correctly — the risk is only that a punchy
Conclusion sentence drops the qualifier. Never "outperforms region everywhere," never "beats,"
never upgrade AZ.

**F7 · The stakes numbers, if promoted to the frame.**
*Temptation:* the "ten regions contain the true region 65.69% of the time, 500× better than random"
line is a fantastic hook for Chapter 1. *Truth:* it is a single-seed, four-dataset motivation sketch
(MobiWac §7), explicitly "motivation, not a measured service result." *Ruling:* it may be used as
motivation, but if promoted to the Introduction it must carry its convention (single seed, the
specific datasets) and the "not a measured service result" hedge, exactly as §7 does. Do not let it
harden into a headline capability. **[VERIFY at adaptation]** + convention required.

**F8 · Fake cohesion from templated bridges.**
*Temptation:* the fastest way to make three papers "read as one" is to bolt identical transition
sentences between chapters ("Building on the previous chapter, we now…"). *Truth:* that is the
documented fake-cohesion failure mode (AGENT_GUARDRAILS §7; WRITING_LAW §4.4). *Ruling:* the recap
subsections and prefaces must carry *real* content (what the prior chapter established, what it
forced), not template scaffolding. Cohesion comes from the argument, not from transition words. Vary
the bridge shapes; the excellence rubric penalizes discourse-skeleton reuse across a 100-page
document.

**No honesty violation is present in the drafted prose** (§2.5 is clean, disciplined, and correctly
hedged). All eight flags are *forward risks* the frame drafting will run into. The arc does not need a
single upgraded claim to be compelling — its honesty *is* its drama.

---

---

## `process/07_recommendations_and_protect/recommendations_and_protect.md`

# Ranked recommendations, protect list, closing (lens 7 + I)

> Part of the storyline review. Extracted verbatim from the consolidated `STORY_REVIEW.md`
> (artifact of this project), unchanged except for the pass-2 note below. All result-claims trace to
> sources fixed in the project instructions; new frame claims are [NEEDS SIGN-OFF]; unverified
> external claims are [VERIFY].
>
> **Pass-2 revision.** Recommendation G-13 (leaning on "CoUrb's weaker protocol" as an arc strength)
> is **suspended**: that protocol difference is unverified (`08_underweighted_sides/` UW-3, [VERIFY]).
> Two new high-value moves are added in files 02 and 08: endorse the task choice as a corollary of the
> representation thesis, and state CoUrb's question precisely (representation, not MTL-vs-STL).
---

## G. Ranked recommendations (lens 7)

Ranked by narrative leverage per hour. In a coletânea the frame chapters (1, 2, 6) dominate leverage,
and the ranking reflects that: the top six all live in the frame. "Cost" is drafting effort. **[NEEDS
SIGN-OFF]** = a new connective/frame claim requiring author approval (AGENT_GUARDRAILS C2) before it
enters the text; route those through personas 07 + 14. **[VERIFY]** = a number to re-check against
its source of truth at adaptation.

| # | Move | Type | Where (file / beat) | Why it strengthens the story | Cost | Flag |
|---|---|---|---|---|---|---|
| 1 | Make the honest arc the **structural spine** of the Introduction, not one paragraph among eight — open on stakes, state the RQ, then narrate null→diagnosis→resolution as the through-line | REFRAME | Ch.1 (NORTH_STAR §6.1 b1–4) | Fixes the top failure mode (stapled papers); the intro is where a coletânea's unity is won (§E.2, persona 17 dim.2) | subsection | [NEEDS SIGN-OFF] (arc sentences) |
| 2 | Write the **Ch.5 recap subsection** bridging CoUrb→MobiWac ("The MTLnet framework and the representation finding") — the one seam with no native bridge | ADD | Ch.5 related-work head (Viegas device) | Welds the weakest structural seam (C.1, E.2); without it the pivot→payoff jump is invisible in Ch.5's own text | subsection | [NEEDS SIGN-OFF] |
| 3 | Write the **three time-capsule prefaces** (venue/status/what-later-revises), one italic paragraph each | ADD | head of Ch.3, Ch.4, Ch.5 | Keeps CBIC's null and CoUrb's protocol from reading as current (F2); makes superseded conclusions read as chronology, not contradiction | paragraph ×3 | — (status wording only) |
| 4 | Add the **"why check-in level specifically" bridging paragraph** (enrich → but every place-level scheme shares the per-place-vector ceiling → represent the visit) | ADD | Ch.1 arc ¶ and/or Ch.5 recap | Motivates the pivotal jump — the least-motivated joint in the arc (D-MISSING-1) | paragraph | [NEEDS SIGN-OFF] |
| 5 | State the **resolution as two-factor** (representation + sharing topology) everywhere the payoff is summarized | REFRAME | Ch.1 arc ¶, Ch.6 §6.4, logline | Prevents the one-factor flattening that would contradict Ch.5 (F1) — honesty and consistency aligned | sentences | — (enforces existing whitelist) |
| 6 | **Show the mechanism at the top** (same place, two visits, one vector) as the hypothesis the arc will test; echo it at the Conclusion as what the resolution fixed | ADD/MOVE | Ch.1 arc ¶; Ch.6 §6.4; echo of §2.5 line | Promotes the intellectual heart of the arc from Ch.5 related-work to the frame (D-MISSING-4, T3) | paragraph | low risk (frame as hypothesis, not fact) |
| 7 | Add a compact **"what each paper changed / what it forced" bridge table** in the Introduction | ADD | Ch.1 (argument twin of the model-lineage table) | Makes the arc's logic visible at a glance; directly answers banca Q19 "convince me this is one dissertation" (D-WORTH-5) | table + para | [NEEDS SIGN-OFF] (connective claims) |
| 8 | Add the **"why representation before architecture"** reasoning (CBIC's three doors; cheapest/most-controlled first) | ADD | Ch.1 arc ¶ or Ch.4 preface | Closes thread T7; shows research reasoning instead of leaving two hypotheses hanging (D-MISSING-2) | 2–3 sentences | [NEEDS SIGN-OFF] |
| 9 | Lift the **stakes** (mobility-aware service, the shortlist number) into the Introduction context funnel | MOVE | Ch.1 §6.1 b1 (from MobiWac §1/§3/§7) | Gives the reader a felt reason to care through the CBIC null (D-MISSING-3, T10) | paragraph | [VERIFY] number + convention |
| 10 | Thread **one forward-pointing sentence** into §2.3 (balancers → Ch.5 answers) and §2.4 (region scaling → Ch.5 answers) | ADD | Ch.2 §2.3, §2.4 | Converts the two catalog/sag sections into threads; pre-empts "why not balancer X?" (D-WORTH-2/3) | 1 sentence ×2 | low risk |
| 11 | **Name the negative-transfer reversal** out loud at the payoff | ADD | Ch.6 §6.4 | Closes T5 explicitly; satisfying and honest (D-WORTH-1) | sentence | [NEEDS SIGN-OFF] |
| 12 | Rephrase **§2.5 hinge clause 3 as a question**, not a result | REFRAME | Ch.2 §2.5 last ¶ | Keeps the hinge three questions; avoids spoiling the payoff two chapters early (D-WORTH-4, C.3) | sentence | — |
| 13 | Elevate **CoUrb's role** in its preface/recap (the controlled pivot, second-authored, weaker protocol — all stated) | REFRAME | Ch.4 preface + Ch.4 recap in Ch.5 | Prevents the arc's most under-owned clause from reading flat; turns the protocol caveat into an arc strength (B.2, F5) | paragraph | [VERIFY] CoUrb numbers |
| 14 | Write the frame in **MobiWac's register**; mark older papers as of-their-time | REFRAME | Ch.1/2/6 voice | Makes register drift read as chronology, not inconsistency (E.3 one-voice seam) | style choice | — (persona 15 owns) |

**Leverage note:** moves 1–3 are the unity backbone — if only three things are done, do these. Moves
4–6 are the intellectual-honesty backbone (they make the arc land *correctly*). Moves 7–14 are
enrichment and craft. The model-lineage table already exists and is good; move 7 is its argument-level
complement.

---

## H. PROTECT LIST — what already works; do not dilute

1. **The honest arc itself.** Null → diagnosis → resolution is a real, rare dramatic structure. Do not
   sand it into a conventional "we propose X and it works" story to look tidier. The null is the
   foundation, not an embarrassment (WRITING_LAW §3; persona 17 dim.7 calls it the dissertation's
   natural superpower).
2. **CBIC as a predicted null.** CBIC's introduction *hypothesizes* the limitation before reporting
   it. This is what makes the null land as a finding. Preserve that framing when re-typesetting; do
   not rewrite CBIC's intro to sound surprised by its own result.
3. **The §2.5 Relevance hinge.** The best-built connective prose in the drafted document. Its
   three-clause structure and its verb discipline (bound to tests, AZ not upgraded) are exactly right.
   Refine clause 3 (move 12) but do not restructure it.
4. **The native CBIC→CoUrb bridge.** CoUrb's own introduction cites MTLnet by name as the baseline it
   improves. This is free, real cohesion — keep it visible; the recap subsection should *complement*
   it, not replace it.
5. **The claim discipline in MobiWac and §2.5.** The four-of-six / matches-at-two / never-upgrade-AZ
   wording, the operational-not-arithmetic cost framing, the "motivation not a measured service"
   hedges. This is the honesty that makes the arc defensible. Every recommendation above is
   constrained to preserve it.
6. **The scope discipline** (next place is not predicted, stated once early and held). Do not blur the
   three tasks for a cleaner sentence.
7. **The model-lineage table.** DGI → HGI → MTLnet → ST-MTLNet → Check2HGI → joint model, with verbs
   disciplined. Keep it; move 7 adds an argument-level twin, it does not replace this.
8. **The mechanism sentence** ("cannot tell a weekday lunch from a Saturday night out", §2.5). The
   single most vivid line in the drafted frame. Reuse it in the Introduction (move 6) — do not
   rewrite it into something blander.

---

## I. Closing — the three questions, answered directly

**Is it cohesive?** The *argument* is cohesive — genuinely one investigation, not three topics: a
single research question, a settled chronological-is-intellectual order, one native inter-paper bridge
already in the text, and a Fundamentals chapter whose §2.5 hinge sets up exactly the three questions
the papers answer. But the *document* is not yet cohesive, because the connective tissue that carries
the cohesion — the Introduction's arc narrative, the two recap subsections, the three time-capsule
prefaces — is planned and unwritten. Cohesion here is a drafting task, not a rethinking task: the
plan welds; it just has not been welded yet. The one place the plan itself risks incoherence is the
logline's temptation to credit the payoff to representation alone, which would contradict Chapter 5's
own two-factor account — keep the resolution two-factor and the argument stays sound.

**Is it enjoyable?** For a reader who already knows the arc, yes — it has an authentic
setup→frustration→insight→payoff shape most theses have to fake, and where prose exists (MobiWac,
§2.5) it is good. For a cold banca member, not yet, because the frame that would tell them "you are
reading a null-that-became-a-method" is the undrafted part; today they would meet three well-written
but separately-voiced papers and have to infer the drama themselves. The enjoyment is latent in the
evidence and will be released the moment the frame narrates it.

**Is it well-crafted?** The drafted prose is well-crafted and disciplined; the governance
(GLOSSARY, WRITING_LAW, the claim whitelist) is unusually strong and already defends the lexical seam
that usually betrays a compilation thesis. The craft risk is entirely in the unwritten frame and in
one translated chapter (CoUrb), both known and gated.

**The single highest-leverage narrative move:** write the Introduction so the honest arc is its
structural spine (recommendation 1) — open on the mobility stakes, pose the research question, then
narrate null → diagnosis → resolution as the through-line, stating the resolution as two-factor
(a representation built for visits, *and* a sharing topology that lets the tasks help each other) and
showing the mechanism (same place, different visit, same vector) as the hypothesis the journey tests.
Everything else in this review is in service of that one move: the recaps and prefaces protect it, the
bridge table makes it visible, and the honesty flags keep it true. The arc is already there in the
evidence; the Introduction is where the reader is told what they are about to read.

---

### Source ledger (what each result-claim in this review traces to)

All result-claims trace to sources fixed in the project instructions; no number is computed here, and
any number promoted into chapter prose must re-verify at adaptation (N1). Key traces:

- CBIC null, three hypotheses, task-dissimilarity emphasis, cost-more, Nash-MTL caveat →
  `../../../../../../CBIC___MTL/sections/intro.tex`, `conclusion.tex`; NORTH_STAR §2, §4.
- CoUrb input-only change, category gain, 16/21 vs audited 15+1 & +20.2–22.0 pp, sample-stratified
  split, second authorship → `../../../../../../CoUrb_2026/src_en/sections/intro.tex`, `conclusion.tex`;
  NORTH_STAR §2, §4; audited numbers per `slides/judge_feedback.md` (not re-opened here — **[VERIFY at
  adaptation]**).
- MobiWac two-factor method (Check2HGI + cross-attention + private spatial path), region 4/6 + TOST
  ±2pp, AZ 0.00 never upgraded, gradient cosine ≈ +0.001, larger-than-combined params (4.2M vs 1.1M),
  shortlist 65.69% single-seed motivation, no ST-MTLNet mention in §2 →
  `articles/[mobiwac]/src/sections/01_introduction.tex`, `02_related.tex`, `03_problem.tex`,
  `04_method.tex`, `07_discussion.tex`, `08_conclusion.tex`.
- §2.5 hinge, mechanism sentence, model-lineage table, draft state →
  `../../../../fundamentals/2.5_relevance/2.5_relevance.tex`, `model_lineage_table.md`,
  `fundamentals.tex`; intended spine → `NORTH_STAR.md` §1–§3, §6.
- Honesty bounds → `WRITING_LAW.md` §3, §5; `AGENT_GUARDRAILS.md` §1–§3, §7; `GLOSSARY.md`.
- Excellence/coletânea calibration → `reviewers/research/dissertation_excellence_2026-07-20.md` (opened
  this session, firsthand) + `exemples/viegas/VIEGAS_ANALYSIS.md`; external searches below.

### External calibration note (§E references) — provenance corrected

**Provenance honesty (fail-closed).** Two web searches were run this session
("framing a negative result as a contribution"; "compilation-thesis coherence / stapled-thesis").
Both returned **titles and URLs only; no page body was retrieved and no page was opened**. They
therefore provide **no firsthand external grounding**, and I do not cite them as support. Every
load-bearing external claim in §E below is re-anchored on the **internal excellence doc**
(`reviewers/research/dissertation_excellence_2026-07-20.md`), which *was* opened firsthand this session and
already contains the relevant examiner-research findings with their identifiers. Convention claims
that appear in neither the internal doc nor an opened page are marked **[VERIFY]** (general domain
knowledge, to confirm against a source before any of it enters chapter prose).

- **E.3 (compilation-thesis unity) — firsthand-grounded, internal doc.** The internal excellence doc
  records (firsthand from the examiner-research literature): stapled compilation is "the most cited
  PBT failure mode" (ANTI_PATTERNS #1: "papers bound without linking material … no thesis-level claim
  above the papers"); and strong publication-based theses have "a substantial introduction with
  literature review, **linking material between publications to contextualise and integrate each
  submission**, and a concluding synthesis" (Sharmini & Kumar 2018). This is what ranks the recap
  subsections and the arc-spine Introduction at the top (moves 1–2); it needs no web source. The
  university-guideline phrasings I drew from the search titles ("narrative overview"; Toronto/ANU
  compilation guidelines) are **[VERIFY]** — I did not open those pages.
- **E.4 (negative result as contribution) — firsthand-grounded, internal doc.** The internal doc
  records (firsthand): Lovitts — otherwise-good dissertations remain acceptable "when experiment(s) do
  not work out and students get null or negative results," and what distinguishes outstanding is *what
  the author does with them*; Mullins & Kiley — examiners prize "how they recognise and deal with
  contradictions" and "critical assessment of their own work"; and the ML-specific form (CS_SIGNALS):
  "a falsified hypothesis with a diagnosed mechanism … is excellence evidence; an unexplained dip is
  not." This fully supports protecting CBIC's predicted-null framing (protect-list 2) and
  time-indexing rather than apologizing for it (move 3) — CBIC predicts its null, CoUrb diagnoses,
  MobiWac resolves. The narrower writing-craft convention "prime the reader in the introduction / frame
  the null as challenging an expectation" is **[VERIFY]** (general knowledge; not in the internal doc
  verbatim and not opened this session) — the recommendation stands without it on the Lovitts/M&K
  grounding above.

---

## `process/08_underweighted_sides/underweighted_sides.md`

# Second-pass audit: sides of the story that need more attention

> **Why this file exists.** The author's task-change concern exposed a systematic error in the first
> review: I graded the *discipline* of a scope choice (was it stated cleanly, held consistently?)
> instead of whether the choice was *justified* and whether it hid a confound. This file re-runs the
> arc with that corrected lens and reports every side I under-weighted, each with its firsthand
> verification status. Two of these are corrections to my own pass-1 claims. New connective framings
> are **[NEEDS SIGN-OFF]**; unverified claims are **[VERIFY]**.

---

## The error type, named

Pass 1 filed "next place is not predicted" as *thread T8 — opened → closed, disciplined throughout*.
The discipline was real, but the *justification* was thin and the *task-pair evolution* underneath it
was invisible. Grading discipline over justification is the mistake; below is every place it recurs.

---

## UW-1 · The task pair evolved, and the arc credits only two of three changes (MAJOR)

Fully developed in `02_task_choice_endorsement/`. In brief: the CBIC→MobiWac reversal changed the
representation, the sharing topology, **and** the task pair (static+sequential → sequential+
sequential), and CBIC itself blamed the static/sequential dissimilarity for the null. The frame
currently narrates two of the three changes. **Verified firsthand** (CBIC `intro.tex` L38–44,
`method.tex` L36–54; CoUrb `intro.tex` L4–5; MobiWac `03_problem.tex`). The honest resolution
(the task refinement is a *corollary* of the representation thesis, plus CoUrb as the fixed-pair
control) is in file 02. **This is the side most needing attention**, and it is the one the author
sensed.

## UW-2 · CoUrb never tests "does MTL help" — it only tests "does the representation help" (MAJOR)

**Verified firsthand** (CoUrb `metodology.tex` L36–38, `results.tex`, `conclusion.tex` L3): CoUrb's
*only* baseline is MTLNet. Every CoUrb comparison is ST-MTLNet (decomposed-representation MTL) vs
MTLNet (place-embedding MTL) — **both multi-task**. CoUrb runs no single-task model.

Consequence for the arc: the central research question ("does MTL help this task pair?") is answered
by CBIC (no, for that configuration) and by MobiWac (yes, for the check-in configuration). **CoUrb is
silent on it.** CoUrb answers a *different*, subordinate question ("is the representation the lever?")
and answers it cleanly. This is actually a *strength* for honesty — CoUrb is the controlled
representation experiment (architecture fixed, single-task question held constant, only the input
varied) — but it creates a specific frame risk: a reader carried by momentum may conclude "CoUrb
showed MTL works," which CoUrb did not show. The Ch.4 preface/recap must state CoUrb's question
precisely: *it isolates the representation effect; it does not revisit the MTL-vs-single-task
verdict.* **[NEEDS SIGN-OFF]** on the framing sentence that draws this boundary.

This also sharpens the logline (pass-1 lens B): the three clauses are "MTL does not beat single-task
on a place embedding" (CBIC) → "the representation, not the architecture, is why" (CoUrb, on the
representation axis only) → "with a check-in representation and redesigned sharing, MTL finally beats
single-task" (MobiWac). CoUrb's clause is about the *diagnosis*, not about MTL beating anything.

## UW-3 · CORRECTION to pass 1 — **RESOLVED 2026-07-23, verified firsthand**

> **Resolution.** The author provided the CoUrb codebase (`/Users/vitor/Desktop/mestrado/temp/
> tarik-new`). Verified firsthand: `PoiMtlNet_Novo/src/etl/mtl/create_fold.py` L190–199 reads
> `userid` and then **drops the column**; folds are built with plain
> `StratifiedKFold(n_splits, shuffle=True)` on sample rows stratified by class (L225–228), and
> `src/etl/next/fold.py` L19+L34 does the same; a repo-wide grep finds **no group-aware splitter**
> in project code. A user's windows can therefore span train and test. **The original claim was
> correct: CoUrb's protocol is sample-stratified, weaker than Ch.5's user-disjoint split.** The
> protocol beat is restored in NORTH_STAR §4/§6 and GLOSSARY with this file/line evidence. The
> retraction below is kept for the record of the fail-closed process.

### The original retraction (historical record)

Pass 1 asserted, in lens B and recommendation G-13, that CoUrb's protocol is "sample-stratified, not
user-disjoint (weaker than MobiWac)." **I cannot verify this firsthand.** CoUrb's `results.tex`
reports only "mean and standard deviation over 5 folds"; it does not state whether folds are
user-disjoint or sample-stratified. The dissertation's `../../../../../../../docs/context/DATA_SPLITS.md` documents a
`StratifiedGroupKFold` user-disjoint protocol but does **not** attribute protocols per paper, and
MobiWac (`05_setup.tex` L28) is explicitly "split by user with stratified five-fold cross-validation."

So the protocol *difference* between CoUrb and MobiWac is **[VERIFY]**, not established. Two honest
paths: (a) the author confirms CoUrb's actual split from the CoUrb codebase / `slides/judge_feedback`
and the frame states it; or (b) the frame does not assert a protocol difference. Any recommendation
that leaned on "CoUrb's weaker protocol as an arc strength" (pass-1 G-13) is **suspended** until this
is verified — do not build a narrative beat on an unverified protocol gap. This correction is itself
an example of UW-0 (I graded my own summary's fluency instead of re-verifying the source).

## UW-4 · "Does MTL help?" is answered on two different task pairs — the comparison is not like-for-like (MODERATE)

Following from UW-1 and UW-2: CBIC's "no" is on {category classification, next category}; MobiWac's
"yes" is on {next category, next region}. The dissertation's headline answer to its own research
question therefore rests on a *no* and a *yes* measured on **different task pairs**. This is defensible
(the pair changed for a principled reason — file 02 §3.1), but the frame must not present it as "the
same experiment, opposite result." The honest statement is "naive MTL did not help the original pair;
a check-in representation with redesigned sharing helps the pair that representation induces." **[NEEDS
SIGN-OFF]** on the exact wording of the arc's answer, because it is the single sentence a banca will
quote back.

## UW-5 · The negative-transfer thread is opened, measured, and never explicitly closed (MODERATE)

Pass 1 flagged this (T5 / D-WORTH-1), but under-weighted how much verified evidence exists to close
it. MobiWac measures the shared-trunk gradients as near-orthogonal — a direct answer to CBIC's
negative-transfer worry. **The number carries scope that must travel with it** (MobiWac
`02_related.tex` L89–94): cosine "+0.001 across training, four seeds each on three of our six
datasets, per-dataset means within ±0.003," "measured during development … on an earlier preparation
of the data," and "a finding for this pair of tasks, not a general rule." Two precisions from the
pass-2 critic (MTL expert): cosine measures *directional* conflict only (so say "no directional
conflict"), and near-orthogonality is evidence negative transfer is *absent* but also evidence against
gradient-level *positive* transfer — so it supports "sharing stopped hurting," not "the tasks teach
each other." Closing this explicitly ("the negative transfer CBIC feared is absent once the
representation carries the visit; on the datasets measured, the tasks' gradients are near-orthogonal")
is high-value and grounded, with the scope attached. **Verified firsthand** (MobiWac `02_related.tex`).
The connective sentence is **[NEEDS SIGN-OFF]**.

## UW-6 · The cascade-vs-parallel choice is a defended strength the frame under-sells (MINOR)

The field predicts category/region as *steps toward* a place (the cascade: Ye2013 → CatDM → CSLSL).
MobiWac drops the cascade and predicts the two as co-equal ends, and — verified — **tests that choice
directly** ("since the cascade is the pattern the field uses, we test the choice directly",
`02_related.tex` L80). This is a genuine methodological contribution (it does not just assert the
parallel framing, it validates it), and the arc currently treats it as a design note. Worth a clause
in the Introduction or §2.1. **Verified firsthand.** Low new-claim risk (it restates what the paper
does).

## UW-7 · Istanbul is generalization evidence, not just a second dataset (MINOR)

Pass 1 filed Istanbul as T9 (external validity, closed). Under-weighted: Istanbul is the *only*
non-US, non-Gowalla dataset in the whole arc (CBIC and CoUrb are Gowalla-only US states). It is the
arc's one piece of evidence that the result is not a Gowalla artifact. The frame should let it carry
that weight — "the joint result holds on a different continent, a different data source, and a
different administrative unit (mahalle)" — rather than listing it as dataset six. **Verified**
(MobiWac datasets; NORTH_STAR). Low risk.

---

## Ranked: how much more attention each side needs

| # | Side | Severity | Verified? | Needs |
|---|---|---|---|---|
| UW-1 | task pair evolved; only 2 of 3 changes credited | **major** | firsthand ✓ | the corollary framing (file 02 §3.1) [SIGN-OFF] |
| UW-2 | CoUrb tests representation, not MTL-vs-STL | **major** | firsthand ✓ | precise Ch.4 preface boundary [SIGN-OFF] |
| UW-4 | RQ answered on two different pairs | moderate | firsthand ✓ | exact wording of the arc's answer [SIGN-OFF] |
| UW-5 | negative-transfer opened, measured, not closed | moderate | firsthand ✓ | one closing sentence [SIGN-OFF] |
| UW-3 | pass-1 "CoUrb weaker protocol" unverified | correction | **NOT verified** | author verifies split, or drop the beat [VERIFY] |
| UW-6 | cascade-vs-parallel is a tested choice | minor | firsthand ✓ | one clause; low risk |
| UW-7 | Istanbul = generalization evidence | minor | firsthand ✓ | reframe; low risk |

**The through-line of this audit:** the arc's honesty is not at risk from any single fact — every
fact is defensible — but from *how many things changed at once between the null and the win*.
Representation, sharing, and task pair all moved. The dissertation's credibility depends on the frame
saying so plainly and showing that the task change follows *from* the representation thesis rather
than sitting beside it as an unacknowledged second cause. That is the highest-value honesty move in
the whole storyline, and it is also, handled well, the most intellectually satisfying beat available.

---

## `process/09_application_scope_breadth/application_scope_breadth.md`

# Application-scope breadth: are we using examples beyond mobility?

> **Why this file exists.** In `noth_star_consideration.md` point 3, the author asks: the
> Introduction's problem statement should motivate next category and next region with **application
> examples beyond mobility**. CBIC and CoUrb cite broader domains; MobiWac stayed mobility-only
> because it was a mobility conference, but the dissertation can broaden the scope. This file answers
> "are we doing this?" and gives the verified material to do it, fail-closed.

---

## 1. Direct answer: no, not yet — the drafts are mobility-framed only

Checked the drafted Fundamentals prose (`2.1_poi_prediction_tasks.tex`, `2.5_relevance.tex`) and the
storyline. Both frame the stakes **exclusively** through mobility and mobility-aware services. The
only application words that appear are "recommenders" in passing (`2.1` L65, describing CatDM). There
is **no** mention of the broader domains the author has in mind. So the author's instinct is correct:
the dissertation is currently inheriting MobiWac's deliberately narrow, venue-driven framing, and has
not yet exercised the wider scope that the coletânea frame permits.

This matters for the arc because MobiWac's stakes paragraph is the single strongest "why care" in the
corpus, and pass-1 recommended lifting it into Chapter 1 (G-9). If that lift copies MobiWac's
mobility-only framing verbatim, the dissertation misses the chance the author is pointing at: a
dissertation Introduction can motivate the two tasks across the *full* range of applications the
component papers already gestured at, then narrow to mobility as the setting where they are
evaluated.

## 2. What CBIC and CoUrb actually cite — the verified raw material

All keys below were confirmed to resolve in the component papers' `.bib` files this session. This is
the material the Introduction can draw on without any new citation.

**From CBIC** (`sections/intro.tex` L5, currently **commented out** in the source; `sections/basis.tex`
L25, uncommented):

| Domain | How CBIC frames it | Cite key (resolves in `CBIC___MTL/references.bib`) |
|---|---|---|
| Computer vision | MTL for joint object detection and segmentation | `kokkinos2016ubernet` |
| Natural language processing | MTL for joint POS tagging + named-entity recognition | `wei2022finetuned` |
| Healthcare | MTL for simultaneous diagnosis of multiple conditions | `lipton2015learning` |
| Recommendation systems | MTL modeling user preferences + item attributes together | `zhang2020interactive` |
| Urban planning | POI prediction/classification as an urban-planning challenge | `Xu2023` (also names recommendation) |

> Note: the four-domain sentence lives in a **commented block** in CBIC's `intro.tex`. It is real,
> cited material the author wrote, but it is not in the compiled CBIC paper. For the dissertation
> Introduction it can be revived and re-verified; treat each of the four as **[VERIFY at adaptation]**
> — open the cited work and confirm it supports the one clause attributed to it (AGENT_GUARDRAILS R3),
> because a commented-out line never passed a citation gate.

**From CoUrb** (`sections/related.tex` L1, L19):

- POI prediction/classification framed as challenges in **location-based recommendation** *and*
  **urban mobility analysis** (L1).
- The spatial encoders the paper adopts (SIREN, Sphere2Vec-M) originate in **species prediction and
  population estimation** (ecology / remote sensing), cited via `wu2024torchspatial` and
  `mai2023sphere2vec` (L19). This is a genuine cross-domain provenance: the geospatial machinery came
  from ecology before it reached POIs.

## 3. How to use it, honestly (the frame move)

**The shape:** open the Introduction on the two tasks as *general* prediction problems whose value is
not limited to LBSN navigation, name two or three concrete non-mobility uses with their citations,
then narrow to the mobility setting where the dissertation evaluates them. This widens the felt
stakes (pass-1 D-MISSING-3) without diluting the honest scope statement that the *experiments* are on
mobility check-in data.

**Concrete, grounded uses the two tasks map onto** (each traceable to a cited domain above; phrase as
illustration, not as measured capability):

- **Next category** -> *recommendation and content preparation* (what kind of place / item the user
  turns to next -- `zhang2020interactive`, `Xu2023`); *demand and staffing* by activity type.
- **Next region** -> *urban planning and resource placement* (which part of the city to provision --
  `Xu2023`, `Lim2022`); the map-partition target is the standard mobility formulation
  (`luca2021mobilitysurvey`).
- **The method's transferability** -> the geospatial encoders came from *ecology / remote sensing*
  (`wu2024torchspatial`), so the representation ideas are not mobility-specific; this is an honest
  breadth note, not a claim that the dissertation tested those domains.

**Honesty guardrails on this move (fail-closed):**
1. **Illustration, not evaluation.** The dissertation evaluates on mobility data only. Non-mobility
   uses are *motivating examples*; never phrase them as things the dissertation demonstrated. A
   sentence like "our model improves urban planning" would be an unlicensed scope widening -- the
   honesty law's exact failure mode. Write "next region is the kind of prediction that supports
   resource placement in urban planning [cite]," not "we improve urban planning."
2. **Re-verify the revived CBIC citations.** The four-domain sentence is commented out; opening and
   confirming each of `kokkinos2016ubernet`, `wei2022finetuned`, `lipton2015learning`,
   `zhang2020interactive` is required before any enters compiled dissertation prose (R1--R3). Mark
   **[VERIFY at adaptation]**.
3. **Keep the narrowing explicit.** After broadening, the scope statement (§1.4: mobility check-ins,
   Gowalla + Istanbul, next place not predicted) must still land plainly, so the widened motivation
   never reads as a widened claim.

## 4. Flags

- **[NEEDS SIGN-OFF]** -- the Introduction beat "these two tasks matter beyond mobility (recommendation,
  urban planning, and by encoder-provenance even ecology), and we evaluate them in the mobility
  setting." New connective framing of the dissertation's scope; strongly grounded in CBIC/CoUrb's own
  citations but assembled here for the first time. Route through personas 07 + 14.
- **[VERIFY at adaptation]** -- the four CBIC domain-breadth citations, because their source sentence is
  commented out and never passed a citation gate.
- **Fail-closed note** -- no new reference is proposed. Every domain named above is already cited in a
  component paper's bib; the work is revival + re-verification + assembly, not new literature search.

---

## `process/10_specialist_check/specialist_check.md`

# Specialist clarity check — the drafts and the arc

## Action summary (read this first)

Four specialists ran fresh-eyes on the drafts and the arc. **The snippet answer: the arc's substance
is clear and honest under all four lenses — no fabrication, no upgraded verb, no AZ upgrade — but the
drafted Ch.2 prose is not yet "all clear," because the task-pair-change acknowledgment (the corollary
framing) lives only in the storyline and is [NEEDS SIGN-OFF], not on the page.** Two of four rate the
drafts `not_clear_major` on exactly that basis; two rate `clear_with_minor`.

**Already fixed by me in the storyline (pass-2 critic corrections, fail-closed):**
1. **"Incoherent" → "unnatural" (02 §3.1).** The POI/mobility expert showed the static task does not
   become impossible under a per-visit representation — you can pool visit vectors into a POI vector
   (CoUrb's own POI Encoder does this). Softened to "the sequential task is the natural fit; the
   static task needs an extra pooling step that discards the per-visit signal."
2. **Gradient-cosine scope restored (02 §3.3, 08 UW-5).** The MTL expert showed my files stripped the
   scope the MobiWac source carries. Restored verbatim: "+0.001, four seeds each on three of six
   datasets, measured during development on an earlier data preparation, a finding for this pair, not
   a general rule," plus "directional conflict only" and "sharing stopped hurting, not tasks teach
   each other."

**The author must action (I am read-only on the drafts and governing docs):**
1. **[BANCA MAJOR / kill-shot] Land the task-pair acknowledgment on the page.** Route the storyline §2
   corollary through C2 sign-off, then add one sentence to `2.1` and re-word `2.5`'s arc paragraph so
   it does not read as one experiment on a constant pair. All four personas name this.
2. **[CLAIM-HONESTY MAJOR / governance collision] Reconcile NORTH_STAR with UW-3.** NORTH_STAR §4/§6
   still instruct the Ch.4 preface to state CoUrb's protocol as "sample-stratified, weaker than Ch.5"
   — the exact claim pass-2 retracted to [VERIFY]. A preface written from the spine will assert an
   unverified (possibly wrong) protocol as fact. Downgrade NORTH_STAR §4/§6 to [VERIFY] until CoUrb's
   split is confirmed from its codebase. (POI expert flags the same collision against GLOSSARY §3.)
3. **[3× MINOR, shared] Scope the 93% predictability at first mention in `2.1`.** Three of four
   personas independently flag that `2.1` calls Song et al.'s 93% "the reference point against which
   any predictive model should be read," but `2.4` correctly says it does *not* bound category macro-F1
   or region ranking. Scope it to next-place-at-coarse-resolution in `2.1` so `2.4` confirms rather
   than corrects.
4. **[MINOR] Migrate the map-partition legitimacy sentence into `2.1`/`2.4`.** "Predicting over a map
   partition is the standard mobility formulation; we substitute administrative units for grid cells"
   is the most disarming answer to "why census tracts / mahalle" and currently lives only in MobiWac +
   the storyline; add the 7-vs-hundreds-to-thousands cardinality contrast as the "not easier" anchor.
5. **[MINOR] Make the under-review status visible where the MobiWac win is first asserted (`2.5`).**
6. **[MINOR] State the "next category" ↔ "next-POI prediction" name mapping once at the Ch.2→Ch.3 seam.**
7. **[MINOR, MTL] Consider adding Elich (arXiv:2311.04698) where the cosine mechanism is stated** — it
   both strengthens and bounds the claim (verify firsthand before adding). Hand the negative-transfer
   definition's dedicated-anchor question to persona 05.
8. **[MINOR, honesty] Sync the stale 2.3 citation map** (items 5, 7) to the corrected `.tex` so a
   re-derivation does not re-introduce the removed Zhang2020 / PLE-descent bindings.

Full per-persona detail below.

---

# Specialist clarity check — the drafts and the arc

> **What this is.** The author asked to run the specialist reviewers on the drafts (Ch.2 Fundamentals) and
> the arc (the storyline review) for a short "is it all clear" snippet. Four personas ran fresh-eyes,
> read-only, each capped at its five highest-value findings, each verdict traced to opened sources. This
> file records their verdicts verbatim-in-substance. Two findings landed on the storyline files themselves
> and have already been corrected (noted inline); the rest are the author's to action on the drafts and
> the governing docs.

## Verdicts at a glance

| Persona | Verdict | The one thing to fix |
|---|---|---|
| MTL expert | **not_clear_major** | The two-factor resolution under-counts a THIRD simultaneous change that an MTL examiner will name first: task-pair homogeneity. CBIC's null is on a st… |
| POI/mobility expert | **not_clear_major** | Split-protocol legitimacy (my #1 lens). Real prose in 2.5 presents "User-disjoint cross-validation ... [is] what separate[s] a real improvement from a… |
| Claim honesty | **clear_with_minor** | Unresolved collision between the approved spine and its own pass-2 correction on the CoUrb protocol. NORTH_STAR asserts CoUrb's split as settled fact … |
| Banca simulator | **clear_with_minor** | The single kill-shot vector. The CBIC->MobiWac reversal changed three things at once (representation, sharing topology, AND the task pair: {static cat… |

**Convergence.** All four independently name the same #1 issue: the drafted Ch.2 prose does not yet
carry the task-pair-change acknowledgment (the corollary framing lives only in the storyline and is
[NEEDS SIGN-OFF]). Two of four rate the drafts `not_clear_major` on that basis; two rate
`clear_with_minor`. **None found a fabrication, an upgraded verb, or an AZ upgrade** — the honesty
backbone held under four independent lenses.

---
## MTL expert — not_clear_major

**The drafted prose is MTL-clean and the scalarization-skeptic framing is exactly right; but the arc credits two of three simultaneous changes (representation + sharing topology, silent on the task-pair homogeneity change) and the gradient-cosine mechanism travels without the scope its own source carries. Both are examiner kill-shots and must land before the banca.**

### Findings
- **[MAJOR]** The two-factor resolution under-counts a THIRD simultaneous change that an MTL examiner will name first: task-pair homogeneity. CBIC's null is on a static+sequential pair (CBIC itself blamed the static/sequential dissimilarity for negative-transfer risk); MobiWac's win is on a two-sequential pair. Task homogeneity is a canonical determinant of whether sharing helps (task-affinity/grouping literature). Crediting the win to representation+topology while the pair silently changed reads as a moved goalpost. Note 2.3 ALREADY plants the hook -- 'joint training can hurt as easily as it helps depending on the pairing [standley2020tasks]' -- but the frame never connects that seed to the arc's own pair change. 2.5's resolution clause is silent on it.
  - *Location:* `fundamentals/2.5_relevance/2.5_relevance.tex (resolution clause, final ¶); storyline/02_task_choice_endorsement (§3.1/§3.4) + 08_underweighted_sides (UW-1/UW-4); hook planted at 2.3_multi_task_learning.tex ~L33`
  - *Direction (never applied):* Name the third change explicitly and either fold it into the representation thesis (the storyline §3.1 corollary: a per-visit representation makes the static task incoherent, so the coherent pair IS two next-visit properties) or concede it (§3.4: no single ablation isolates representation from task-homogeneity in the final win; CoUrb is the fixed-pair control). Route the corollary through sign-off; do not leave it only in the storyline.
- **[MAJOR]** The gradient-cosine mechanism beat is promoted into the arc stripped of the scope its source carries. MobiWac 02_related.tex states it correctly: '+0.001 across training (four seeds each on three of our six datasets, per-dataset means within ±0.003)' AND 'measured during development ... on an earlier preparation of the data.' The storyline renders it as a bare 'cosine ≈ +0.001' in every place it appears (08 UW-5, 02 §3.3, 03, 04, 07). A measured-mechanism claim that loses '3 of 6 datasets / 4 seeds / development-time / earlier data preparation' is an overstatement, and the earlier-data-prep hedge matters: the mechanism was NOT measured on the identical pipeline that produced the headline win.
  - *Location:* `storyline/08_underweighted_sides/underweighted_sides.md:82 (UW-5) + 02_task_choice_endorsement/task_choice_endorsement.md:144-146 (§3.3); source of truth: articles/[mobiwac]/src/sections/02_related.tex L89-94`
  - *Direction (never applied):* Any frame beat using the number must transport the source's scope verbatim. Consider citing Elich (arXiv:2311.04698) where the mechanism is stated: cosine measures DIRECTIONAL conflict only, so 'no conflict to resolve' should read 'no directional conflict' -- magnitude imbalance is not captured by cosine and Adam already partially normalizes it.
- **[MINOR]** The 'sharing finally helps' half of the negative-transfer reversal is a forward over-claim risk. Near-orthogonal gradients (cosine ≈ 0) are sound evidence that negative transfer is ABSENT, but they are simultaneously evidence AGAINST gradient-level POSITIVE transfer: orthogonal gradients mean the two tasks are not cooperating at the shared trunk either. So 'MTL finally helps' must be read as 'the shared check-in representation lifts both tasks and sharing stopped hurting' (supported by the freeze control -- category gain survives with the region pathway frozen), NOT as 'the two tasks now teach each other.' Storyline UW-5 phrases it correctly ('negative transfer ... is absent'); the risk is a looser frame rendering that upgrades it to task-to-task transfer, which the orthogonality measurement would contradict.
  - *Location:* `storyline/08_underweighted_sides/underweighted_sides.md:82-86 (UW-5); storyline/01 F1/A.3-1 (private spatial path does the region work)`
  - *Direction (never applied):* Phrase the reversal as 'the negative transfer CBIC feared is absent + the representation lifts both,' never 'the tasks help each other.' Keep the freeze control attached wherever the category gain is claimed; it is the evidence that the gain is a trunk/representation effect.
- **[MINOR]** Skeptic-block citation gap tied to the mechanism claim. 2.3's scalarization-skeptic anchor (Kurin, Xin, RLW) is strong and correctly positioned, but Elich (arXiv:2311.04698) -- the paper that shows gradient/angular conflict is not uniquely MTL and that magnitude differences dominate -- is absent, and it is precisely the citation that both strengthens AND bounds the gradient-cosine mechanism the arc leans on. Flagged as a gap to consider, not padding to demand.
  - *Location:* `fundamentals/2.3_multi_task_learning/2.3_multi_task_learning.tex L50-58 (skeptic block)`
  - *Direction (never applied):* Add Elich where the cosine mechanism is stated (Ch.5, and any frame beat); it makes the mechanism claim rigorous rather than asserted.
- **[MINOR]** Negative transfer is DEFINED correctly in 2.3 ('leave a task worse off than its single-task model') but anchored on standley2020tasks (task grouping) + sener2018mgda (multi-objective), not on a dedicated negative-transfer reference. The definition is load-bearing for the whole arc (it is CBIC's fear and MobiWac's rebuttal). Largely persona-05 turf -- flagged as an out-of-lens handoff -- but the must-cite MTL canon expects a dedicated negative-transfer anchor for the definitional sentence.
  - *Location:* `fundamentals/2.3_multi_task_learning/2.3_multi_task_learning.tex L36-40`
  - *Direction (never applied):* Consider a dedicated negative-transfer anchor for the definition; verify its identity firsthand before adding (not opened this session). Hand to persona 05.

### Live-item checks
- **(needs_fix)** Resolution credited to TWO factors (check-in representation + redesigned sharing topology), not representation alone -- MTL-accurate and consistent with the arc's evidence?
  - Two-factor is a genuine improvement over one-factor and both named factors are real; CoUrb isolates representation on the FIXED (dissimilar) pair, so representation-dominance is proven independent of the task change. BUT from an MTL lens the honest count is THREE simultaneous changes: representation, sharing topology, AND task-pair homogeneity. The joint WIN is measured only on the changed pair, so no single controlled ablation separates representation+topology from task homogeneity in the final win (storyline §3.4 concedes this). Two-factor crediting is sound only once the third change is named and folded in (§3.1 corollary) or conceded. The storyline holds the fix; the prose (2.5) does not yet carry it.
- **(sound)** Balancers (PCGrad, Nash-MTL) do not beat a tuned fixed weighting BECAUSE the two tasks' gradients are near-orthogonal (cosine ≈ +0.001) -- MTL-sound reasoning?
  - Sound and aligned with the field's null. Tight for PCGrad specifically: at cosine ≈ 0 PCGrad's conflict-projection is a near-no-op, so it reduces to fixed weighting. The MobiWac SOURCE states it properly scoped (4 seeds, 3/6 datasets, development-time, earlier data preparation). Two caveats, both about statement not logic: (i) cosine measures DIRECTIONAL conflict only -- 'no conflict' should be 'no directional conflict' (magnitude imbalance is not captured; Elich 2311.04698); (ii) the scope must travel with the number into frame prose (see finding 2). Reasoning holds; the risk is transport/precision. I verified the number and its scope exist in the source; I did not re-derive it.
- **(sound)** Hard-sharing (CBIC) -> cross-attention two-stream + private spatial path (MobiWac) framing in 2.3 and the arc -- correct use of MTL terms (hard/soft/structured sharing, negative transfer)?
  - Correct throughout. 2.3 defines hard sharing (common trunk, split at heads) and soft sharing (own parameters, weak coupling) per Ruder; frames cross-stitch/MMoE/PLE/DSelect-k as 'architectures that learn what to share' (structured sharing) accurately; positions the joint model as adopting the shared+task-specific principle via cross-attention 'rather than expert gating' -- correctly avoiding a false PLE/MoE lineage (the F6 fix). Negative transfer is correctly defined. Minor positioning: a cross-attention two-stream is architecturally closest to cross-stitch (learned mixing of two task streams), which the text could name; lumping it under the general principle is acceptable.
- **(sound)** The 'negative-transfer reversal' beat (CBIC feared it; MobiWac shows sharing helping) -- MTL-sound as stated?
  - Sound as the storyline actually states it in UW-5: 'the negative transfer CBIC feared is absent ... gradients near-orthogonal.' That is the correct claim -- no destructive interference. Caveat (see finding 3): orthogonal gradients are ALSO evidence against gradient-level positive transfer, so the 'helping' must be credited to the shared representation (freeze control), not to the tasks teaching each other. The beat is sound if it stays 'sharing stopped hurting + representation lifts both'; it becomes unsound if upgraded to 'the tasks positively transfer.'

### What holds (do not dilute)
Do not dilute these. (1) 2.3's scalarization-skeptic block is exactly right for the field's 2022-2026 null: Kurin + Xin + RLW anchored, and the ruling 'a balancer earns its place only by outperforming a well-tuned fixed-weight baseline' is the correct default prior -- this dissertation's static-weight finding ALIGNS with the field, and the text claims it with the right scope. (2) The arc review already holds the honest line hard: A.3-1, F1, and B.2 all rule that the win must NOT be credited to representation alone, noting representation-only would contradict Ch.5's own text -- protect this two-factor floor. (3) CBIC's null is time-indexed and verb-bound ('does not outperform ... for that configuration'); the Nash-MTL solver-bug containment is held (F2, no amplification in Ch.2). (4) The MobiWac gradient-cosine measurement is genuinely measured and scope-honest IN THE SOURCE -- the evidence is real, the problem is only its transport. (5) 2.4's operative-ceiling correction (the dedicated single-task model, not the 93%% predictability bound, is the ceiling for these tasks) is MTL-correct, and Delta_m carries the 'positive only when each per-task change is established' guard against a blended scalar hiding a sacrificed task. (6) The capacity disclosure (~4.2M vs 1.1M params; benefit is operational, not compute-savings) is held in the arc (F3) -- a key MTL credibility signal. The plans (2.2/2.3/2.4) set up the arc well; my findings are about the frame's causal story and scope transport, not the drafted sentence craft, which is clean.

---
## POI/mobility expert — not_clear_major

**The drafted prose reads clearly and the task-choice defense is domain-sound; one honesty-foundation gap blocks a clean 'all clear' -- user-disjoint CV is sold as the dissertation's protocol in real prose while it is only Ch.5's, and the earlier chapters' splits are unverified and cross-doc-contradicted.**

### Findings
- **[MAJOR]** Split-protocol legitimacy (my #1 lens). Real prose in 2.5 presents "User-disjoint cross-validation ... [is] what separate[s] a real improvement from a hopeful one" as THE dissertation protocol, but it is only MobiWac/Ch.5's. The split strengthening across chapters (Ch.3/4 weaker -> Ch.5 user-disjoint) is the arc's honesty story and is not set up anywhere in the drafted frame. Worse, the foundation is unverified: GLOSSARY sec.3 asserts "Ch.3/Ch.4 used sample-stratified splits" as fact, yet storyline/08 UW-3 retracts that to [VERIFY]. CoUrb's own results.tex describes only "5 folds ... stratified split ... preserving the proportion between categories" with NO user-grouping stated -- the textual signature of a sample-level split, but not conclusive. If CoUrb turns out user-disjoint the strengthening beat collapses; if it is sample-level, 2.5 currently lets a banca believe all three chapters used the strong protocol.
  - *Location:* `fundamentals/2.5_relevance/2.5_relevance.tex:32 (real prose); GLOSSARY.md sec.3 vs storyline/08 UW-3; CoUrb_2026/src_en/sections/results.tex:16`
  - *Direction (never applied):* Confirm CoUrb's actual split from the CoUrb codebase (not the paper text); then scope 2.5's user-disjoint claim to Ch.5 and foreshadow the strengthening in 2.4 (or a 2.4 pointer to the prefaces). Reconcile GLOSSARY (asserts sample-stratified) with storyline UW-3 ([VERIFY]) once verified.
- **[MINOR]** Floor/ceiling scope seam. 2.1 opens on Song et al. 93% next-location predictability and calls it "the reference point against which any predictive model should be read ... one that approaches it is near the limit the data allows." But this dissertation predicts next category and next region, not next place -- and 2.4 itself correctly states the 93% figure "is not, however, a ceiling on seven-class category macro-F1 or on region ranking." A thin frame's opening ceiling frames the whole chapter; a reader carries 93% forward to the category/region results the section is really about. Escalates to MAJOR if it reaches the banca uncorrected.
  - *Location:* `fundamentals/2.1_poi_prediction_tasks/2.1_poi_prediction_tasks.tex:16-18 vs fundamentals/2.4_datasets_and_evaluation/2.4_datasets_and_evaluation.tex:49-53`
  - *Direction (never applied):* Scope the 2.1 sentence to next-place/next-location predictability (the task NOT studied), and name the operative reference points for the studied tasks (majority-class and Markov-1 floors, dedicated single-task ceiling) as 2.4 already does.
- **[MINOR]** The region task's strongest field-legitimacy sentence is missing from the drafts. "Predicting over a map partition is the standard mobility formulation (grid cell); we substitute administrative units (census tract/mahalle)" is a correct characterization of the field (next-location over a discretized grid/region is canonical, luca2021mobilitysurvey), and it is the most disarming answer to "why census tracts / mahalle?". It lives only in MobiWac sec.2.2 and the storyline plan -- it is absent from the drafted 2.1 and 2.4 (grep confirms). For a Ch.2 that must set up the arc, the newest task should carry its own legitimacy here.
  - *Location:* `absent from fundamentals/2.1 and fundamentals/2.4; present in MobiWac src/sections/02_related.tex and storyline/02 sec.2.3`
  - *Direction (never applied):* Migrate the map-partition/administrative-unit sentence into 2.1 or 2.4; add one clause that administrative units are non-uniform (population-drawn), unlike uniform grid cells, so the label geometry differs. Consider stating the concrete cardinality contrast (7 categories vs hundreds-to-thousands of regions) here as the 'not easier' anchor.
- **[MINOR]** The task-change-as-corollary reasoning is sound as a MOTIVATED corollary, but one link overreaches. storyline/02 sec.3.1 says a per-visit representation makes static per-POI category classification "incoherent" / "loses its footing." A per-visit representation does not abolish the POI or its ground-truth category; the standard escape hatch is to pool visit vectors into a POI vector and classify that -- which is exactly what CoUrb's own POI Encoder does ("the resulting embedding is generated per category and remapped to each POI"). So the honest claim is "the sequential task is the natural fit for a per-visit representation," not "the static task becomes incoherent." The framing is correctly flagged [NEEDS SIGN-OFF] and sec.3.4 concedes the experimental gap; that concession must reach the frame text, not stay only in the storyline doc.
  - *Location:* `storyline/02_task_choice_endorsement/task_choice_endorsement.md sec.3.1 (and sec.3.4 concession); CoUrb_2026/src_en/sections/metodology.tex:141 (POI Encoder remap)`
  - *Direction (never applied):* Soften 'incoherent' to 'no longer the natural task for a per-visit representation'; acknowledge the pooling alternative once and say why the sequential task is preferred; carry sec.3.4's 'no single controlled ablation isolates representation from task-homogeneity in the final win' into a Ch.2 scope note or Ch.6 limitation.
- **[MINOR]** Load-bearing novelty negative stated flatly. 2.3 asserts "no multi-task model among them predicts the next region as a co-equal end target alongside the next category ... the joint setting is open." This is the dissertation's core gap claim and a banca target (someone will name a counterexample). It is a negative over a large, fast-moving literature that I cannot exhaustively verify from here.
  - *Location:* `fundamentals/2.3_multi_task_learning/2.3_multi_task_learning.tex:71-74`
  - *Direction (never applied):* Hedge to a scoped, defensible form ('to our knowledge, no prior multi-task model predicts next category and next region as co-equal ends') and have the citation auditor (persona 05) confirm the negative against the frontier set before it ships.

### Live-item checks
- **(sound)** Next category + next region as targets, exact next place deliberately NOT predicted -- is the storyline/02 task-choice defense domain-sound?
  - Domain-sound and unusually well-built: service-first (category=intent, region=where to prepare) + means->ends (HMT-GRN uses region to constrain beam search, CatDM uses category to prune candidates; promoted from means to ends, zhu2022drrgnn / capanema2023poirgnn) + not-easier (region spans hundreds-to-thousands of classes vs 7 for the dropped static task) + standard-formulation. 2.1 executes the distinctness and means->ends cleanly and states 'we do not predict the exact next place' once (2.1:37). Caveat: the standard-formulation sentence and the concrete cardinality contrast are not yet in the drafted sections (finding 3); class counts re-verify at adaptation (N1).
- **(sound)** Task pair evolved (CBIC/CoUrb = static category classification + next category; MobiWac = next category + next region); storyline/02 argues the task change is a COROLLARY of the check-in representation. Sound or a stretch?
  - Sound as a motivated corollary and correctly [NEEDS SIGN-OFF]; the causal direction (representation change -> task change) is defensible and CBIC did blame the static/sequential dissimilarity. But the word 'incoherent' overreaches -- pooling visit vectors to a POI label is standard (CoUrb's POI Encoder does exactly this remap-to-POI), so the static task becomes unnatural, not impossible. Soften the wording and carry sec.3.4's honest concession into the frame (finding 4).
- **(sound)** 'Predicting over a map partition is the standard mobility formulation (grid cell); we substitute administrative units (census tract/mahalle)' -- correct characterization of the field?
  - Correct. Next-location prediction over a discretized grid/region is a canonical mobility formulation (luca2021mobilitysurvey), and substituting administrative units for arbitrary grid cells is legitimate. Two caveats: (a) the sentence is currently ABSENT from the drafted 2.1/2.4, living only in MobiWac + the storyline plan (finding 3); (b) census tracts / mahalles are non-uniform (population-drawn) unlike uniform grid cells, so the label geometry differs -- worth one clause where the claim lands.
- **(sound)** storyline/08 UW-2: CoUrb has NO single-task baseline (only compares vs MTLNet). Verify against CoUrb src_en/sections. Sound?
  - Verified firsthand. CoUrb's only baseline is 'MTLNet with DGI' (metodology.tex:36-38), itself a multi-task hard-sharing model; every comparison is ST-MTLNet vs MTLNet, both multi-task (results.tex:20 category 21/21; results.tex:28 next-POI 16/21). A grep for single-task/STL/dedicated returns zero hits in the CoUrb sections. So CoUrb tests representation-vs-representation only and is silent on 'does MTL help.' Drafted 2.5 already respects this boundary ('the representation, rather than the architecture, is the lever ... the same model receives') -- protect that; the Ch.4 preface must state the boundary explicitly [NEEDS SIGN-OFF]. Sharpening: CoUrb's pair is two category tasks (static category + next category), so its representation-dominance evidence is category-side only; the region task never appears in a controlled representation swap.

### What holds (do not dilute)
Protect these -- they read clearly and are domain-correct. (1) The three-task distinction in 2.1 is clean and disciplined: 'we do not predict the exact next place' stated once, and the entire next-place model lineage (ST-RNN, DeepMove, HST-LSTM, Flashback, STAN, GeoSAN, GETNext) explicitly labeled background ('every model named in this paragraph predicts the exact next place'). This is both the GLOSSARY law and the field's law; do not blur it. (2) 2.5 frames CoUrb as a representation experiment ('the same model receives'), consistent with UW-2 -- it does NOT overclaim that CoUrb showed MTL works. (3) 2.4's metric conventions are domain-correct and defensible: macro-F1 primary for the imbalanced category task with the majority-class floor named, Acc@10 + MRR for region, unseen-region-counts-as-a-miss (OOD) stated, Markov-1 floor over the training partition, and verbs bound to tests (outperforms = paired superiority; matches = TOST within a two-point margin). No cross-cardinality Acc@K comparison is implied anywhere. (4) The task-choice defense (storyline/02) is the strongest part of the arc work -- a positive, honest position, not a scope apology; keep its shape and just migrate its best sentences into the drafted sections.

---
## Claim honesty — clear_with_minor

**Drafted prose is honest and the arc is well-governed; the one thing to fix before Ch.4 is drafted is a governance collision -- NORTH_STAR still asserts CoUrb's protocol as settled after pass-2 retracted it -- plus two real minors in the shipping prose.**

### Findings
- **[MAJOR]** Unresolved collision between the approved spine and its own pass-2 correction on the CoUrb protocol. NORTH_STAR asserts CoUrb's split as settled fact and instructs the preface to state it -- "split is stratified by sample, not user-disjoint (weaker than Ch.5's protocol -- say so, it strengthens the arc)" (§4 Ch.4) and "protocol weaker than Ch.5's (sample-stratified split) -- flagged, not hidden" (§6 Ch.4 preface). storyline/08 UW-3 retracted exactly that claim to [VERIFY] ("I cannot verify this firsthand ... the protocol difference ... is [VERIFY], not established"). Because §6 is the spine drafting agents "expand; they do not reinvent," a Ch.4 preface written from it will assert an unverified -- possibly wrong -- protocol claim as fact. The retraction has not propagated to the governing doc.
  - *Location:* `NORTH_STAR.md:§4 Ch.4 / §6 Ch.4-preface  vs  storyline/08_underweighted_sides/underweighted_sides.md:UW-3`
  - *Direction (never applied):* Down-grade NORTH_STAR §4/§6 to [VERIFY] (or strike the "say so" instruction) until the author confirms CoUrb's actual split from the codebase / slides/judge_feedback.md; do not build a preface beat on the protocol gap meanwhile.
- **[MINOR]** 2.1 over-scopes the 93% predictability as a universal reference point, which 2.4 then walks back. 2.1 ¶1: "...potential predictability of about 93% on where an individual goes next. That ceiling is the reference point against which any predictive model should be read ... one that approaches it is near the limit the data allows." 2.4 (correctly, fact-gate F5) narrows it: song2010limits is "a bound for predicting the next location at coarse resolution ... it is not, however, a ceiling on seven-class category macro-F1 or on region ranking," with the dedicated single-task model as the operative ceiling. Two sections of the same chapter disagree on the number's scope; the real-prose section (2.1, read first) generalizes a next-location bound onto the next-category / next-region tasks the dissertation actually builds.
  - *Location:* `2.1_poi_prediction_tasks/2.1_poi_prediction_tasks.tex:¶1  vs  2.4_datasets_and_evaluation/2.4_datasets_and_evaluation.tex:reference-points ¶`
  - *Direction (never applied):* Scope 2.1's reference-point sentences to next-location coarse-resolution (mirror 2.4) so 93% does not read as a ceiling/limit for the category and region models.
- **[MINOR]** The resolution clause in the hinge paragraph grammatically subordinates the second factor. 2.5 ¶4: "...what a representation built for check-ins unlocks for a redesigned joint model, one that ... outperforms ..." -- both factors are named (not an upgrade to representation-alone), but the syntax makes the representation the active enabler and the sharing topology a recipient, softer than the approved spine's co-equal phrasing ("a check-in-level representation and the right sharing topology," NORTH_STAR §1; "plus a redesigned sharing topology," §6) and than honesty-flag F1's ruling that the *resolution* stay two-factor because MobiWac §4.2 makes the private spatial path what keeps region competitive. This is precisely the one-factor temptation F1 names; the hinge paragraph is where it must not creep in.
  - *Location:* `2.5_relevance/2.5_relevance.tex:¶4 (clause 3)`
  - *Direction (never applied):* Echo the spine's co-equal "and/plus" so the redesigned sharing topology reads as a co-cause of the win, not the vehicle the representation acts through.
- **[MINOR]** The 2.3 citation map carries two claim-to-source bindings the corrected .tex prose deliberately removed, so re-deriving citations from the map would re-introduce them. (a) Map item 7 attributes the negative-transfer definition to Zhang2020; the .tex ledger removed Zhang2020 ("= iMTL next-POI recommender, NOT negative-transfer literature") and folded the claim onto standley2020tasks. (b) Map item 5 calls PLE "the structured-sharing topology the joint model descends from"; the .tex was reworded to "adopts [the principle] ... though it realizes it with cross-attention" precisely to avoid the false descent ("NOT a PLE/MoE descendant"). The shipping prose is correct; the working map is stale.
  - *Location:* `2.3_multi_task_learning/2.3_citations.md:items 5,7  vs  2.3_multi_task_learning/2.3_multi_task_learning.tex:ledger`
  - *Direction (never applied):* Sync map items 5 and 7 to the .tex (standley2020tasks for negative transfer; drop "descends from" for PLE). Existence-of-citation belongs to persona 05; flagged here as an attribution/lineage claim mismatch.
- **[NIT]** The document's core result numbers are asserted in draft prose ahead of their source-of-truth trace. 2.5 states "four of six datasets" and "two-point margin"; the section ledger NOTE 10 flags "confirm against Ch.5 RESULTS_BOARD.md / PAPER_PLAN §3 at adaptation," and NORTH_STAR §2 (the only current trace) is itself "orientation only -- re-verify ... before any of them enters dissertation text." The flag is live and correct; the risk is only that it gets lost between draft and gate.
  - *Location:* `2.5_relevance/2.5_relevance.tex:¶4 + ledger NOTE 10`
  - *Direction (never applied):* Ensure NOTE-10 adaptation trace to RESULTS_BOARD.md is cleared before this section leaves draft; the [VERIFY-at-adaptation] flag is currently the only thing between the prose and an untraced result number.

### Live-item checks
- **(sound)** storyline/06 honesty flags bind verbs to tests (outperforms=paired superiority; matches=TOST 2pp; AZ 0.00 never upgraded)
  - F6 binds outperforms->paired superiority, matches->TOST within a two-point margin, and "never upgrade the zero-delta dataset," and mandates the frame summary carry the four-of-six split + "matches" for AL/AZ. Corroborated against NORTH_STAR §2 (outperforms Istanbul/FL/TX/CA, matches AL/AZ) and against the drafted 2.5 result sentence, which uses the exact bound form; no banned verb (beat/win/tie) present.
- **(sound)** Two-factor resolution stated honestly (NOT upgraded to representation-alone)
  - NORTH_STAR §1/§6 and 2.5 clause 3 both name the check-in representation AND the redesigned joint model; 2.2 states the diagnosis as "the representation, more than the architecture" (hedged, not "alone"). No representation-alone upgrade of the win. Caveat: 2.5's "unlocks for" phrasing subordinates the second factor (top finding #3) -- present but grammatically softened, so still sound, not a violation.
- **(sound)** New connective claims flagged [NEEDS SIGN-OFF], esp. storyline/02 'task change is a corollary of the representation thesis'
  - 02 §3.1 marks the corollary claim [NEEDS SIGN-OFF] explicitly ("needs author sign-off before it enters the text ... not verbatim in any source"), routed through AGENT_GUARDRAILS §3 C2 + personas 07 and 14; UW-1/UW-2/UW-4/UW-5 connectives likewise flagged. Verified the corollary is held OUT of drafted 2.1/2.5 -- 2.1 makes only the grounded means->ends argument (Lim2022/yu2020catdm/zhu2022drrgnn/capanema2023poirgnn), not the corollary framing.
- **(sound)** storyline/08 UW-3 retraction of the 'CoUrb weaker sample-stratified protocol' claim to [VERIFY] -- correctly handled, fail-closed?
  - The retraction itself is textbook fail-closed: it names what it checked (CoUrb results.tex = "mean and std over 5 folds" only; DATA_SPLITS.md does not attribute per paper; MobiWac 05_setup.tex L28 explicitly user-split), states it cannot verify firsthand, suspends the dependent pass-1 recommendation (G-13), and flags [VERIFY]. Sound AS HANDLED IN 08. Not yet resolved across governance: it collides with NORTH_STAR §4/§6, which still assert the claim as settled -- see top finding #1.

### What holds (do not dilute)
Protect these; do not dilute in any trim. (1) 2.1's task-scope discipline is exemplary -- next place "is named only to hold it apart from the two the dissertation studies," and the three targets stay distinct throughout; this is the arc's load-bearing honesty device. (2) 2.4's verb-test law (Wilcoxon->"outperforms", TOST 2pp->"matches") and its verbatim application in 2.5's result sentence, with AZ held in "the other two" and never upgraded, is the document's honesty backbone. (3) The time-capsule discipline is already in the drafted prose -- 2.5 "reports an honest answer for that configuration," 2.3 "a result that holds for that configuration" -- and 2.3 describes Nash-MTL as a method (navon2022nashmtl) without amplifying CBIC's superseded "consistently better" claim. (4) The plans set up the arc cleanly: 2.2's one-hot->DGI->HGI->check-in spine with correct encoder attribution (the decomposed encoders are CoUrb's, not MTLnet's) directly protects the two-factor story; 2.3's "balancers rarely outperform tuned fixed weights" + the next-region-as-end-target gap; 2.4's reference points and CV protocol. (5) The storyline's fail-closed instinct is strong -- OpenAlex sweeps that returned noise produced no new citation, and UW-3 corrected a pass-1 claim rather than defend it.

---
## Banca simulator — clear_with_minor

**Aprovado com correcoes menores: the drafted background reads cleanly and the honesty discipline is exemplary, but before the defense the frame must say out loud that the task pair itself changed across the arc, or an examiner reads a moved goalpost.**

### Findings
- **[MAJOR]** The single kill-shot vector. The CBIC->MobiWac reversal changed three things at once (representation, sharing topology, AND the task pair: {static category classification, next category} -> {next category, next region}), and CBIC itself blamed its null partly on the static/sequential dissimilarity. The arc review diagnoses this in full (storyline/08 UW-1: 'changed the representation, the sharing topology, and the task pair'; storyline/02 stages the corollary fix). But the drafted Ch.2 prose does not carry it: 2.1 names the static task only generically ('A fourth, non-sequential task, category classification, ... from static features'), never as the task the earlier chapters actually paired; 2.5's arc paragraph ('It first asks ... It then asks ... It finally asks') narrates null->diagnosis->resolution as if the pair were constant. The disarming move is [NEEDS SIGN-OFF] and absent from the page, so the moved-goalpost attack is live as drafted.
  - *Location:* `fundamentals/2.1_poi_prediction_tasks.tex (closing para + 'A fourth, non-sequential task'); fundamentals/2.5_relevance.tex (arc para); storyline/02 sec.3.1, storyline/08 UW-1/UW-4`
  - *Direction (never applied):* Route the 'task refinement is a corollary of the representation thesis' framing (storyline/02 sec.3.1) through C2 sign-off, then land one acknowledging sentence in 2.1 and re-word 2.5's arc paragraph so it does not read as one experiment on a constant pair.
- **[MINOR]** Terminology seam a sloppiness-sensitive examiner flips on (Q22). The frame uses the canonical 'next category' throughout 2.1/2.3, but NORTH_STAR sec.1 records that the reproduced CBIC/CoUrb chapters call their sequential task 'next-POI prediction' while predicting the category of the next POI. Read across the whole build, the banca meets two names for one task at the Ch.2->Ch.3 seam.
  - *Location:* `fundamentals/2.1 & 2.3 (canonical 'next category'); NORTH_STAR.md sec.1 task-name mapping; reproduced Ch.3/Ch.4`
  - *Direction (never applied):* State the name mapping once at the seam (Ch.3 preface, or a Ch.2 footnote at first use of 'next category') so the reproduced 'next-POI prediction' reads as the same task, not a drift.
- **[MINOR]** The 93% predictability ceiling is over-scoped at first mention and then walked back. 2.1: 'That ceiling is the reference point against which any predictive model should be read.' 2.4 later narrows it: 'it is not, however, a ceiling on seven-class category macro-F1 or on region ranking.' A linear reader hits the universal claim first, then learns two sections on that it does not bound the tasks actually studied.
  - *Location:* `fundamentals/2.1 para 1 ('any predictive model'); fundamentals/2.4 ('not ... a ceiling on ... macro-F1 or on region ranking')`
  - *Direction (never applied):* Scope the 93% at first mention in 2.1 (it bounds next-place at coarse resolution; the operative ceiling for the studied tasks is the dedicated single-task model), so 2.4 confirms rather than corrects it.
- **[MINOR]** 'Why these two tasks' (Q5) is answered in Ch.2 only at the academic positioning level (2.1's means->ends: category/region promoted to 'co-equal ends'). The stronger, more disarming service-utility answer (what kind of place to prepare; which part of the city to provision) is developed in storyline/02 sec.2.1 but routed to the still-unwritten Ch.1, so it is not yet anywhere on the page.
  - *Location:* `fundamentals/2.1 (closing 'co-equal ends'); storyline/02 sec.2.1 ('lift ... into the Introduction')`
  - *Direction (never applied):* Confirm Ch.1 will carry the utility motivation before the banca build, and echo its one-sentence form early (Intro or 2.1) so the first 'why these tasks' answer is not purely the internal means->ends one.
- **[MINOR]** The arc's payoff win is asserted in the fundamentals chapter without its status caveat nearby. 2.5 claims the joint model 'outperforms the dedicated single-task models on the next category everywhere ... and on the next region at four of six datasets' with no 'submitted, under review' marker; the time-capsule/status framing lives only in the unwritten Ch.5 preface, which the reader reaches much later. Overclaim-adjacent for an under-review result (Q20).
  - *Location:* `fundamentals/2.5_relevance.tex (arc para, MobiWac win); NORTH_STAR.md sec.3 time-capsule rule + status wording`
  - *Direction (never applied):* Make the under-review status visible where the win is first asserted (a clause in 2.5 or a forward-pointer to the Ch.5 preface), so Ch.2 does not read a settled published win for an under-review paper.

### Live-item checks
- **(sound)** Does the arc hold as ONE document (coletanea unity), or three stapled papers? (Q19)
  - Sound for the drafted Ch.2 itself: the representation spine (one-hot->DGI->HGI->check-in level, 2.2) threads Ch.3/4/5 explicitly, the lineage table is the unifying device, and 2.5 is a genuine hinge, not a paper-by-paper recap. Caveat, from the storyline's own admission: document-level unity rests on the Ch.1 arc narrative and the three time-capsule prefaces, which are planned and unwritten. Ch.2 does its integrative job; the full 'one document' verdict is earned only once those land.
- **(needs_fix)** Task pair changes across the arc -- kill-shot under arguicao? Does storyline/02 disarm it?
  - storyline/02 disarms it well as a PLAN (the corollary framing + CoUrb as the fixed-pair control + the measured gradient near-orthogonality), and the diagnosis in 08 is honest and complete. But the disarming content is [NEEDS SIGN-OFF] and is not yet in the drafted 2.1/2.5, which are silent on the task-pair change. As drafted, the arc is defensible in the reviewer's notes but not on the page. This is finding 1.
- **(sound)** Why MTL / why these two tasks (Q4/Q5) -- answered convincingly by drafts + arc?
  - Why MTL is answered honestly in 2.3 (shared representation may help; whether it does is measured, and a well-tuned fixed-weight baseline is treated as a serious competitor -- the null is not hidden). Why these two tasks is answered at the positioning level in 2.1 (means->ends) and very convincingly in storyline/02. The gap is placement, not substance: the service-utility form of the answer is not yet on the page (finding 4). Q4's same-tuning-budget question is a Ch.5 methods matter, correctly outside Ch.2.
- **(needs_fix)** RQ answered on TWO DIFFERENT task pairs (storyline/08 UW-4) -- banca-safe as framed?
  - Not yet as drafted. CBIC's 'no' is on {category classification, next category}; MobiWac's 'yes' is on {next category, next region}. 2.5's arc paragraph presents this as null->resolution without flagging the pairs differ, which reads as 'same experiment, opposite result.' storyline/08 UW-4 flags the exact wording as [NEEDS SIGN-OFF]. Defensible with explicit handling (the pair changed for a principled reason); dangerous if presented as like-for-like. Same root as finding 1.

### What holds (do not dilute)
Protect these; they are what makes the drafts defensible. (1) Verb-binding is exemplary: 2.4 binds 'outperforms' to a paired Wilcoxon test and 'matches' to TOST within a two-point margin, and 2.5 states the MobiWac result in exactly those bound terms without upgrading the AL/AZ non-inferior pair to a win. (2) The three targets are kept distinct and next place is disclaimed cleanly and early (2.1: 'It does not predict the exact next place'), repeated in 2.5. (3) 2.5 scopes CoUrb correctly as a representation experiment ('whether the representation, rather than the architecture, is the lever'), avoiding the momentum-trap of claiming CoUrb re-established MTL-beats-single-task (storyline/08 UW-2's exact risk). (4) The 'same place, different visit, same vector' limitation (2.2) is the hinge of the whole argument and is stated crisply. (5) The storyline's fail-closed honesty -- no new citation minted from the OpenAlex noise, and pass-1 self-corrections in UW-2/UW-3 -- is exactly the discipline a banca rewards; do not edit the concessions away.

---

## `process/11_full_arc_rereview/five_verdicts.txt`

```
==============================================================================================
### Cold reader — ready_with_fixes
HEADLINE: The arc as planned is a genuinely good story that would carry a cold reader once the frame narrates it, but the package leaves three things hanging: the author's own unanswered doubt under the N3 beat, an unbudgeted pile-up of approved moves all routed to Chapter 1, and a drafted sentence in 2.1 that a cold reader will experience as false on reaching Chapter 3.

OVERLOOKED:
  [MAJOR] The author's N3 reply contains a direct, unanswered question plus an experiment offer that no file in the package registers. He writes that the current why-MTL-wins evidence feels 'nao muito convincentes', asks for an opinion, and offers local or nespdgpu (SSH) experiments. PANORAMA, the specialist check, and the README all treat N3 as 'Approved' and closed. The Conclusion's centerpiece beat (why the joint model wins without positive gradient-level transfer) thus rests on evidence the author himself doubts, and an undecided experiment question can silently reopen results mid-drafting -- with governance implications for an under-review paper.
      @ storyline/AVAL_NECESSARIA_2_ptBR.md:155-158 (Author line under N3); absent from PANORAMA_ptBR.md secs 4/8
      -> Answer the question explicitly before drafting Ch.6: decide whether follow-up experiments (e.g. the fixed-pair ablation file 02 sec 3.4 names as future work) are in-scope for the dissertation or logged as future work, and record the ruling in the decisions ledger.
  [MAJOR] The cumulative load on Chapter 1 was never assessed after the approvals. Nearly every approved move routes there: the arc as structural spine (Item 8), the stakes paragraph, beyond-mobility breadth (Item 11), the mechanism sentence, the three-legged task-choice endorsement (Items 1/2 + N1), why-representation-before-architecture (Item 5), why-check-in-level (Item 4), plus the mandated beats of NORTH_STAR sec 6.1. The pacing/craft lens (05) predates all of these approvals. To a cold banca member, an Introduction that pre-answers every possible objection before showing any evidence reads as defensive and delays the story; several moves carry unadjudicated 'and/or' placements (Ch.1 and/or Ch.4 preface and/or Ch.5 recap).
      @ storyline/PANORAMA_ptBR.md sec 7 (Cap. 1 list); storyline/05_craft_pacing_and_voice/ (pass-1 only); AVAL items 1,2,4,5,8,11 + N1 'Onde entra' fields
      -> Before drafting, write a one-page Ch.1 beat budget assigning each approved move exactly one home (Ch.1 vs Ch.4 preface vs Ch.5 recap vs Ch.6), so the Introduction narrates the arc rather than litigating it.
  [MAJOR] 2.1's scope sentence is not merely silent on the task-pair evolution -- it is affirmatively misleading for a linear reader. 'The work reported here predicts the next category and the next region' reads as a statement about the whole document; two chapters later Ch.3 predicts static category classification plus a task called 'next-POI prediction'. The cold reader experiences this as a contradiction ('didn't it just say the opposite?'), compounded by the absent name mapping. The catalogued specialist finding asks to ADD an acknowledging sentence; the cold-reader escalation is that the existing sentence must also be EDITED, because as written it will be falsified by Chapter 3.
      @ fundamentals/2.1_poi_prediction_tasks/2.1_poi_prediction_tasks.tex:36-38; contrast NORTH_STAR.md sec 1 task-name mapping
      -> When landing the approved corollary sentence, rescope this sentence (e.g. name the pair evolution: the earlier studies pair the static task with next category; the final study predicts next category and next region) and state the next-category/next-POI name mapping once at the Ch.2-to-Ch.3 seam.
  [MINOR] The concession in file 02 sec 3.4 -- no single controlled ablation separates representation from task-homogeneity in the final win -- has no recorded author sign-off and no assigned home. The aval items covered the corollary (Item 1) and the answer wording (Item 3), but the concession itself, which every specialist calls necessary ('carry sec 3.4's concession into the frame'), was never a numbered item. Under fail-closed C2, a drafting agent must either omit it (the examiner's opening stays live) or insert an unapproved frame statement.
      @ storyline/02_task_choice_endorsement/task_choice_endorsement.md sec 3.4 and sec 4 step 6; absent from AVAL_NECESSARIA_ptBR.md and AVAL_NECESSARIA_2_ptBR.md item lists
      -> Add the concession as a one-line third-round aval (or an explicit author 'approved' note in the ledger) and fix its home: Ch.2 scope note or Ch.6 limitation, not both.
  [MINOR] Two of the three candidate dissertation titles embody the exact one-factor flattening that honesty flag F1 bans everywhere else. 'One Model, Two Tasks: Representation-Driven Multi-Task Learning...' credits the win to representation alone, and 'Check-in-Level Representations for Multi-Task Point-of-Interest Prediction' names only the first factor. The title is the coldest reader's very first contact with the arc, the decision (NORTH_STAR open item 8) is due now for the defense-build front matter, and no document has run the shortlist against the two-factor rule.
      @ NORTH_STAR.md sec 5 item 8 (title candidates, lines 196-200); honesty rule at storyline/06_honesty_under_pressure/honesty_flags.md F1
      -> Apply the F1 two-factor test to the title shortlist before front matter is drafted; the first candidate ('From Representations to a Single Joint Model...') is the only one that survives it as written.
  [MINOR] The recommended drafting order conflicts with the package's own pending verifications. PANORAMA sec 8 recommends drafting Ch.1 first ('fixa a voz e o arco'), yet Ch.1's problematizacao is where the still-unverified material lives: N1 leg 2 (the region-more-present-in-literature comparison, [VERIFY]) and the Item 11 beyond-mobility external anchors (search authorized, OpenAlex restored per the author's N1 reply, but not yet run). Drafting Ch.1 first with those holes either stalls the draft or tempts memory-citation in the most visible chapter.
      @ storyline/PANORAMA_ptBR.md:194-197 (writing-order suggestion) vs sec 6 (pending work); AVAL_NECESSARIA_2_ptBR.md N1 Author line (OpenAlex restored, CAFe offered)
      -> Run the dedicated, open-and-verify beyond-mobility search first (the author has unblocked it), or start with the low-risk prefaces and recap subsections that PANORAMA itself names as the alternative opening move.

APPROVED-MOVES CHECK:
  (sound) Item 1 + N1 -- task change as corollary, plus the three-legged literature/utility endorsement
      For a cold reader the positive, service-first endorsement reads as a position rather than a scope apology, which is exactly the register that disarms suspicion. Leg 2 (the comparative literature-presence claim) must wait for its verified anchor; drafting legs 1 and 3 first, as proposed, is the right split.
  (sound) Item 2 -- category and region as two coordinates of the next visit, promoted from means to ends
      The most intuitive framing in the package for a naive reader, and the 7-vs-520-to-8501 class-count contrast is the single most disarming fact available. Land the cardinality contrast on the page, not only in the storyline.
  (sound) Item 3 + N2 -- the answer spans two task pairs, bridged by CBIC's own future work
      'The progression CBIC itself announced' is what carries a cold reader across the null without smelling a moved goalpost. Keep F4's guard: CBIC opened three doors; do not retro-read it as already knowing the answer was representation.
  (sound) Item 4 -- why check-in level specifically (the per-place-vector ceiling)
      Repairs the arc's least-motivated jump; without it Check2HGI is a rabbit from a hat. This is the bridge a first-time reader needs most.
  (sound) Item 5 -- why representation before architecture, one paragraph
      One paragraph is the right size; it converts two visibly hanging hypotheses into a demonstration of method.
  (risky) Item 6 -- CoUrb isolates representation, stated 'brief and with criterio' per the author
      The author's brevity instruction and the reviewers' load-bearing-precision requirement pull in opposite directions and the package never reconciles them. Too brief and the momentum-carried reader concludes CoUrb showed MTL works; too prominent and it invites the questions the author fears. The drafted boundary sentence should be tested on a fresh cold reader before it ships.
  (risky) Item 7 + N3 -- name the negative-transfer reversal and explain why MTL wins (trunk + cross-attention gate, never parameters)
      Sound as scoped (directional-conflict-only caveat, freeze control attached, parameter count as cost not cause), but the author's own unanswered doubt about the convincingness of this evidence sits directly beneath it (overlooked finding 1). Settle that before the Conclusion is drafted.
  (sound) Item 8 -- the honest arc as the structural spine of the Introduction
      The highest-leverage move in the package; it is what turns three well-written but separately-voiced papers into a story a cold reader can follow. Subject to the Ch.1 load budget (overlooked finding 2).
  (sound) Item 9 -- the Ch.5 recap subsection bridging CoUrb to MobiWac
      Welds the only seam with no native bridge; without it the diagnosis-to-resolution jump is invisible in Ch.5's own text.
  (sound) Item 10 resolution -- no bridge table; the recaps and arc paragraph carry the logic
      Matches the Viegas precedent and respects the author's repetition worry. The burden it shifts onto the recaps is real: they must carry actual content (what was established, what it forced), or the F8 fake-cohesion failure mode returns.
  (risky) Item 11 + N1 -- motivate the tasks beyond mobility (illustration, never demonstrated capability)
      The direction is right and the author has now unblocked the search, but every external anchor is still unverified and the traffic-control example has no source at all yet. The illustration-not-capability line must hold word by word, and nothing should be drafted from memory in the meantime.

NARRATIVE QUALITY: As a story, this is now a good narrative -- a real null, a controlled diagnosis, a two-factor resolution, and a mechanism (the same place, a different visit, the same vector) that makes the turn feel inevitable rather than lucky; with the approved moves it would carry me from cover to conclusion. But today the carrying is promissory: everything that would make a first-time reader feel the arc -- the Introduction spine, the prefaces, the recaps, the task-pair admission -- is approved and unwritten, and the one place the drafted prose speaks on the tasks' scope will read as false when I reach Chapter 3. The plan is right; the reading experience does not exist yet, and the residual risks are all in the gap between the two.
TOP PRIORITY BEFORE DRAFTING: Land the task-pair evolution on the page: edit 2.1's 'The work reported here predicts...' sentence (it will be falsified for a linear reader by Chapter 3) and reword 2.5's arc paragraph so the null and the win are not narrated as one experiment on a constant pair -- every specialist converges on this and it is the one banca kill-shot still live in real prose. Immediately after, answer the author's open N3 question so the Conclusion's why-MTL-wins beat rests on evidence the author himself believes.

==============================================================================================
### Claim honesty — ready_with_fixes
HEADLINE: The approved claims are honest at their core and every load-bearing number/mechanism traced to source this session; but the summary layer has drifted on one load-bearing sentence (PANORAMA denies the shared trunk that N3 credits), N2's headline reads stronger than CBIC's actual future-work text, and the CoUrb-protocol retraction (UW-3) still has not propagated to NORTH_STAR/GLOSSARY -- fix the paper trail before any frame sentence is drafted.

OVERLOOKED:
  [MAJOR] The PANORAMA logline contradicts the approved N3 attribution and the GLOSSARY on the shared trunk. PANORAMA section 1 says the two tasks come to share 'via atencao cruzada em vez de um tronco comum' (via cross-attention INSTEAD OF a common trunk), but the GLOSSARY defines the cross-attention stack AS 'the shared trunk' (entries 'the joint model' and 'the shared trunk'), and the freeze-control finding N3 rests on attributes the category gain TO 'a stronger shared trunk' (MobiWac 06_results.tex L92-94). If Ch.1 is drafted from the PANORAMA logline, the dissertation will deny the existence of the very trunk its headline mechanism credits -- a self-contradiction an examiner reads in one sitting.
      @ storyline/PANORAMA_ptBR.md:27 (section 1 logline) vs GLOSSARY.md:48,50 and articles/[mobiwac]/src/sections/06_results.tex:92-94
      -> Reword the logline to the licensed form: the tasks share THROUGH a cross-attention trunk (exchanging information between per-task streams) rather than by owning hidden layers in common (04_method.tex L30-33 wording). Never draft Ch.1's mechanism sentence from the current PANORAMA phrasing.
  [MAJOR] N2's approved headline is stronger than its source. The claim summary says CBIC's future work 'apontou para arquiteturas e representacoes mais avancadas' (pointed to more advanced architectures AND representations). Verified against CBIC conclusion.tex this session: the future-work sentence names ONLY architecture doors (soft sharing/Cross-Stitch/MoE), advanced optimizers/loss balancing, and task-relatedness analysis. Representation appears in the HYPOTHESIS list ('representation may not have been rich enough'), never in the future-work program. The N2 text itself carries the correct caution ('CBIC opened three doors and we followed the most controllable first', 'nao reescrever a enfase do CBIC depois do fato') -- but the author approved the whole item, and a drafting agent reading the headline rather than the caution will write 'CBIC's future work called for better representations', which the source does not support.
      @ storyline/AVAL_NECESSARIA_2_ptBR.md:N2 (headline vs caution paragraph) vs articles/CBIC___MTL/sections/conclusion.tex (future-work sentence)
      -> Bind drafting to the caution paragraph's form: CBIC hypothesized three causes (one of them representation) and its future work proposed the architecture door; the dissertation took the representation door first as the cheapest controlled test (approved Item 5). Do not attribute a representation program to CBIC's future work.
  [MAJOR] The UW-3 retraction has still not propagated to the governing docs, and drafting is about to start from them. GLOSSARY.md line 64 still asserts 'Ch.3/Ch.4 used sample-stratified splits' as fact, and NORTH_STAR sections 4/6 still instruct the Ch.4 preface to state the weaker-protocol claim -- the exact claim storyline/08 UW-3 retracted to [VERIFY] ('cannot verify firsthand'). PANORAMA section 7 lists the reconciliation as an author action, but at re-review time it has not been executed (verified live in both files this session). Because the spine is what drafting agents 'expand; they do not reinvent', a 2.4 paragraph or Ch.4 preface drafted now will assert an unverified, possibly wrong protocol fact.
      @ GLOSSARY.md:64 and NORTH_STAR.md sections 4 (Ch.4 honesty items) and 6 (Ch.4 preface beat) vs storyline/08_underweighted_sides/underweighted_sides.md UW-3 (line ~124: 'NOT verified')
      -> Before drafting: either verify CoUrb's actual split from its codebase and update all three surfaces at once, or downgrade GLOSSARY:64 and NORTH_STAR sections 4/6 to [VERIFY] and strike the 'say so' preface instruction until verified. This was ordered by the specialist check and remains open.
  [MINOR] N1 leg 2 ('next region is stronger / more present in the literature than category classification') has no fixed comparator and a latent collision with already-drafted prose. Drafted 2.1 verifiably states 'A smaller body of work makes one of them the end target directly' -- i.e., region/category AS ENDS are the minority framing. A loosely drafted leg 2 ('both tasks are well-established literature targets') would contradict 2.1 on the same pages. The [VERIFY] flag itself is correctly load-bearing and correctly held (no citation minted from memory -- good fail-closed discipline), and the author has now restored OpenAlex access (his N1 note; the key is present this session), but PANORAMA section 6 still records OpenAlex as blocked and no owner/checkpoint exists for clearing the [VERIFY] before Ch.1 drafting begins.
      @ storyline/AVAL_NECESSARIA_2_ptBR.md:N1 (leg 2 [VERIFY]) vs fundamentals/2.1_poi_prediction_tasks/2.1_poi_prediction_tasks.tex (closing paragraph, 'A smaller body of work'); stale status at storyline/PANORAMA_ptBR.md section 6
      -> Fix the comparator before searching: the claim to anchor is 'next region and next category as END targets appear in the literature and next region feeds a larger problem family' -- not 'region is a big literature'. Run the now-unblocked OpenAlex sweep as a named pre-drafting task; if anchors are not found, leg 2 is dropped, not softened into vagueness.
  [MINOR] The N3 approval carries an unanswered author question that the package silently drops. In his N3 sign-off the author wrote that he finds the current mechanism evidence 'nao estao muito convincentes', asked for an opinion on running additional experiments (locally or on nespdgpu), and no file in the package answers him. Two honesty risks: (a) the question dangles into drafting and the frame overcompensates in prose for evidence the author himself doubts; (b) if new development-time experiments ARE run, their numbers have no licensing home (the whitelist covers the submitted paper's results only) and could leak into frame text. Also within N3: the author's 'gate de conhecimento' vocabulary maps to no GLOSSARY term and no literal gating mechanism in the model -- the licensed vocabulary is 'the tasks share by exchanging information between per-task streams' plus 'private spatial path' (04_method.tex L30-33), and the freeze-control scope (gain survives within 0.3 at Alabama, Arizona, Florida -- three named datasets, not all six) must travel with the claim.
      @ storyline/AVAL_NECESSARIA_2_ptBR.md:N3 (Author line) -- question unanswered anywhere in storyline/ or fundamentals/; vocabulary source articles/[mobiwac]/src/sections/04_method.tex:30-33, scope source 06_results.tex:92-94
      -> Answer the author explicitly before drafting Ch.6: either (recommended) draft from the licensed freeze-control finding as-is and route the deeper mechanism study to future work (section 6.3, tied to a limitation), or scope any new experiment now with a licensing rule agreed in advance. Translate 'gate' to the paper's own sharing vocabulary; never let the trunk attribution read as measured on all six datasets.
  [NIT] PANORAMA section 2 arc table says CBIC 'previu esse limite antes de medi-lo' (predicted the limit before measuring it). CBIC's intro states a hedged hypothesis ('It is possible that forcing a shared encoder ... could result in negative transfer') and later says results 'lend weight to' it -- 'hypothesized and then supported' is the licensed strength; 'predicted' slightly upgrades it. Same file also carries the stale OpenAlex-blocked status (sections 6 and 8).
      @ storyline/PANORAMA_ptBR.md section 2 (Setup row) vs articles/CBIC___MTL/sections/intro.tex:44-48; stale status sections 6/8
      -> On the next PANORAMA refresh: 'levantou a hipotese e a confirmou para aquela configuracao' instead of 'previu'; update the OpenAlex status. Batch with other meta-doc syncs.

APPROVED-MOVES CHECK:
  (sound) N1 - three-legged task justification (utility, literature presence, convergence with next place)
      Legs 1 and 3 are corpus-grounded and verified (Lim2022/yu2020catdm as means; zhu2022drrgnn/capanema2023poirgnn as ends -- all present in drafted 2.1). Leg 2 is correctly held [VERIFY] and correctly load-bearing: no citation was minted from memory. Two guards for drafting: fix the comparator (see finding 4) so leg 2 does not collide with 2.1's verified 'smaller body of work' sentence, and run the now-restored OpenAlex sweep as a named pre-drafting task.
  (risky) N2 - CBIC's future work is the foundation the later papers execute
      The underlying facts verify (three hypotheses + 'We plan to explore alternative parameter-sharing' confirmed in conclusion.tex), and the item's own caution paragraph states the honest form. But the headline overstates -- CBIC's future work names architecture/optimizer/task-relatedness doors, never a representation program (see finding 2). Draft only from the caution's form: 'CBIC opened three doors; the dissertation took the most controllable first', combined with approved Item 5. The 'MTL reviews endorse that naive MTL does not always help' clause is correctly gated on firsthand confirmation of zhang2021survey/yu2024survey pages before citing.
  (sound) N3 - the win comes from a stronger shared trunk + cross-attention sharing with a private spatial path, NOT from parameters
      Verified verbatim this session: freeze control and 'as a finding, not a hypothesis' at 06_results.tex L92-94; sharing-by-exchange and private spatial path at 04_method.tex L30-33; parameters disclosed as cost ('operational rather than arithmetic', 4.2M vs 1.1M at Alabama) at 04_method.tex L42-49. The three-way split (assert 1 and 2, never 3) is exactly right and the parameters-as-cause refusal is the correct honesty call. Guards: freeze-control scope is AL/AZ/FL, not all six; 'gate' is not licensed vocabulary; the author's embedded experiment question must be answered (finding 5).
  (sound) Item 1 - task change as corollary of the representation thesis (corrected 'unnatural' version)
      The corrected version (pooling escape hatch acknowledged, 'not natural' not 'incoherent') is honest and the fix is not defective. Must always appear WITH the N1 literature/utility legs per the author's adjustment, and the UW-1 concession (no single ablation isolates representation from task homogeneity in the final win) must reach the page, not stay in the storyline.
  (sound) Item 2 - category and region as two coordinates of the next visit; harder, not easier
      The 520-8,501 class counts verified at MobiWac 03_problem.tex:13 and 05_setup.tex; the 7-class contrast is real. The planned re-verification at adaptation (file 02 note) is the right discipline -- keep it.
  (sound) Item 3 - research question answered on two different task pairs
      The two-pair honesty is the arc's spine protection; the CBIC-future-work framing the author added routes through N2 -- subject to the N2 caution (finding 2). The exact answer sentence remains the highest-stakes sentence in the document; UW-4's 'never present as same experiment, opposite result' must bind it.
  (sound) Item 5 - representation door first because cheapest/most controllable; brief, one paragraph
      CBIC's three hypotheses verified in conclusion.tex. Keep the honest asymmetry visible: CBIC's future work suggested the ARCHITECTURE door; the dissertation chose differently and says why. One paragraph, as the author ruled.
  (risky) Item 6 - CoUrb isolates representation, does not revisit MTL-vs-single-task (author: brief and judicious)
      The claim itself is verified firsthand (UW-2: MTLNet is CoUrb's only baseline, zero single-task runs). The risk is the author's brevity instruction: this boundary is the load-bearing protection of the arc's weakest link, and 'breve e com muito criterio' must not shrink it below one explicit sentence in the Ch.4 preface. If brevity deletes the boundary, a reader concludes CoUrb proved MTL works -- the exact failure Item 6 exists to prevent. Draft it short but never implicit.
  (sound) Item 7 - negative-transfer reversal named in the closing, with restored scope
      The pass-2 scope restoration (4 seeds, 3/6 datasets, development-time, earlier data preparation, directional-only, 'sharing stopped hurting' not 'tasks teach each other') matches 02_related.tex L89-94 verbatim. The fix is not defective. The scope must travel into every frame rendering -- compression passes are where it will die.
  (sound) Item 8 - honest arc as the Introduction's structural spine
      Consistent with NORTH_STAR section 6; highest-leverage approved move. Only guard: the arc paragraph must carry the task-pair acknowledgment (Items 1-3) and the two-factor resolution, and must not inherit the PANORAMA trunk-denial phrasing (finding 1).
  (sound) Item 9 - recap subsection CoUrb -> MobiWac at the head of Ch.5
      Verified need (MobiWac section 2 cites CBIC but never CoUrb/ST-MTLNet). Follows the Viegas precedent. Content must be real (what CoUrb established and forced), not template transition prose.
  (sound) Item 10 resolution - no bridge table; recaps carry the logic; lineage table stays
      Evidence-based resolution (Viegas exemplar uses recap subsections, not tables) and it respects the author's repetition concern. Author confirmed. No honesty exposure.
  (sound) Item 11 - motivate beyond mobility, illustration not demonstrated capability
      The guard is exactly right: 'next region is the kind of prediction that supports resource allocation [cite]' as illustration, never 'our model improves urban planning'. External anchors (traffic control etc.) correctly gated on opened sources; the arXiv crowd-flow conflation refusal was the correct fail-closed call. Traffic-control remains uncited until an anchor is opened.

NARRATIVE QUALITY: Yes -- this is now a good narrative, and more importantly it is an honest one that got MORE honest under pressure: the three-changes-at-once problem was named rather than buried, the corollary was weakened when a reviewer showed the pooling escape hatch, the cosine number got its scope back, and nobody minted a citation when the search came up empty. The approved claims are, with one exception (N2's headline), no stronger than their sources, and the whitelist discipline held in every piece of real prose I audited. What the package has NOT done is keep its own summary layer synchronized with its rulings: the PANORAMA logline contradicts the trunk attribution it elsewhere celebrates, and two governing docs still assert a fact the review itself retracted. The story is ready; the paper trail feeding the drafting agents is not, and in a fail-closed pipeline the paper trail IS the story.
TOP PRIORITY BEFORE DRAFTING: Synchronize the three governance surfaces before any frame sentence is written: (1) fix the PANORAMA logline so it stops denying the shared trunk that the freeze-control finding credits (share THROUGH a cross-attention trunk, not 'instead of a common trunk'); (2) resolve the CoUrb-protocol collision -- verify the split from the CoUrb codebase or downgrade GLOSSARY:64 and NORTH_STAR sections 4/6 to [VERIFY] and strike the preface instruction; (3) bind N2 drafting to its caution paragraph, not its headline (CBIC's future work proposed the architecture door; it did not propose a representation program). All three are one-session fixes and all three sit directly upstream of Ch.1/Ch.4 drafting.

==============================================================================================
### Banca simulator — ready_with_fixes
HEADLINE: The narrative now survives Q4/Q5/Q19/Q20/Q22 on its merits -- the three-legged task defense plus the N2 foundation framing and the N3 freeze-control mechanism are exactly what a banca rewards -- but the approved moves live only in the storyline sign-off documents while the spine the drafting agents will expand (NORTH_STAR SS4/SS6, GLOSSARY) is stale on two points, and the one question the package still cannot answer well is the capacity-matched dedicated baseline: 'se o ganho vem do tronco e nao da interacao entre tarefas, um dedicado com a mesma capacidade nao recuperaria o mesmo ganho?'

OVERLOOKED:
  [BLOCKER] The UW-3 governance collision is still live at the moment drafting begins. NORTH_STAR:139 ('split is stratified by sample, not user-disjoint (weaker than Ch.5's protocol -- say so...)') and NORTH_STAR:262 ('protocol weaker than Ch.5's (sample-stratified split)') and GLOSSARY.md:64 ('Ch.3/Ch.4 used sample-stratified splits') all still assert as settled fact the exact claim storyline/08 UW-3 retracted to [VERIFY]. The spine is what drafting agents 'expand; they do not reinvent' -- a Ch.4 preface written tomorrow will state an unverified, possibly wrong, protocol claim as fact, and 2.5:32 meanwhile sells user-disjoint CV as the dissertation-wide protocol when it is Ch.5's only. The specialist check flagged this as author-action on 2026-07-21; verified today it has not landed, and its window closes when drafting starts.
      @ NORTH_STAR.md:139 and :262; GLOSSARY.md:64; vs storyline/08_underweighted_sides UW-3; fundamentals/2.5_relevance/2.5_relevance.tex:32
      -> Before any Ch.4/preface drafting: confirm CoUrb's actual split from its codebase, or downgrade NORTH_STAR SS4/SS6 and GLOSSARY to [VERIFY] and scope 2.5's user-disjoint sentence to Ch.5. Either resolution takes minutes; drafting from the stale spine costs a gate failure.
  [MAJOR] The spine was never synchronized with the approved moves. NORTH_STAR SS6 is the G0 outline drafting agents expand, and it predates the entire sign-off round: its Ch.1 beats carry no task-pair acknowledgment (items 1-3/N1/N2), its Ch.6 limitations list (Gowalla vintage, taxonomy, transductive caveat, no next-place, single non-U.S. city) omits the approved SS3.4 concession ('no single controlled ablation isolates representation from task-homogeneity in the final win'), and its Ch.6 SS6.4 beats omit the N3 why-MTL-wins story (freeze control, cross-attention gate, parameters-as-cost). The approved narrative exists only in AVAL_NECESSARIA_*.md author lines and storyline files; an agent obeying the 'expand the spine' rule will draft the pre-sign-off narrative.
      @ NORTH_STAR.md SS6 (Ch.1 beats 4-6, Ch.6 beats) vs storyline/AVAL_NECESSARIA_ptBR.md + AVAL_NECESSARIA_2_ptBR.md author decisions; storyline/02_task_choice_endorsement SS3.4
      -> One consolidated spine update (or a mandatory addendum file named inside NORTH_STAR SS6) folding in: the three-legged task defense, the N2 CBIC-future-work framing, the N3 mechanism story with its honesty boundary, and the SS3.4 concession added to the Ch.6 limitations list.
  [MAJOR] The author's direct question at the end of N3 is unanswered anywhere in the package, and it points at the arc's real residual weakness. He wrote that the current experiments/arguments on WHERE the improvement comes from 'nao estao muito convincentes' and asked for an opinion and possibly new experiments (local or nespdgpu). No file responds. The package's own N3 text names the fatal question ('entao e so deixar o modelo de tarefa unica maior?') and says the dissertation does not answer it. The freeze control shows the gain is a trunk effect, and the ~4.2M vs ~1.1M disclosure is honest -- but honesty about the confound is not a defense against the capacity-matched dedicated baseline question, which is the one arguicao item the package cannot currently answer well.
      @ storyline/AVAL_NECESSARIA_2_ptBR.md N3, final 'Author:' paragraph; storyline/06_honesty_under_pressure (F3); 10_specialist_check MTL findings
      -> Decide before drafting, not after: (a) run or schedule a capacity-matched dedicated single-task control (the author offered nespdgpu), or (b) commit to a Ch.6 limitation + future-work item conceding it, written from the SS3.4 template. Option (b) is defensible at a master's; leaving the question undecided is not.
  [MAJOR] N1 leg 2 -- 'next region is stronger / more present in the literature than category classification' -- is a comparative bibliometric claim that may be unverifiable in the shape approved. It is currently [VERIFY] pending an OpenAlex sweep, but no single opened paper can ground 'more present in the literature'; that claim shape needs either a survey that says it or a citation-count analysis the dissertation would then own and defend. The package has no fallback formulation, so drafting either stalls on leg 2 or a drafting agent smooths it into an unanchored superlative.
      @ storyline/AVAL_NECESSARIA_2_ptBR.md N1 (leg 2 + author note granting OpenAlex/CAFe access)
      -> Pre-approve a fallback now: 'both are established end targets [cites], and next region feeds a broader family of downstream problems [cites]' -- a conjunction of verifiable existentials instead of an unverifiable comparative. Upgrade to the comparative only if a survey sentence is actually opened that supports it.
  [MINOR] The page-level fixes the specialist check assigned to the author have not landed and nothing tracks them into the drafting wave: 2.1 still scopes the 93% predictability as 'the reference point against which any predictive model should be read' (lines 14-19, verified today); 2.5 still asserts the MobiWac win with no 'submitted, under review' marker anywhere in the file (grep confirms, Q20 exposure); the map-partition legitimacy sentence is still absent from 2.1/2.4; the 'next category' vs 'next-POI prediction' name mapping (Q22) has no landed seam sentence. Individually small; collectively they are the sloppiness pattern that flips an examiner into hypercritical mode at exactly the chapter where first impressions form.
      @ fundamentals/2.1_poi_prediction_tasks/2.1_poi_prediction_tasks.tex:14-19; fundamentals/2.5_relevance/2.5_relevance.tex (no status marker); 10_specialist_check action items 3-6
      -> Convert the specialist-check action list into a checklist artifact the drafting wave must clear per section (the DRAFT_LEDGER is the natural home), so the fixes ride the first edit pass instead of resurfacing at the gate.
  [MINOR] A latent contradiction sits inside an approved author note. In Item 2 the author wrote that the text could 'dizer que essas tarefas sao mais simples' while also endorsing the 'not trivial' cardinality fact. If a drafting agent renders 'simpler' literally, it collides head-on with the approved disarming argument that the task set got HARDER (region: 520-8,501 classes vs seven for the dropped static task) and hands the banca the 'you chose easier tasks' opening the whole defense exists to close.
      @ storyline/AVAL_NECESSARIA_ptBR.md Item 2, 'Author:' line; vs 02_task_choice_endorsement SS2.4
      -> Fix the rendering rule now: the tasks are 'coarser-grained than next place' (fewer classes than tens of thousands of venues), never 'simpler' or 'easier'; the second task got harder, not easier. One line in the drafting guidance prevents the collision.

APPROVED-MOVES CHECK:
  (sound) Item 1 + N1 -- task change as corollary, plus literature/utility legs
      The three-legged structure (utility, literature presence, convergence-to-next-place) is the strongest possible answer to Q5, and the corrected 'unnatural, not incoherent' wording holds. Leg 2's comparative claim is the weak joint (see MAJOR finding); legs 1 and 3 can be drafted today from the corpus.
  (sound) Item 2 -- category and region as two coordinates of the next visit
      Well anchored (Lim2022, yu2020catdm as means; zhu2022drrgnn, capanema2023poirgnn as ends) and already executed in 2.1. Guard the author's 'mais simples' phrasing against the 'not easier' fact (see MINOR finding).
  (sound) Item 3 + N2 -- the two-pairs answer framed through CBIC's own future work
      This is the move that defuses Q20's cousin ('which version do I believe?') -- the null becomes a foundation the paper itself announced. Respect N2's own guard: CBIC blamed task dissimilarity substantially, so the honest line is 'CBIC opened three doors and we took the most controllable first,' never 'CBIC already knew it was the representation.' zhang2021survey/yu2024survey pages must be opened before the 'naive MTL does not always help' sentence cites them.
  (sound) Item 4 -- why the check-in level specifically (the per-place-vector ceiling)
      Closes the 'rabbit from the hat' gap between diagnosis and resolution; well supported by MobiWac SS2.1.
  (sound) Item 5 -- representation before architecture, one paragraph
      The author's 'one paragraph, as insurance' sizing is right; it converts a loose thread into a demonstration of method under Q16.
  (risky) Item 6 -- CoUrb isolates representation, stated briefly
      The author's constraint ('breve e com muito criterio' to protect reading flow) is in tension with the POI expert's demand that the boundary be explicit in the Ch.4 preface. Reconcile as: one plain declarative sentence in the preface ('CoUrb compares two multi-task models; it does not revisit MTL versus single-task'), nothing more. Brief must not become omitted -- an examiner opens CoUrb's table in thirty seconds.
  (risky) Item 7 + N3 -- negative-transfer reversal named, plus why MTL wins without positive transfer
      Sound as scoped (freeze control -> stronger shared trunk; cross-attention with private spatial path as the 'gate'; parameters disclosed as cost, never credited). The risk is not the framing but the residue: the capacity-matched dedicated baseline question remains unanswered and the author himself flagged the evidence as not yet convincing. The cosine number must travel with its full scope verbatim (4 seeds, 3/6 datasets, development-time, earlier data preparation, directional only).
  (sound) Item 8 -- honest arc as the structural spine of the Introduction
      The highest-leverage move; it is the direct answer to Q19 and the correction-trail framing is what the persona's own question bank rewards under Q20.
  (sound) Item 9 -- CoUrb -> MobiWac recap subsection at the head of Ch.5
      Verified need: MobiWac SS2 does not cite ST-MTLNet, so this is the only bridge at the arc's weakest seam. Follows the Viegas precedent.
  (sound) Item 10 resolved -- no bridge table; recaps carry the logic
      Correct resolution: the closest precedent (same advisor, same format) uses recap subsections, and the model-lineage table already covers the model level without competing with the text.
  (risky) Item 11 + N1 -- motivate beyond mobility, as illustration never capability
      The frame ('next region is the kind of prediction that supports resource allocation [cite]') is right and the fail-closed discipline so far is exemplary. Risky only because every external anchor is still unopened; the traffic-control example in particular must not enter prose before a source is opened, and 'our model improves urban planning' remains the forbidden rendering.

NARRATIVE QUALITY: Yes -- this is now a good narrative, and I say that as the examiner it was built to survive. A published null, its controlled diagnosis, and a resolution whose verbs are bound to tests is the correction-trail structure my question bank explicitly rewards, and the task-pair confound, which was the kill-shot, now has a layered defense (corollary + literature/utility + convergence + the SS3.4 concession) that turns Q5 from an ambush into the candidate's best five minutes. But my verdict forms from the written text, not the reviewer's notes: the disarming content still lives in sign-off documents while the pages and the spine the drafters will expand do not yet carry it, and the one probe I would still press -- the capacity-matched dedicated baseline -- currently has no answer beyond an honest disclosure. Fix the transport and decide that one answer, and this defends as aprovado com correcoes menores.
TOP PRIORITY BEFORE DRAFTING: Synchronize the governing documents with what the author approved, before any drafting agent expands them: (1) resolve or downgrade the CoUrb-protocol assertion in NORTH_STAR:139/:262 and GLOSSARY:64 (the UW-3 collision -- the only true blocker); (2) fold the approved moves (three-legged task defense, N2 framing, N3 mechanism story, SS3.4 concession into the Ch.6 limitations list) into NORTH_STAR SS6 or a mandatory addendum. Then decide the answer to the one question the package cannot yet answer well, which I would pose verbatim: 'O controle de congelamento mostra que o ganho de categoria vem de um tronco compartilhado mais forte, nao da tarefa de regiao ensinando a de categoria; e o senhor divulga que o modelo conjunto tem cerca de 4,2 milhoes de parametros contra 1,1 milhao de um dedicado. Se o ganho vem do tronco, e nao da interacao entre as tarefas, um modelo dedicado de tarefa unica com a mesma capacidade nao recuperaria o mesmo ganho? O senhor rodou esse baseline -- e, se nao, o que resta de multitarefa na sua vitoria?' Either the capacity-matched control gets run (nespdgpu was offered) or the concession gets written into Ch.6 from the SS3.4 template -- but the choice must be made now, because it shapes how Ch.5's discussion and Ch.6 are drafted.

==============================================================================================
### Adversarial advisor — ready_with_fixes
HEADLINE: The narrative package is coherent, honest, and author-owned, but two governance defects must be repaired before any drafting agent expands the spine: the CoUrb-protocol claim retracted to [VERIFY] still stands as settled fact in NORTH_STAR and GLOSSARY (a preface drafted from the spine will assert an unverified claim), and the approved moves N2+Item 8, executed carelessly, over-smooth the honest null into a scripted journey.

OVERLOOKED:
  [BLOCKER] The UW-3 retraction never propagated to the governing docs. NORTH_STAR:139 still instructs the Ch.4 preface to state 'split is stratified by sample, not user-disjoint (weaker than Ch.5's protocol -- say so, it strengthens the arc)' and NORTH_STAR:262 repeats it; GLOSSARY.md:64 asserts 'Ch.3/Ch.4 used sample-stratified splits' as registry fact. storyline/08 UW-3 retracted exactly this claim to [VERIFY] ('I cannot verify this firsthand'). NORTH_STAR SS6 is by its own words what drafting agents 'expand; they do not reinvent' -- so the moment drafting begins, a fail-closed-retracted claim re-enters as fact. Compounding: 2.5_relevance.tex:32 already sells user-disjoint CV as THE dissertation protocol when it is only Ch.5's. This was flagged by two specialists and is recorded as 'author must action' -- but it has NOT been actioned, and this re-review is the last gate before drafting.
      @ NORTH_STAR.md:139, NORTH_STAR.md:262, GLOSSARY.md:64, fundamentals/2.5_relevance/2.5_relevance.tex:32; retraction at storyline/08_underweighted_sides/underweighted_sides.md UW-3
      -> Before any drafting: either confirm CoUrb's actual split from its codebase/judge_feedback and restore the claim with a source note, or edit NORTH_STAR:139/:262 and GLOSSARY:64 to carry [VERIFY] and strike the 'say so' instruction. Scope 2.5's user-disjoint sentence to Ch.5 at the same time.
  [MAJOR] Interaction between approved moves N2 and Item 8 (the highest-damage careless execution). N2 frames the task-pair change as 'part of a progression CBIC itself announced'; Item 8 makes the arc the Introduction's structural spine; the protect list separately celebrates CBIC as a 'predicted null' (its intro hypothesized the limitation). Stacked without care, these three produce a teleological script -- 'we knew all along' -- which (a) contradicts honesty flag F4 (CBIC attributed the null substantially to task dissimilarity, and its future work pointed first at alternative SHARING architectures, not at representations and never at check-in-level representations or a region task), (b) violates the time-capsule rule (CBIC's conclusion is of-the-time), and (c) destroys the arc's core asset, which is that the null was a genuine finding, not a planned step. N2's own caution paragraph says this, but the caution lives in a PT meta-doc a drafting agent may skim past once it sees 'Author: Approved'.
      @ AVAL_NECESSARIA_2_ptBR.md N2 (caution paragraph) x AVAL_NECESSARIA_ptBR.md Item 8; honesty bound at storyline/06_honesty_under_pressure/honesty_flags.md F4; NORTH_STAR SS3 time-capsule rule
      -> Guardrail sentence for the drafting brief: 'CBIC anticipated that naive hard sharing might face limitations and proposed exploring alternative parameter sharing; it did NOT predict the representation diagnosis, the check-in level, or the region task -- write the bridge as three doors opened, the most controllable walked first, never as foresight.'
  [MAJOR] N3's author reply embeds an unanswered question and a live experiment offer that nobody has resolved. The author wrote that today's evidence for WHY the joint model wins feels 'nao muito convincente', asked for an opinion, and offered to run new experiments (locally or on nespdgpu). This is an open fork in the record: if new experiments run, their numbers cannot enter Ch.5 (a version-of-record under review at MobiWac) and would need a sanctioned home (frame discussion or appendix, with their own fact-gate), and the Conclusion's SS6.4 paragraph would be drafted twice. If they do not run, someone must tell the author the freeze control + cross-attention account is the defensible ceiling of the current evidence. Drafting SS6.4 while this hangs risks wasted or contradicted prose.
      @ AVAL_NECESSARIA_2_ptBR.md N3, final 'Author:' paragraph
      -> Answer the author before Ch.6 SS6.4 is drafted. If experiments proceed, pre-rule their venue (frame/appendix as post-submission analysis, never inside Ch.5's record) and gate their claims like any new number.
  [MAJOR] The author's Item 1 adjustment quietly re-weights the task-choice defense toward its only UNVERIFIED leg. He judged the corollary ('changed tasks because the representation changed') as 'not much force alone' and asked the literature/utility argument to lead -- but N1 leg 2 ('next region is more present/stronger in the literature than category classification') still has zero opened external anchors ([VERIFY], OpenAlex was down; now restored but the search has not run), and the 'traffic control' illustration has none either. A drafting agent following the author's emphasis will lead with the unverified comparative claim and demote the verified corollary -- inverting the evidence order. The corollary is also what all four specialists say must land on the page in 2.1/2.5; the author's preference for a different LEAD does not cancel that landing.
      @ AVAL_NECESSARIA_ptBR.md Item 1 'Author:' line x AVAL_NECESSARIA_2_ptBR.md N1 (leg 2 [VERIFY]); specialist convergence at storyline/10_specialist_check/specialist_check.md action item 1
      -> Drafting order rule: legs 1 and 3 plus the corollary (verified, sign-off complete) are draftable now, and the corollary sentence must still reach 2.1 and 2.5's arc paragraph; leg 2 and any traffic-control illustration enter only after sources are opened and verified. Never write 'more studied than' from memory.
  [MINOR] The author's Item 6 ruling ('brief, with much criterion... revealing this may raise questions for a naive reader and break the reading flow') can be read by a drafting agent as license to OMIT the CoUrb boundary sentence. It is not: UW-2 is a MAJOR finding (without the boundary, momentum lets a reader conclude CoUrb showed MTL works, which its own tables refute in thirty seconds), and the drafted 2.5 only survives because it phrases CoUrb as a representation question. The ruling constrains length, not existence.
      @ AVAL_NECESSARIA_ptBR.md Item 6 'Author:' line x storyline/08_underweighted_sides/underweighted_sides.md UW-2
      -> Guardrail: the Ch.4 preface carries exactly one boundary sentence ('this chapter isolates the representation effect; both compared models are multi-task; the MTL-versus-single-task question returns in Chapter 5') -- one sentence satisfies the author's brevity ruling; zero sentences violates UW-2.
  [MINOR] The drafting entry point (PANORAMA SS7's chapter map) carries only the approved items; it omits the standing law-level rulings a Ch.1 drafter needs -- F3 above all (the Introduction beat still promises 'shared structure and lower cost', NORTH_STAR:222, while CBIC cost more and MobiWac's joint model is ~4.2M vs 1.1M params; the redefinition to operational simplicity must be narrated, not hidden), plus F4, and the eight-item specialist fix list for the already-drafted 2.1/2.5 (93% scoping, under-review marker, map-partition sentence, name-mapping seam, stale 2.3 citation map). None of these are applied or assigned; a drafter working from PANORAMA + the AVAL files alone will miss them.
      @ PANORAMA_ptBR.md SS7 vs storyline/06_honesty_under_pressure/honesty_flags.md F3-F4 and storyline/10_specialist_check/specialist_check.md action items 3-8; NORTH_STAR.md:222
      -> Assemble one per-chapter drafting brief that unions the approved items, the honesty flags (F1-F4), and the Ch.2 fix list; make applying the Ch.2 fixes the first work order of the drafting wave, before new prose.

APPROVED-MOVES CHECK:
  (risky) Item 1 - task change as corollary of the representation thesis (approved with adjustment)
      Sound in substance (the 'unnatural' correction holds; never revert to 'incoherent'), but the author's adjustment re-weights toward the unverified literature leg -- see overlooked #4. The corollary must still land in 2.1/2.5 regardless of what leads.
  (sound) Item 2 - category and region as two coordinates of the next visit (approved)
      Keep the 'harder, not easier' anchor; the 520-8,501 region counts re-verify against the MobiWac source at adaptation before entering prose.
  (risky) Item 3 - RQ answered on two different task pairs (approved with adjustment)
      The two-pair honesty is right; the adjustment routes it through CBIC's future work (N2), which carries the scripted-journey risk -- see overlooked #2. Never phrase as 'same experiment, opposite result' nor as foresight.
  (sound) Item 4 - why check-in level specifically, the per-place-vector ceiling (approved)
      Keep the universal scoped: 'every PLACE-LEVEL representation shares the ceiling' is defensible; 'the only possible fix' unscoped is not. State it as the direction that removes THIS limitation.
  (sound) Item 5 - why representation before architecture, three doors (approved, one paragraph)
      Respect the author's one-paragraph cap; the 'cheapest, most controllable first' reasoning is honest and closes thread T7.
  (conflicts) Item 6 - CoUrb isolates representation, does not revisit MTL-vs-single-task (approved with adjustment: brief)
      Author's brevity ruling is in tension with UW-2's MAJOR status; resolution: one mandatory boundary sentence in the Ch.4 preface -- brevity yes, omission no. See overlooked #5.
  (sound) Item 7 - name the negative-transfer reversal at the close (approved with adjustment)
      Only with the restored scope traveling verbatim into English: +0.001, four seeds, three of six datasets, development-time, earlier data preparation, this pair not a general rule; 'directional' qualifier mandatory; 'sharing stopped hurting', never 'the tasks teach each other'.
  (risky) Item 8 - honest arc as the Introduction's structural spine (approved)
      The highest-leverage move and the one that pairs worst with N2 if drafted carelessly -- the null must stay a genuine of-its-time finding, not act one of a script. See overlooked #2.
  (sound) Item 9 - recap subsection bridging CoUrb to MobiWac at Ch.5 head (approved)
      The only seam with no native bridge; recap by name, carry real content, complement (not replace) CoUrb's native citation of MTLnet.
  (sound) Item 10 resolution - no bridge table; recap subsections carry the logic (approved)
      Matches the Viegas precedent; the model-lineage table stays. No loss: the 'what it forced' logic is recoverable from Items 5/6/9 plus the arc paragraph.
  (risky) Item 11 - motivate the tasks beyond mobility (approved with adjustment)
      Illustration-only rule is the honesty boundary: 'next region is the kind of prediction that supports X [cite]', never a demonstrated capability. Traffic control and any comparative breadth claim currently have zero opened anchors; the crowd-flow conflation trap (ST-ResNet-type aggregate density is a different task) is documented and must reach the drafting brief.
  (risky) N1 - three-legged task justification: utility, literature presence, convergence with next place (approved; leg 2 gated)
      Legs 1 and 3 draftable now; leg 2 ('region stronger in the literature than category') stays [VERIFY] until external sources are opened -- OpenAlex is restored, so run the search BEFORE drafting the problematization, not after.
  (risky) N2 - CBIC connects to MobiWac through its own future work (approved)
      The single approved move where careless execution does the most damage: CBIC's future work named alternative sharing architectures and a rudimentary-MTL caveat -- it did not call for check-in representations or a region task. Quote it for what it says; keep F4's task-dissimilarity emphasis intact.
  (risky) N3 - why MTL wins without gradient-level positive transfer: stronger trunk + cross-attention gating, never parameters (approved)
      The explanation hierarchy is right (freeze control proves the trunk account; cross-attention + private spatial path is the design rationale; parameters are disclosed cost, never cause) -- but the author's reply embeds an unresolved experiment question that must be answered before SS6.4 is drafted. See overlooked #3.
  (sound) Cross-cutting law (two-factor resolution, verbs bound to tests, AZ never upgraded, time-indexing)
      Held everywhere I checked, including the drafted 2.5; the one soft spot is 2.5's 'unlocks for' syntax subordinating the sharing topology -- echo the spine's co-equal 'and' when 2.5 is retouched.

NARRATIVE QUALITY: Yes -- this is now a good narrative, and a rare one: a published null, a controlled diagnosis, and a two-factor resolution, with the arc's most dangerous confound (the task-pair change) converted into its most satisfying beat rather than smoothed over. The governance around it is stronger than most defended dissertations I have gated: verbs bound to tests survived four independent specialist lenses, and the package corrected itself twice under pressure instead of defending its own errors. My residual worry is not the story but its transmission: the approvals live in Portuguese meta-docs whose caution paragraphs a drafting agent can skip once it sees 'Approved', and two governing files still carry a claim the package itself retracted. Fix the transmission and the narrative will hold under arguicao.
TOP PRIORITY BEFORE DRAFTING: Reconcile the CoUrb-protocol collision (NORTH_STAR:139/:262 and GLOSSARY:64 vs UW-3) -- verify the split from the CoUrb codebase or downgrade both governing docs to [VERIFY] and scope 2.5:32's user-disjoint sentence to Ch.5. It is the only defect that turns a drafting agent's obedience to the spine into a fact-gate failure, and every other fix can ride the drafting wave; this one must precede it.

==============================================================================================
### Excellence assessor — ready_with_fixes
HEADLINE: The narrative is now genuinely good and within reach of outstanding: the arc is real, the task-pair confound has been converted into the most satisfying beat, and the honesty machinery held under four specialist lenses. What still separates this plan from an outstanding coletanea is not the story but its bookkeeping: the spine document (NORTH_STAR/GLOSSARY) lags the corrections the package itself made, one author question is unanswered, and two intro-conclusion threads (the cost promise, the confound limitation) have no owner. All are cheap fixes relative to their leverage.

OVERLOOKED:
  [MAJOR] The author's open question inside his N3 approval has no recorded answer anywhere in the package. He wrote that the mechanism evidence ('where does the MTL improvement come from') feels 'nao muito convincentes', asked for an opinion, and offered local or nespdgpu experiments. The package treats N3 as closed ('Approved') and moves on. This is the single highest excellence-leverage item left: the mechanism story (freeze control + cross-attention with private spatial path) is the dissertation's originality and critical-self-assessment core (rubric dims 6-7), and it currently ends on the author's own doubt. Grep confirms no reply, plan entry, or ledger note exists.
      @ storyline/AVAL_NECESSARIA_2_ptBR.md, N3 'Author:' line (~L152-158); no counterpart anywhere in storyline/, fundamentals/, or PLAN
      -> Answer it explicitly before Ch.5/6 drafting: either (a) scope a small, targeted mechanism experiment (e.g. extend the freeze control symmetrically, or a fixed-pair ablation - which would also discharge the 02 sec.3.4 concession), or (b) rule the existing freeze-control evidence sufficient, state its bounds, and route the rest to future work. Record the decision; do not let drafting proceed on an evidence base the author himself distrusts.
  [MAJOR] The spine has not absorbed the package's own corrections, and drafting agents are instructed to expand the spine, not reinvent it. NORTH_STAR still asserts the CoUrb sample-stratified protocol as settled fact in two places, and GLOSSARY sec.3 asserts 'Ch.3/Ch.4 used sample-stratified splits' - the exact claim pass-2 retracted to [VERIFY] (UW-3). The specialist check flagged this as author action; at this re-review it is still on the page. A Ch.4 preface faithfully drafted from the spine will state an unverified, possibly false, protocol claim as fact.
      @ NORTH_STAR.md:139 (sec.4 Ch.4) and :262 (sec.6 Ch.4 preface); GLOSSARY.md:64 - vs storyline/08_underweighted_sides/underweighted_sides.md UW-3
      -> Before any frame drafting: verify CoUrb's actual split from its codebase (or slides/judge_feedback.md) and then either restore the beat with a source, or strike the 'say so' instruction from NORTH_STAR sec.4/sec.6 and fix GLOSSARY:64. The suspended G-13 stays suspended until then.
  [MAJOR] The intro-conclusion loop has one thread that closes only by an unnarrated redefinition, and no approved move owns the narration. NORTH_STAR sec.6.1 beat 2 still has the Introduction promise 'MTL promises shared structure and lower cost'; the delivered arc never produces lower cost (CBIC costs more; MobiWac's joint model is larger than the two dedicated models combined, ~4.2M vs 1.1M at Alabama) and the Conclusion closes as 'one forward pass, two predictions' - operational simplicity, not savings. Honesty flag F3 rules the redefinition must be narrated, but it appears in none of the 11 signed items, none of N1-N3, and no G-recommendation number. A banca member will compute the parameter ratio; the excellence rubric's loop test fails exactly here if the beat is drafted as written.
      @ NORTH_STAR.md sec.6.1 beat 2 vs sec.6.4 final remarks; storyline/06_honesty_under_pressure/honesty_flags.md F3; storyline/03_cohesion_and_threads/cohesion_and_threads.md T4
      -> Amend spine beat 2 so the Introduction promises the operational wish (one model, one forward pass, one artifact to maintain) rather than 'lower cost', or add an explicit conclusion beat that narrates the redefinition ('the wish was efficiency; what the arc delivers is operational simplicity at higher compute, disclosed'). One sentence each end; closes T4 honestly.
  [MAJOR] The confound concession has no home in the spine. File 02 sec.3.4 rules that the frame must concede, somewhere, that no single controlled ablation separates representation+topology from task-pair homogeneity in the final win (CoUrb is the fixed-pair control for the diagnosis, not for the joint win). The POI expert repeats it ('carry sec.3.4's concession into a Ch.2 scope note or Ch.6 limitation'). But NORTH_STAR sec.6.4's limitations list predates the task-pair discovery (dataset vintage, taxonomy, transductive caveat, no next-place, single-city) and was never updated; none of the signed items places the concession. Outstanding dissertations name their own confound in the limitations (Lovitts/Mullins-Kiley critical self-assessment); an examiner who finds it before the text does gets the kill-shot back.
      @ NORTH_STAR.md sec.6.4 limitations beat - vs storyline/02_task_choice_endorsement/task_choice_endorsement.md sec.3.4 and sec.4 step 6; specialist_check.md POI expert finding 4
      -> Add one limitation bullet to the sec.6.4 beat (and optionally one Ch.2 scope sentence), tied 1:1 to a future-work item: the fixed-pair ablation under the check-in representation. Note this future-work item is also a candidate answer to the N3 open question - the two findings can be resolved by one decision.
  [MINOR] Rubric dimensions 8 (reproducibility and artifacts) and 10 (external validation / products trail) are unplanned in the narrative package. Spine beat 8 names 'Software (MTLnet + Check2HGI + reproducible pipeline, repo footnote)' but nothing in the storyline, the approved moves, or the Ch.2 plans decides where the artifact inventory lives, whether code/seeds/configs are released, or where a committee finds the products list (2 published DOIs + 1 under review + code + the benchmark protocol - the SBC CTD / CAPES criterion III shape). For a dissertation whose empirical protocol is a headline contribution, this is the cheapest unclaimed excellence surface left.
      @ NORTH_STAR.md sec.6.1 beat 8 (only mention); absent from storyline/07 recommendations and both AVAL rounds
      -> One author decision + one pattern: a short artifacts/products appendix or per-chapter repository footnotes (seeds, configs, split definitions). Low cost, direct award-lens value; does not touch any claim.
  [MINOR] Item 6's approval carries an instruction ('breve e com muito criterio', to protect reading flow) but no content floor. The CoUrb boundary sentence is what prevents the exact momentum-trap UW-2 names (a reader concluding 'CoUrb showed MTL works' - falsifiable in thirty seconds from CoUrb's own table). An over-cautious drafting agent honoring 'brief, with criterion' can shrink the move until the boundary vanishes, reopening the trap the item exists to close.
      @ AVAL_NECESSARIA_ptBR.md Item 6 'Author:' decision; storyline/08 UW-2
      -> Fix the minimum in the drafting instruction: the Ch.4 preface/recap must contain, at minimum, one sentence with the precise boundary ('CoUrb isolates the representation effect with MTLNet as its only baseline; it does not revisit the MTL-versus-single-task verdict, which Chapter 5 reopens'). Brevity applies to elaboration, not to the boundary itself.

APPROVED-MOVES CHECK:
  (sound) Item 1 + N1 - task change as corollary, plus the three-legged literature/utility defense
      The corrected 'unnatural, not incoherent' version is the honest form, and the author's utility/literature leg makes the defense positive rather than defensive - exactly the outstanding-grade shape. The split (draft legs 1 and 3 now; leg 2 only after an opened external anchor) is correctly fail-closed. Trap to hold: leg 2's comparative claim ('next region is stronger in the literature than static category classification') must be dropped, not softened, if no anchor verifies.
  (sound) Item 2 - category and region as two coordinates of the same next visit, promoted from means to ends
      Grounded in verified corpus keys (Lim2022, yu2020catdm, zhu2022drrgnn, capanema2023poirgnn); the drafted 2.1 already executes the means-to-ends half. The 520-8,501-classes 'not easier' fact is the most disarming line available - keep it wherever the choice is defended, with class counts re-verified at adaptation.
  (sound) Item 3 + N2 - two-pairs answer framed through CBIC's own future work
      Turns the arc's biggest vulnerability into a planned progression, and the caution is correctly recorded: CBIC blamed task dissimilarity substantially, so the bridge is 'CBIC opened three doors', never 'CBIC already knew it was the representation' (F4). The MTL-survey support (zhang2021survey, yu2024survey) still requires firsthand page-level confirmation before citing.
  (sound) Item 4 - why check-in level specifically (the per-place-vector ceiling)
      Repairs the arc's least-motivated joint (the diagnosis-to-resolution jump); without it Check2HGI is a rabbit from a hat. Strongly supported by MobiWac sec.2.1.
  (sound) Item 5 - why representation before architecture (three doors, cheapest first)
      The author's 'one paragraph, as insurance' sizing is right; it closes thread T7 and displays research reasoning - a Mullins-Kiley excellence signal at paragraph cost.
  (risky) Item 6 - CoUrb boundary (isolates representation; silent on MTL-vs-STL), brief per author
      The move itself is necessary and verified (UW-2). The risk is the author's brevity instruction without a stated minimum - see finding 6. Give the drafting agent a one-sentence floor and the risk disappears.
  (risky) Item 7 + N3 - negative-transfer reversal named at the payoff, plus why MTL wins without gradient-level positive transfer
      The content is the best-guarded claim in the package (scope travels with the cosine number; freeze control credits the trunk; 'more parameters' correctly excluded as cause). Risky for a process reason: the author's own closing doubt about the evidence's convincingness is unanswered (finding 1). Resolve that before this beat is drafted, or the section will assert a mechanism story its author does not yet believe.
  (sound) Item 8 - honest arc as the structural spine of the Introduction
      The highest-leverage move in the package, correctly ranked first everywhere. The null-result-as-strength test passes: predicted null, diagnosis, resolution, narrated as a correction trail - protect CBIC's predicted-null framing while executing.
  (sound) Item 9 - recap subsection at the head of Ch.5 (CoUrb to MobiWac)
      Welds the only seam with no native bridge (MobiWac sec.2 never mentions ST-MTLNet). Viegas-precedented. Must carry real content, not template transitions (F8).
  (sound) Item 10 resolution - no bridge table; recaps and the arc paragraph carry the logic
      Correctly decided on the Viegas precedent and the author's repetition concern. Consequence to accept knowingly: the at-a-glance unity device is gone, so the arc paragraph and the two recaps now carry the full 'one dissertation, not three papers' burden - which raises the stakes on findings 2-4 landing in the spine before drafting.
  (sound) Item 11 + N1 - motivate beyond mobility, then narrow to the mobility evaluation setting
      Right shape (illustration, never demonstrated capability). Two open dependencies handled correctly as [VERIFY]: the four CBIC domain citations live in a commented-out block that never passed a citation gate, and the traffic-control example still needs an opened anchor. OpenAlex is restored per the author; run the dedicated sweep before drafting the Ch.1 problematization.

NARRATIVE QUALITY: Yes - this is now a good narrative, and it is close to an outstanding one. It has the thing money cannot buy: a real setup-frustration-insight-payoff arc with a predicted null at its base, and the two rounds of author sign-off have converted its biggest liability (three things changed between the null and the win) into its most intellectually satisfying beat. The remaining distance to outstanding is not story invention but consolidation: the spine the drafting agents will expand still carries three pre-correction sentences (the protocol claim, the lower-cost promise, the pre-confound limitations list), and the mechanism story - the dissertation's claim to originality - currently ends on the author's own unanswered doubt. Fix the spine, answer the N3 question, and plan the products surface, and this plan competes at the level the author asked for.
TOP PRIORITY BEFORE DRAFTING: Reconcile the spine with the package's own corrections in one sitting, because drafting agents expand NORTH_STAR verbatim and every uncorrected spine sentence is a defect scheduled for reproduction: (1) resolve the CoUrb protocol claim (verify the split from the codebase, then fix NORTH_STAR sec.4/sec.6 and GLOSSARY:64); (2) reword sec.6.1 beat 2 so the Introduction does not promise 'lower cost' the arc never delivers; (3) add the fixed-pair-ablation confound concession to the sec.6.4 limitations beat. In the same sitting, answer the author's open N3 question (experiment or explicit sufficiency ruling) - it gates the Ch.5/6 mechanism beats and doubles as the future-work item the new limitation needs.
```

---

## `process/11_full_arc_rereview/full_arc_rereview.md`

# Full-arc re-review — five personas on the complete approved narrative

> **What this is.** The author-requested final pass before drafting: five reviewers (cold reader,
> claim honesty, banca simulator, adversarial advisor, excellence assessor) ran fresh-eyes on the
> COMPLETE package — the spine, all storyline files, both sign-off rounds with the author's inline
> decisions, and the drafted 2.1/2.5 — asking "are we overlooking something, forgetting something;
> is this now a good narrative?"
>
> **The one-line verdict: 5/5 `ready_with_fixes`.** Every persona independently answers "yes, this
> is now a good narrative" — and every persona independently found the same category of defect:
> not the story, but its **transmission**. The approvals lived in the storyline sign-off documents
> while the spine (NORTH_STAR/GLOSSARY) that drafting agents expand still carried pre-correction
> sentences. Most of those are now FIXED (see §2); the remaining items are the author's.

---

## 1. What the five lenses agreed on

**The narrative is good.** From the verdicts: the cold reader — "a genuinely good story that would
carry a cold reader once the frame narrates it"; claim honesty — "an honest one that got MORE
honest under pressure"; the banca — the correction-trail structure its question bank rewards, and
conditional on the fixes "this defends as aprovado com correções menores"; the adversarial
advisor — "a rare one … the arc's most dangerous confound converted into its most satisfying
beat"; excellence — "close to an outstanding one."

**The convergent findings (each found independently by 3–5 personas):**
1. **[BLOCKER] The UW-3 protocol retraction never propagated** to NORTH_STAR:139/:262 and
   GLOSSARY:64 — a Ch.4 preface drafted from the spine would assert an unverified protocol claim.
2. **[MAJOR] The spine predated the sign-offs** — NORTH_STAR §6 carried no task-pair
   acknowledgment, no three-legged defense, no N2/N3 framing, no §3.4 concession in the
   limitations list.
3. **[MAJOR] The author's N3 question was unanswered** — the package treated N3 as closed while
   its "Author:" line contains a direct question and an experiment offer (§3 below).
4. **[MAJOR] The PANORAMA logline contradicted the mechanism** — "via atenção cruzada em vez de um
   tronco comum" denied the shared trunk the freeze control credits.
5. **[MAJOR] The intro's "lower cost" promise (NORTH_STAR §6.1 beat 2)** was never redefined to the
   operational form the arc actually delivers (honesty flag F3 / thread T4).

## 2. Fixed in this pass (governance sync, applied to the repo)

| Fix | Where |
|---|---|
| CoUrb protocol claim downgraded to [VERIFY] with verification path (codebase / judge_feedback) | `NORTH_STAR.md` §4 honesty items + §6 Ch.4 preface beat |
| GLOSSARY protocol note downgraded to [VERIFY] | `GLOSSARY.md` user-disjoint-split row |
| Item 6 one-sentence boundary floor written into the Ch.4 preface beat ("brevity yes, omission no") | `NORTH_STAR.md` §6 Ch.4 preface |
| Intro beat 2 rewritten: operational simplicity promised, F3 guard added (never "lower cost") | `NORTH_STAR.md` §6.1 beat 2 |
| Arc beat 4 extended with the five signed-off additions (task-pair acknowledgment; three-legged defense with leg-2 fallback; corrected corollary; N2 caution-form-only with F4 guard; mechanism-as-hypothesis) | `NORTH_STAR.md` §6.1 beat 4 |
| Ch.6 limitations beat gains the §3.4 confound concession, tied 1:1 to the fixed-pair-ablation future-work item; N3 mechanism beats appended with full scope + licensed vocabulary ("gate" translated) | `NORTH_STAR.md` §6.4 beats |
| PANORAMA logline corrected (shares THROUGH a cross-attention trunk; correction note kept visible) | `storyline/PANORAMA_ptBR.md` §1 |
| PANORAMA "previu" softened to "levantou a hipótese e os resultados a sustentaram" (licensed strength) | `storyline/PANORAMA_ptBR.md` §2 |
| Stale OpenAlex status updated (connector needs in-app authorization) | `storyline/PANORAMA_ptBR.md` §6 |

**N2 drafting rule (recorded here, binding):** draft ONLY from N2's caution paragraph — CBIC
hypothesized three causes and its future work proposed the *architecture* door (soft
sharing/Cross-Stitch/MoE, optimizers, task-relatedness); it did NOT propose a representation
program. The claim-honesty auditor verified this against `conclusion.tex` this session. Never
write "CBIC's future work called for better representations."

**Item 2 rendering rule (banca finding):** the tasks are "coarser-grained than next place," never
"simpler"/"easier" — the author's "mais simples" note must not be rendered literally, or it
collides with the approved "harder, not easier" cardinality fact.

## 3. The N3 answer the author asked for (my opinion, as requested)

You wrote under N3: the current evidence for *where the MTL improvement comes from* feels not very
convincing; should we run more experiments (locally or on nespedgpu)?

**My honest assessment.** The evidence you have is better than you are giving it credit for, but it
has one real hole, and the banca simulator posed it verbatim as the one question the package cannot
yet answer: *"Se o ganho vem do tronco e não da interação entre as tarefas, um modelo dedicado de
tarefa única com a mesma capacidade não recuperaria o mesmo ganho? O senhor rodou esse baseline?"*
The freeze control proves the gain is a trunk effect (not task-teaching); what it does not prove is
that a **capacity-matched dedicated model** would not do the same. Today the defense is an honest
disclosure (params as cost) plus a concession — defensible at a master's, but it is the weakest
point under arguição.

**The options, ranked:**
1. **Run the capacity-matched dedicated baseline (recommended if time allows).** One experiment:
   the dedicated category model (and optionally region) scaled to ~the joint model's parameter
   count, same protocol (user-disjoint 5-fold, seeds, same tuning budget). It answers the exact
   banca question with a number instead of a concession. Feasibility: the repo has the full
   training pipeline (`../../../../../../../src`, `../../../../../../../scripts/train.py`, closing-data protocol), and nespedgpu (A40 46GB,
   128GB RAM, 32 cores) is connected — this is well within reach. **Licensing rule (mandatory,
   from the adversarial advisor):** the new numbers do NOT enter Ch.5 (the MobiWac version of
   record is under review); they live in the frame (a Ch.5-adjacent discussion or an appendix) as
   post-submission analysis, with their own fact gate, clearly dated. Either outcome strengthens
   you: if capacity-matched dedicated ≈ dedicated, the joint win is not a capacity artifact and
   the trunk story is confirmed; if it recovers part of the gain, you report it honestly and the
   two-factor story gains a third, quantified nuance — still your finding, not a reviewer's.
2. **Write the concession (the floor, already signed off).** The §3.4 concession is now in the
   spine's limitations beat, tied to the fixed-pair ablation as future work. This is the
   defensible minimum if no experiment runs.
3. **Do not** run broad new mechanism studies (symmetric freezes, representation probes, etc.)
   before the defense — scope creep against an August deadline; the capacity-matched baseline is
   the one experiment that answers the one live question.

**Decision needed from you:** option 1 (schedule the run; I prepare the scripts and dispatch to
nespedgpu) or option 2 (concession only). The Ch.6 §6.4 mechanism paragraph is drafted differently
under each, so this decision gates Ch.5/Ch.6 drafting — Ch.1–Ch.4 work is unaffected.

## 4. Still open (the author's list)

1. **The N3 decision** (§3 above) — gates Ch.6.
2. **CoUrb split verification** — one look at the CoUrb codebase (github.com/TarikSalles/
   Spatial_Embeddings) or `slides/judge_feedback.md` settles UW-3; until then no protocol
   difference is drafted anywhere.
3. **OpenAlex authorization** — the reconnected literature server needs its in-app authorization
   (Configurações → Conectores); then the beyond-mobility + N1-leg-2 sweep runs (open-and-verify,
   with the pre-approved fallback if no anchor supports the comparative form).
4. **The Ch.2 page fixes** (already catalogued in `10_specialist_check/`, still unapplied): the 2.1
   scope sentence (cold-reader escalation: it reads as false at Ch.3 — edit, not only add), the
   93% scoping, the under-review marker in 2.5, the map-partition sentence, the name-mapping seam.
   These ride the first drafting wave as its first work order.
5. **Ch.1 beat budget** (cold-reader MAJOR): before drafting Ch.1, one page assigning each approved
   move exactly one home (Ch.1 vs Ch.4 preface vs Ch.5 recap vs Ch.6) so the Introduction narrates
   rather than litigates. The "and/or" placements in the aval items are resolved there.
6. **Title shortlist** (cold-reader MINOR): two of the three NORTH_STAR §5 candidates fail the F1
   two-factor test ("Representation-Driven…", "Check-in-Level Representations for…"); the first
   candidate is the only survivor as written. Decide before front matter.
7. **Products/artifacts surface** (excellence MINOR): where the committee finds the products list
   (2 DOIs + 1 under review + code + protocol) — a short appendix or per-chapter footnotes.

## 5. Where the five full verdicts live

The complete structured verdicts (each persona's overlooked-items list, per-move soundness check on
all 11+3 approved items, narrative-quality paragraph, and top priority) are archived verbatim in
this folder as `five_verdicts.txt`.

---

## `process/README_old.md`

# Storyline review — folder index

Narrative/craft review of the unified CBIC → CoUrb → MobiWac arc, organized one folder per part of
the storytelling. Read-only assessment: it proposes narrative moves and never applies them or drafts
replacement chapter prose. Every result-claim traces to the sources fixed in the project
instructions; new frame claims are marked **[NEEDS SIGN-OFF]**; unverified external claims are
**[VERIFY]**.

## What is here

| Folder | Contents | Status |
|---|---|---|
| `01_arc_and_logline` | The reconstructed arc, the diff against the intended spine, the logline test, per-chapter earn-its-clause verdict (lenses 1–2) | pass-1, pass-2 note |
| `02_task_choice_endorsement` | **The task-change endorsement** — why next category + next region is the right object, and how to turn the task-pair evolution from a hidden confound into the arc's most satisfying beat (author-requested) | **pass-2, new** |
| `03_cohesion_and_threads` | Seam-by-seam cohesion audit + the thread ledger (lens 3) | pass-1, pass-2 note |
| `04_beats_missing_and_worth_adding` | Missing vs worth-adding beats (lens 4) | pass-1 |
| `05_craft_pacing_and_voice` | Momentum map, sag points, one-voice seam verdict (lens 5) | pass-1 |
| `06_honesty_under_pressure` | The honesty flags where a cleaner story would tempt a violation (lens 6) | pass-1, pass-2 note |
| `07_recommendations_and_protect` | Ranked located cost-tagged recommendations, protect list, closing 3-question answer (lens 7 + closing) | pass-1, pass-2 revision |
| `08_underweighted_sides` | **Second-pass audit** — sides of the story the first review under-weighted, incl. two corrections to pass-1 claims (author-requested) | **pass-2, new** |
| `09_application_scope_breadth` | **Beyond mobility** — are we motivating the tasks with examples beyond mobility (recommendation, urban planning, ecology)? Answer + verified material (author-requested, `noth_star_consideration.md` point 3) | **pass-2, new** |
| `10_specialist_check` | **Specialist clarity check** — four reviewers (MTL, POI/mobility, claim-honesty, banca) run on the drafts + arc; action summary separating what is fixed from what the author must action (author-requested) | **pass-2, new** |
| `AVAL_NECESSARIA_ptBR.md` | **Documento em português** — cada afirmação [NEEDS SIGN-OFF] explicada para o autor aprovar item a item (11 itens, TODOS decididos pelo autor) | pass-2, decided |
| `AVAL_NECESSARIA_2_ptBR.md` | Sub-avais dos ajustes do autor (N1–N3 + item 10) — TODOS decididos | pass-3, decided |
| `AVAL_NECESSARIA_3_ptBR.md` | **Decisões da re-revisão do arco completo** (D1 experimento-ou-concessão; D2 título; D3 orçamento de beats) — **abertas** | **pass-4, new** |
| `PANORAMA_ptBR.md` | A visão geral (logline, arco em 3 atos, estado das decisões, mapa dos capítulos, caminho até o rascunho) — corrigido na re-revisão | pass-3/4 |
| `11_full_arc_rereview` | **Re-revisão do arco completo** — 5 personas, 5/5 "ready_with_fixes"; correções de governança aplicadas; resposta à pergunta N3 do autor; vereditos completos em `five_verdicts.txt` | **pass-4, new** |

## The three questions, in one line each

- **Cohesive?** The *argument* is; the *document* is not yet, because the connective tissue (Ch.1
  arc narrative, the two recap subsections, the three time-capsule prefaces) is planned and unwritten.
  Cohesion here is a drafting task, not a rethinking task.
- **Enjoyable?** For a reader who knows the arc, yes — it has an authentic
  setup→frustration→insight→payoff shape. For a cold banca member, not until the frame narrates it.
- **Well-crafted?** The drafted prose (MobiWac, §2.5) is; the governance (GLOSSARY, WRITING_LAW,
  claim whitelist) is unusually strong. The risk is in the unwritten frame and the one translated
  chapter (CoUrb).

## The single highest-leverage move

Write the Introduction so the honest arc is its structural spine — open on the mobility stakes, pose
the research question, then narrate null → diagnosis → resolution, stating the resolution as
**two-factor** (a representation built for visits *and* a sharing topology that lets the tasks help
each other) and showing the mechanism (same place, different visit, same vector) as the hypothesis
the journey tests.

## What pass 2 changed (the author's task-change concern)

The concern was correct and exposed a systematic under-reading: pass 1 graded the *discipline* of the
task-scope choice instead of its *justification*, and missed that the task **pair** evolved across the
arc (static+sequential → two-sequential), which is a third change alongside representation and sharing
topology. Files 02 and 08 address this in full. Two pass-1 claims were corrected:
1. CoUrb tests representation-vs-representation only (both multi-task); it does **not** re-establish
   MTL-vs-single-task (UW-2).
2. The "CoUrb used a weaker sample-stratified protocol" claim is **unverified** and is retracted to a
   [VERIFY] flag (UW-3).

## Provenance note

Two web searches run this session ("negative-result framing"; "compilation-thesis unity") returned
titles/URLs only; no page was opened, so they provide no firsthand external grounding. External
calibration in these files is re-anchored on the internal excellence doc
(`reviewers/research/dissertation_excellence_2026-07-20.md`), opened firsthand; un-opened specifics are
[VERIFY]. An OpenAlex sweep for a cleaner task-choice anchor returned only noise and produced no new
citable reference (fail-closed: no new citation proposed).
