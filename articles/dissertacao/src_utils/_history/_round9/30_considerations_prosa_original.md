<!-- PRESERVED VERBATIM. This is src_utils/CONSIDERATIONS.md exactly as it stood at commit
     d4078c75 (the reviewers' prose as the author transcribed it, plus the 2026-07-28
     Codex audit and its addendum), before the rewrite into the per-item schema. Not one byte
     below was edited. sha256 of the original: ec352ade7706c54040423be0600b18eb13518d0bb7082e3cae06668875e0f3a6
     bytes 91492, lines 1229.
     Verify (the offset is MEASURED to a fixpoint, not reasoned: it depends on this header's
     own line count, so a hand-written guess is wrong and reads as tampering):
       tail -n +11 _history/_round9/30_considerations_prosa_original.md | shasum -a 256
     EXPECT: ec352ade7706c54040423be0600b18eb13518d0bb7082e3cae06668875e0f3a6
-->
# Considerações de revisão

## Germano

O germando não fez uma lista de considerações ele passou de forma verbal, vou descrever o que ele me passou:

Ele começou lendo `Representations for mobility`, sobre os dois primieiro paragrafos, ele comentou que está bem
contruido e que no segundo gostaria que adicionacemos a citação dos:
`Spectral Networks and Locally Connected Networks on Graphs` e `The graph neural network model`. Já no terceiro
paragrafo que discutimos sobre DGI e HGI, ele comenta sobre fazer um contraste com HGI e DGI, não é correto pois o DGI e
uma abordagem e HGI e uma aplicação, no texto parece que ambos estão como contrapontos.

A frase: "The baseline was also tuned rather than taken as published: the cross-region edge weight of their Equation 2,
set to 0.4 for the dense Chinese cities they study, was raised to 0.7 for the sparser United States state datasets used
here. The sweep that fixed that value ran on Alabama over four settings of the weight, 0.4, 0.5, 0.6, and 0.7, each
measured over five folds with a budget of 50 epochs, and the category F1 rose monotonically across them,
from $0.7388 \pm 0.0205$ at the published setting to $0.8186 \pm 0.0123$ at the adopted one, on a zero-to-one scale,
with the spread taken across the five folds." está jogado no texto e parece sem nexo com que está sendo dito.

Em sequencia o paragrafo: "A place embedding, however it is trained, shares one property: it assigns each place a single
fixed vector. That vector is the same whether the place is visited on a weekday morning or a Saturday night, by a
commuter or a tourist. Yet a place serves different functions in different contexts, and a representation that cannot
express this cannot distinguish two visits to the same place that mean different things. CTLE makes the point concrete
by learning location embeddings that are context- and time-aware, so that the vector for a place depends on the visit
\cite{lin2021ctle}. This is the limitation the rest of the dissertation responds to: a per-place vector is static across
visits, and moving below the place level, to the check-in itself, is the way to make the representation reflect the
visit." está bem escrito, mas nas palavras de germano parece mais um texot de introdução, mas ele é muito importante
para compreenção do que está sendo feito.

Ele sugere removermos o: "HGI is the place-level baseline representation the later chapters measure against, and it is
the direct base of the representation the dissertation contributes. Two qualifications belong with that use."

no paragrafo seguinte:"Before that step, several general....", temos alguns problemas, os artigos aparecem jogados um
atrás do outro sem muito ligação entre eles e ainda temos a adição do Film que é uma camada téoricamente do MTL não de
mobility. E ao final desse parágrafo em "In the models of Chapters 3 and 4 it conditions...", começamos a discutir sobre
sobré a métodologia do capitulo 3 and 4 e desnevolvemos um raciocinio que deveria ser possivelmente em outro lugar.

No paragrafo em sequencia: "Thecheck-in-levelrepresentation,Check2HGI", germano comenta se já definimos o que é
chekc2hgi.

Saindo do `Representations for mobility`, mas ainda dentro do contexto da fundamentação ele comenta que parece que
falata uma definição formal para varios conceitos, por exemplo como definimos um checking? Isso e importante pois nas
formulas em que vamos apresentar relacionado aos nossos modelo podemos usar esse conceitos.

Entrando na secão de `2.3 Multi-tasklearning`, ele comenta que sente falta de definição formais de multi task learning
formulas e debates mais elaborados. Comentamos mutio sobre MTL + POI, mas pouco sobre MTL em si, o que usamos
balanceadores, quem definiu arquiteturaas, balanceadores famosos e assim por diantes. Algo ainda que temos que pensar em
discutir dentro do tema de MTL com conflito no loss e como esse loss e medido na literatura e como usamos isso junto as
balanceadores, essa discução é importante pois no artigo vamos falar sobre isso, no mobiwac onde nosso modelo tem os
cosseno do loos ortogonal, é hoje esse conceito parece jogado no artigo e sem contexto para quem quiser entender.

O foco na fundamentação téorica tem que ser em criar um narrativa logica, com blocos de definições formais

Discussão extra traga pelo germano o nosso achado que as duas tarefas: next-region e next-category sobre o nosso modelos
não entram em conflito em nosso modelo MTL pode ser extendido em um trabalho futuro sobre se isso é algo que podemos
afirmar de forma mais global. O germano ainda argumenta que ele sente falta de uma argumentação mais técnica em com
dados sobre a prova que em nosso modelo essas tarefas não entream em conflito

## Fabrício

### 1. `0_main.tex`

1. **Quote:** `Orientador: Fabrício Aguiar Silva.`
   **File:** `0_main.tex`
   **Review:** Colocar em inglês também. **Claude take:**
   **Author take:**
   **Status:**

2. **Quote:**
   `permite que um serviço sensível à mobilidade aja antes que a visita aconteça, e as duas tarefas de previsão leem o mesmo histórico de visitas,`
   **File:** `0_main.tex`
   **Review:** Iniciar nova sentença com algo como: "Em termos de dados, essas duas tarefas de previsão precisam do
   mesmo histórico...."
   **Claude take:**
   **Author take:**
   **Status:**

3. **Quote:** `era uma questão em aberto quando esta pesquisa começou.`
   **File:** `0_main.tex`
   **Review:** Colocar no presente: "é uma questão em aberto", como se estivesse escrevendo no começo da pesquisa.
   **Claude take:**
   **Author take:**
   **Status:**

4. **Quote:**
   `Esta dissertação responde a essa pergunta ao longo de três estudos, apresentados como uma coletânea de artigos...`
   **File:** `0_main.tex`
   **Review:** Não precisa falar aqui sobre a coletânea de artigos; deixar apenas para a introdução, na organização do
   texto. Aqui, falar como se fosse um único trabalho. **Claude take:**
   **Author take:**
   **Status:**

5. **Quote:**
   `apresentados como uma coletânea de artigos na ordem em que aconteceram: um resultado negativo, seu diagnóstico e sua resolução.`
   **File:** `0_main.tex`
   **Review:** Em "na ordem em que aconteceram: um resultado negativo, seu diagnóstico e sua resolução.": Tirar essa
   parte. **Claude take:**
   **Author take:**
   **Status:**

6. **Quote:** `cinco estados dos Estados Unidos e Istambul`
   **File:** `0_main.tex`
   **Review:** O leitor não sabe nada de estados ainda; falar em "cenários" em vez de "estados". **Claude take:**
   **Author take:**
   **Status:**

7. **Quote:** `e não a arquitetura de compartilhamento, era o gargalo naquele estágio da pesquisa.`
   **File:** `0_main.tex`
   **Review:** Em "naquele estágio da pesquisa", ele comenta: `no primeiro estudo (??)`
   **Claude take:**
   **Author take:**
   **Status:**

8. **Quote:** "; os dois primeiros pareavam a classificação de categoria com a previsão da próxima categoria, de modo
   que o próprio par de tarefas mudou ao longo da coletânea."
   **File:** `0_main.tex`
   **Review:** Tirar... está ficando confuso para o leitor **Claude take:**
   **Author take:**
   **Status:**

9. **Quote:** `por 5,3
    a 9,4 pontos de macro-F1 sob uma seleção \emph{joint-best} (um único \emph{checkpoint}
    por partição, escolhido na validação, com as duas tarefas avaliadas nesse
    \emph{checkpoint}), e, na tarefa da próxima região, supera em quatro dos seis
    conjuntos e equipara-se estatisticamente, com não-inferioridade dentro de uma
    margem de dois pontos de Acc@10 (TOST), nos outros dois. A resposta é, portanto,
    condicional, e a condição é o achado:`
   **File:** `0_main.tex`
   **Review:** Simplificar essa descrição dos resultados... colocar em mais alto nível. **Claude take:**
   **Author take:**
   **Status:**

10. **Quote:** "A resposta é, portanto, condicional, e a condição é o achado:"
    **File:** `0_main.tex`
    **Review:** Esse início está confuso também; começar com algo como: "Como principais resultados, identificamos que o
    aprendizado multitarefa etc etc..."
    **Claude take:**
    **Author take:**
    **Status:**

11. **Quote:** "\textbf{Palavras-chave}:\\ aprendizado multitarefa\\ ponto de interesse\\ previsão da próxima
    categoria\\ previsão da próxima região\\ representação em nível de check-in"
    **File:** `0_main.tex`
    **Review:** Separar por "virgula" em vez de quebra de linha; fazer o mesmo no inglês. **Claude take:**
    **Author take:**
    **Status:**

### 2. `chapters/1_introduction.tex`

12. **Quote:** `a given user visited a given place`
    **File:** `chapters/1_introduction.tex`
    **Review:** `users`
    **Claude take:**
    **Author take:**
    **Status:**

13. **Quote:** "The two properties above are the two prediction tasks of this dissertation."
    **File:** `chapters/1_introduction.tex`
    **Review:** Em `prediction tasks`, consideração: `prediction tasks that are object of study of this ...`
    **Claude take:**
    **Author take:**
    **Status:**

14. **Quote:** "The \\emph{next category} task predicts the category of the next visited place, one of seven top-level
    classes."
    **File:** `chapters/1_introduction.tex`
    **Review:** Não precisa detalhar que são 7 aqui na introdução; isso não é característica do problema, mas dos dados,
    e deve aparecer apenas na hora de descrever a avaliação. **Claude take:**
    **Author take:**
    **Status:**

15. **Quote:** "The \\emph{next region} task predicts the official geographic unit of the next visit, a census tract in
    the United States or a mahalle in Istanbul, a target space that ranges from hundreds to several thousand classes per
    dataset."
    **File:** `chapters/1_introduction.tex`
    **Review:**Em ", a census tract in the United States or a mahalle in Istanbul," e feito a consideração: "Isso também
    é inerente aos dados e não precisa entrar aqui na introdução."
    **Claude take:**
    **Author take:**
    **Status:**

16. **Quote:** "The exact \\emph{next place} task, predicting the specific establishment, is a third and different
    problem; this dissertation does not address it, and Chapter~\\ref{ch:fundamentals} keeps the three tasks formally
    distinct."
    **File:** `chapters/1_introduction.tex`
    **Review:**Em "; this dissertation does not address it," a consideração: "not addressed in this dissertation (TENTE
    USAR MENOS ; no meio das frases...parece muito resultado de IA)"
    **Claude take:**
    **Author take:**
    **Status:**

17. **Quote:** "A fourth task also appears in this dissertation: the first two studies paired next category prediction
    with the static classification of a place's category, category classification, and Section~\\ref{sec:intro:arc}
    explains why the final study replaced it. Next category and next region were chosen for what a mobility-aware
    service can act on, and both are established end targets in the literature on the way to the harder next-place
    problem."
    **File:** `chapters/1_introduction.tex`
    **Review:** Parágrafo confuso; acho que pode tirar. **Claude take:**
    **Author take:**
    **Status:**

18. **Quote:** "was unresolved when this research started."
    **File:** `chapters/1_introduction.tex`
    **Review:** Colocar no presente. **Claude take:**
    **Author take:**
    **Status:**

19. **Quote:** "\section{Research question and the arc of this dissertation}"
    **File:** `chapters/1_introduction.tex`
    **Review:** Em "the arc of this dissertation" consideração: "Tirar"
    **Claude take:**
    **Author take:**
    **Status:**

20. **Quote:** "Does multi-task learning help point-of-interest prediction (next category and next region), and what
    does the answer depend on?"
    **File:** `chapters/1_introduction.tex`
    **Review:** Padronizar a escrita de `point of interest` (POI) em todo o texto. É com ou sem hífen? Manter o mesmo
    sempre. **Claude take:**
    **Author take:**
    **Status:**

21. **Quote:** "with decomposed spatial, temporal, and categorical encoders. Category performance rose sharply at every
    state tested."
    **File:** `chapters/1_introduction.tex`
    **Review:** Em "state", o comentario é: `scenario`
    **Claude take:**
    **Author take:**
    **Status:**

22. **Quote:** "five states of the United States and Istanbul: on the category task at all six, and on the region task
    at four of six, with statistical non-inferiority within a two-point margin (TOST) at the other two."
    **File:** `chapters/1_introduction.tex`
    **Review:** Não precisa incluir os detalhes dos resultados aqui. **Claude take:**
    **Author take:**
    **Status:**

23. **Quote:** "\textbf{Chapter~\ref{ch:fundamentals}, Fundamentals}, consolidates the background the three"
    **File:** `chapters/1_introduction.tex`
    **Review:** Em ", Fundamentals}," o comentario é:  "Tirar."
    **Claude take:**
    **Author take:**
    **Status:**

24. **Quote:** "\textbf{Chapter~\ref{ch:conclusion}, Conclusion}, consolidates the answer to the research question,
    states the limitations, and derives future work from them."
    **File:** `chapters/1_introduction.tex`
    **Review:** Em ", Conclusion}, " o comentario é: "Tirar."
    **Claude take:**
    **Author take:**
    **Status:**

### 3. `chapters/2_fundamentals.tex`

25. **Quote:** "Each record is a \emph{check-in}: a user, a point of interest (POI), and a timestamp."
    **File:** `chapters/2_fundamentals.tex`
    **Review:** Em: "point of interest (POI)". consideração: "Aqui está sem hífen; padronize em todo o texto."
    **Claude take:**
    **Author take:**
    **Status:**

26. **Quote:** "The check-in-level representation, Check2HGI, completes the line."
    **File:** `chapters/2_fundamentals.tex`
    **Review:** Ficou parecendo que é um artigo concorrente existente; falar que é a sua proposta já no começo do
    parágrafo. **Claude take:**
    **Author take:**
    **Status:**

27. **Quote:** Na tabela: "\caption{Representation and model lineage threaded through this dissertation, from the
    place-level graph-infomax...."
    **File:** `chapters/2_fundamentals.tex`
    **Review:** A referência dos capítulos da tabela está errada. **Claude take:**
    **Author take:**
    **Status:**

28. **Quote:** "In mobility, MTL has been used almost entirely in the service of next place."
    **File:** `chapters/2_fundamentals.tex`
    **Review:** Pelo que me lembro, há outros artigos que abordam MTL para tarefas de POI, não? Ficaram apenas dois
    artigos aqui, o que parece pouco pelo que me lembro. **Claude take:**
    **Author take:**
    **Status:**

29. **Quote:** "This section fixes both: the datasets the dissertation uses..."
    **File:** `chapters/2_fundamentals.tex`
    **Review:** `fixes ???`
    **Claude take:**
    **Author take:**
    **Status:**

30. **Quote:** "and the tests that license the verbs used to report a comparison."
    **File:** `chapters/2_fundamentals.tex`
    **Review:** Em "license the verbs" a consideração: "Cuidado com termos muito incomuns de serem encontrados,
    provavelmente gerados por IA. Não é comum usar `license the verbs` em textos técnicos; revisar o texto que foi
    gerado por IA para evitar isso."
    **Claude take:**
    **Author take:**
    **Status:**

### 4. `chapters/6_conclusion.tex`

31. **Quote:** "raised category macro-F1 by 20.2 to 22.0 percentage points across the three states tested."
    **File:** `chapters/6_conclusion.tex`
    **Review:** Trocar `states` para `scenarios`
    **Claude take:**
    **Author take:**
    **Status:**

---

# Codex Audit — Chapter 2 (Fundamentals)

_Independent audit, 2026-07-28. Scope: `chapters/2_fundamentals.tex` only; comments on other files are listed in
CONSIDERATIONS.md but are out of scope here except where they set a rule Chapter 2 must obey (POI hyphenation,
`states` -> `scenarios`). Every factual claim below was checked against the repository or the source of record this
session; where a check failed or could not be completed, it says so._

**Method.** I re-read the chapter as committed, then read Fabrício's items 25-30 and Germano's verbal notes. Claims that
could be verified were verified: the lineage-table references were read from
`src/tables/frame/lineage.tex` against the `\label{ch:...}` set actually defined in `src/chapters/`;
`point of interest` / `point-of-interest` were counted across the whole `src/` tree; the two citations Germano requested
were resolved firsthand (Crossref, arXiv); the candidate MTL-for-POI works were read from `src/references.bib`.
Comparative material comes from the five dissertations in `exemples/`, with Viegas (same advisor, same program, English
coletânea, approved) measured page by page.

**Verdict in one line.** Both reviewers are right about the chapter's central weakness, and they found it from two
different directions: the chapter narrates a lineage well but does not **define** anything formally, and its §2.3 is a
catalogue of MTL machinery rather than a treatment of MTL. Of the eleven review points I can act on, I agree with nine,
agree-with-correction with one (Fabrício 28 is right but his "apenas dois artigos" undercounts what the chapter actually
cites), and disagree with one in part (Germano's DGI/HGI framing, where the prose is already correct and the fix should
be narrower than he suggests).

---

## Part I — Audit of Fabrício's comments

### F25. `point of interest (POI)` — hyphenation must be standardized

**Verdict: agree. Required.**

This is not a preference; it is an inconsistency the reader can see. Counted across `src/` this session:
**13 hyphenated** vs **8 spaced**, and the split is not even principled within a single file. Both forms appear in
Chapter 2 (`2_fundamentals.tex:28` spaced, one hyphenated elsewhere) and both appear in Chapter 1
(`1_introduction.tex:34` spaced, `:93` and `:146` hyphenated).

The correct rule is the standard English compound-modifier rule, and it explains the whole distribution:
hyphenate when the phrase modifies a noun, leave it open when it is the noun itself.

- attributive -> hyphenated: "point-of-interest prediction", "point-of-interest category".
- nominal -> open: "a user visits a point of interest (POI)".

So `2_fundamentals.tex:28` ("a user, a point of interest (POI), and a timestamp") is **already correct**
and should not be changed, whereas "point-of-interest prediction" in Chapter 1 and Chapter 6 is also correct. Recommend
adopting this rule explicitly in `GLOSSARY.md` rather than flattening everything to one form, and then sweeping the tree
once against it. Flattening to the hyphen everywhere would produce "a user visits a point-of-interest", which is wrong.

### F26. "The check-in-level representation, Check2HGI, completes the line." — reads like a competitor

**Verdict: agree, and this is the highest-value small edit in the chapter. Required.**

Fabrício has identified a real defect with a real cost. The paragraph introduces Check2HGI in exactly the same
grammatical register the chapter has just used for DGI, HGI, CTLE, and Time2Vec — all other people's work — and it
carries no first-person marker, no "we", no "this dissertation proposes". A reader arriving at that sentence has no way
to know the sentence has crossed from related work into contribution. It is worth noting **why** the defect exists: the
honesty protocol removed the `\cite` that used to sit there (it pointed at the CBIC paper, which does not contain
Check2HGI), and removing the citation without adding an ownership marker left the sentence looking like an uncited
third-party method — the worst of both readings.

Concrete fix, naming ownership in the first clause:

> "The check-in-level representation this dissertation contributes, Check2HGI, completes the line. It
> extends the graph-infomax hierarchy with a fourth level below the place, the check-in, and is trained
> without task labels in the same infomax spirit, so that each visit, rather than each place, carries its
> own vector. Chapter~\ref{ch:mobiwac} develops it in full."

This also answers Germano's independent question on the same sentence ("já definimos o que é Check2HGI?"), which is
strong evidence the sentence is genuinely unclear: two readers stumbled at the same place.

### F27. "A referência dos capítulos da tabela está errada."

**Verdict: disagree as stated, but he is pointing at a real problem. Required, different fix.**

I checked this directly. `src/tables/frame/lineage.tex` references `Chapter~\ref{ch:courb}` (ST-MTLNet) and
`Chapter~\ref{ch:mobiwac}` (Check2HGI, joint model). Those labels **are** defined, in
`4_courb.tex` and `5_mobiwac.tex` respectively, and `0_main.tex:412-417` includes the chapters in the order 1-2-3-4-5-6,
so `ch:courb` resolves to Chapter 4 and `ch:mobiwac` to Chapter 5. The `\ref` keys are therefore **not** wrong, and no
key is dangling.

What is almost certainly behind the comment is that the table **mixes two kinds of thing in one column**. The
"Reference" column holds bibliographic citations for the first three rows (`\cite{velickovic2019deep}`,
`\cite{huang2023hgi}`, `\cite{silva2025mtlnet}`) and internal chapter pointers for the last three
(`Chapter~\ref{ch:courb}`, `Chapter~\ref{ch:mobiwac}` twice). A reader scanning the column sees "[41]",
"[23]", "[57]", "Chapter 4", "Chapter 5", "Chapter 5" and reasonably reads the chapter numbers as mis-rendered
citations. Two further asymmetries make it worse: ST-MTLNet has a published record (CoUrb 2026, DOI
10.5753/courb.2026.22960) and MTLnet is cited bibliographically, so the table cites one of the author's own published
papers by reference and the other by chapter, with no visible reason.

Recommended fix: **split the column in two** — "Reference" (bibliographic, for external work and for the author's
published papers) and "Where in this dissertation" (chapter pointer, for all six rows). Every row then gets a chapter
pointer, MTLnet and ST-MTLNet both get their published citations, and Check2HGI and the joint model correctly show a
chapter pointer with no citation because they are under review. This removes the mixed-column ambiguity rather than
changing a `\ref` that is already correct.

*Please confirm with Fabrício which reading he meant.* If he was looking at a built PDF where the numbers genuinely
rendered as `??`, that is a stale-`.aux` build artifact, not a source error — the source is sound as committed.

### F28. "há outros artigos que abordam MTL para tarefas de POI... apenas dois artigos aqui, parece pouco"

**Verdict: agree with the substance, correct on one detail. Required.**

The detail first: the paragraph cites **two** works (`Liao2018`, `huang2024cslsl`), but §2.3 as a whole also carries
`silva2025mtlnet`, and §2.1 separately discusses `Lim2022` (HMT-GRN, explicitly a *Hierarchical Multi-Task* Graph
Recurrent Network), `yu2020catdm`, `zhu2022drrgnn`, and `capanema2023poirgnn`. So the chapter's MTL-for-POI coverage is
not two papers; it is split across two sections, which is itself part of the problem — the reader of §2.3 cannot see the
coverage that §2.1 already provided.

The substance is correct, and I can name what is missing, because it is **already in the global bib and uncited in the
chapter**. Verified in `src/references.bib` this session:

| Key             | Work                                                                                                                                                   | Why it belongs in §2.3                                                                                       |
|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| `Zhang2020`     | Zhang et al., *An Interactive Multi-Task Learning Framework for Next POI Recommendation with Uncertain Check-ins*, IJCAI 2020, 10.24963/ijcai.2020/491 | An MTL-for-POI framework proper; currently cited nowhere in Ch.2                                             |
| `wang2025hamtl` | Wang et al., *Hierarchy Aware-based Multi-task Learning for User Location Prediction*, J. Supercomputing 81(11), 2025, 10.1007/s11227-025-07643-7      | Hierarchy-aware MTL for **location** prediction — the closest neighbour to our region task, and recent       |
| `Halder2021`    | Halder et al., *Transformer-Based Multi-task Learning for Queuing Time Aware Next POI Recommendation*, PAKDD 2021, 10.1007/978-3-030-75765-6_41        | Transformer MTL for POI; shows the auxiliary-task pattern                                                    |
| `Halder2022`    | Halder et al., *POI Recommendation with Queuing Time and User Interest Awareness*, DMKD 36, 2022, 10.1007/s10618-022-00865-w                           | Journal extension of the above                                                                               |
| `Xu2023`        | Xu et al., *TME: Tree-guided Multi-task Embedding Learning towards Semantic Venue Annotation*, TOIS 41(4), 2023, 10.1145/3582553                       | Already cited in §2.1 for static category classification, but it is an **MTL** method and §2.3 never says so |

There is a further reason to act on this beyond completeness, and it is the strongest argument in the audit: **§2.3's
novelty claim is currently exposed.** The paragraph asserts that "no multi-task model among them predicts the next
region as a co-equal end target alongside the next category" while citing only two systems. A
`Journal of Supercomputing` 2025 paper on *hierarchy-aware multi-task learning for user location prediction* sits
uncited in the same bibliography. An examiner who finds it will ask why a claim of absence was made over a sample of
two. The claim may well survive — `wang2025hamtl` predicts location, not a region co-equal with a category — but the
chapter must be seen to have looked.

**[VERIFY before drafting]** I could not read the `wang2025hamtl` or `Zhang2020` abstracts this session (OpenAlex search
returned empty for these titles; Semantic Scholar returned HTTP 429). Their bibliographic attributes above are copied
from `src/references.bib`, not from the source of record. Before any of them is cited for a *claim*, its abstract must
be opened and its target space checked — specifically whether
`wang2025hamtl` treats a region-like unit as an end target, which is what the novelty sentence turns on. Do not let a
new citation enter on the strength of its title.

### F29. "This section fixes both: ... `fixes ???`"

**Verdict: agree. Required.**

"Fixes" is being used in the sense of *fixes in place / pins down*, which is idiomatic in British academic prose but
collides head-on with the dominant computing sense of *repairs*. In a sentence that begins "A claim about mobility
prediction is only as trustworthy as the data it is measured on and the protocol that measures it. This section fixes
both", the near-reading is "this section repairs the data and the protocol", which is nonsense and momentarily suggests
something is broken. Fabrício's three question marks are a reader-experience report, and they are the correct response.

Suggested wording: **"This section sets out both:"** or **"This section specifies both:"**. Note the same verb-sense
appears in the §2.4 ledger comment ("the datasets ... the metrics ... this section fixes both"), so fix the prose and
leave the comment, or change both together.

### F30. "license the verbs" — uncommon phrasing, likely AI-generated

**Verdict: agree on the phrasing, and the underlying concept must survive the edit. Required.**

He is right about the register. "License" as a transitive verb taking a *verb* as object ("the tests that license the
verbs used to report a comparison") is not standard technical English; it is a philosophy-of- science construction. It
appears **twice** in the chapter (§2.4 opening and again in the Wilcoxon sentence,
"either test licenses the verb ``outperforms''"), plus in the ledgers. To a reader — and to a banca — an unusual
metaphor repeated is a stylistic tell, exactly as he says.

But the *concept* it encodes is one of the strongest things in this dissertation and must not be lost in the rewording:
the rule that a comparative verb may only be used when a specific test supports it. Replace the metaphor with the plain
statement of the rule:

- §2.4 opening: "...and the statistical tests that must support each comparative claim."
- Wilcoxon sentence: "...either test supports the claim that one model outperforms another;"
- Closing sentence: "Wherever this dissertation reports a comparison, the claim and the test are stated together: one
  model is said to *outperform* another only on the evidence of a paired superiority test, and to *match* another only
  on the evidence of a non-inferiority test within the stated margin."

**A broader point his comment opens up, which I would act on.** I swept Chapter 2 for the same class of construction and
found a cluster of metaphors carrying analytical weight: "Two check-in datasets **serve as the ground**", "**That
protocol is the last piece**", "Two qualifications **belong with that use**", "it is the **hinge** of the representation
argument", "Here the representation is **the lever**" (twice), "The preceding sections are **not a catalog**", "That
stance only **pays off** if...", "a balancer **earns its place**". Individually each is defensible; together, at this
density, they are the chapter's most identifiable stylistic signature, and F30 is the reviewer noticing it once.
Recommend one deliberate pass to convert the load-bearing metaphors into plain statements and keep at most one or two as
deliberate rhetoric. **Recommended** (not Required — this is register, not correctness).

---

## Part II — Audit of Germano's comments

### G1. Add `Spectral Networks and Locally Connected Networks on Graphs` and

`The graph neural network model` to the GNN paragraph

**Verdict: agree. Required. Both verified; neither is currently in the bibliography.**

The §2.2 GNN paragraph currently runs GCN -> GAT -> GraphSAGE and so begins the graph-neural-network story in 2017. That
is a real gap: it presents the localized spectral rule of GCN without the spectral-graph foundation it simplifies, and
it presents "graph neural network" as a settled term without the paper that defined it. Both requested works are the
standard anchors, and adding them costs two sentences.

Verified firsthand this session:

- **Bruna, Zaremba, Szlam, LeCun**, *Spectral Networks and Locally Connected Networks on Graphs*, arXiv:1312.6203
  (2013-12-21; ICLR 2014). Author list and title read from the arXiv record.
- **Scarselli, Gori, Tsoi, Hagenbuchner, Monfardini**, *The Graph Neural Network Model*, IEEE Transactions on Neural
  Networks **20**(1):61-80, 2009, DOI 10.1109/tnn.2008.2005605. Title, venue, volume, pages and the first four authors
  read from Crossref; the fifth author (Monfardini) is standard on this paper but was truncated by the Crossref author
  list I read — **[VERIFY: complete the author list from IEEE Xplore before the entry is committed]**.

Both keys are **absent from `src/references.bib`** (grepped: no `bruna`, `scarselli`, `spectral networks`, or
`graph neural network model`), so this adds two new entries. Suggested insertion, one sentence before the existing GCN
sentence:

> "Graph neural networks generalize this idea: the model class was defined by Scarselli et al.\
> \cite{scarselli2009gnn}, and the spectral construction of Bruna et al.\ \cite{bruna2014spectral} showed
> how convolution can be defined on a graph through the graph Laplacian. The graph convolutional network
> simplifies that construction into a localized first-order rule \cite{kipf2017gcn}; ..."

Note this makes the existing GCN sentence *more* accurate, since "localized spectral rule" is precisely a simplification
of Bruna's spectral construction — the citation Germano asks for is the one that makes our own sentence true.

### G2. The DGI/HGI contrast: "DGI é uma abordagem e HGI é uma aplicação"

**Verdict: partially disagree. The prose is already correct; a narrower fix is warranted. Recommended.**

I re-read the passage. It does **not** set DGI and HGI against each other as competing alternatives. It says DGI
"applies the principle to graphs", then "Hierarchical Graph Infomax (HGI) **builds directly on it**", then "HGI
**extends** the infomax objective across a hierarchy". "Builds directly on" and "extends"
are inheritance language, not contrast language, and they encode exactly the relation Germano is asking for. On the
plain text of the paragraph I disagree that both appear as counterpoints.

His reading is nonetheless evidence of something real, and I can name the cause. The **lineage table**
lists DGI and HGI as two adjacent rows in a column called "What it added", which is a comparative presentation, and the
sentence "HGI is the place-level baseline representation the later chapters measure against" casts HGI in a *baseline*
role — i.e. as something to be beaten. A reader holding the table and that sentence together can easily come away
thinking the chapter is weighing DGI against HGI. The fix is therefore not to rewrite the inheritance sentences but to
make the **roles** explicit, which the prose currently leaves implicit: DGI is the objective (the method), HGI is that
objective instantiated over the POI-region-city hierarchy, and *in this dissertation* DGI supplies the embeddings of the
first study while HGI supplies the place-level baseline of the later ones. One clause stating the two roles removes the
ambiguity without touching a correct description.

I would also record a caution: his framing "HGI é uma aplicação" is itself slightly too strong. HGI contributes a
genuinely new objective (mutual information across a three-level hierarchy plus the cross-region edge weighting of its
Equation 2), not merely an application of DGI to new data. Describing it as "an application" in our prose would
under-credit Huang et al. and would sit badly beside our own statement that Check2HGI *extends* the same hierarchy — if
HGI is a mere application of DGI, our fourth level is a mere application of HGI. Keep "extends", make the roles
explicit.

### G3. The HGI tuning sentence (w_r 0.4 -> 0.7, F1 0.7388 -> 0.8186) "está jogado no texto e parece sem nexo"

**Verdict: strongly agree, and I would go further than he does. Required.**

He is right, and the diagnosis is structural rather than stylistic. That passage is a **methods result**
sitting in a **fundamentals** chapter. Chapter 2's job, as the chapter's own opening paragraph states, is to set out
concepts the three studies share; a four-point hyperparameter sweep on one state with a 50-epoch budget and fold-level
standard deviations is not shared background, it is an experimental finding belonging to whichever study adopted it. Its
presence also breaks the paragraph's argument: the sentence before it establishes what HGI *is*, and the sentence after
moves to the static-vector limitation, so the reader must hold a hyperparameter table in mind across a conceptual
transition for no benefit.

There is a second, sharper reason to move it. The passage carries an unresolved `[VERIFY]` in the source:
the averaging convention of the swept "Cat F1" is not established (macro vs weighted), which is why the prose says
"category F1" and not "macro-F1". §2.4 makes macro-F1 the primary category metric. So the chapter reports four F1
numbers to four decimal places under a convention it has not fixed, thirty lines before it fixes the convention. That is
a fair target at a defense.

Recommendation, in order of preference:

1. **Move** the sweep to the chapter that owns the baseline (Chapter 5 method or its appendix), where the convention is
   fixed and the numbers sit among other experimental detail. **Required.**
2. In §2.2 keep only the conceptual residue, one sentence with no numbers: *"The baseline was retuned rather than taken
   as published, because the published cross-region edge weight was set for dense cities and the datasets used here are
   sparser; Chapter~\ref{ch:mobiwac} reports the sweep."*
3. If the numbers must stay in Chapter 2, resolve the `[VERIFY]` first and name the convention.

The **first** qualification in that same passage (that Huang et al. present HGI for urban *region*
representation, so we repurpose its POI-level output for a sequential task their paper does not address)
should **stay**. It is conceptual, it is honest, it is exactly the kind of thing a fundamentals chapter should say, and
it is the qualification an examiner is most likely to raise.

### G4. Remove "HGI is the place-level baseline representation the later chapters measure against, and it is the direct base of the representation the dissertation contributes. Two qualifications belong with that use."

**Verdict: agree in part — disagree on the first sentence, agree on the second. Recommended.**

Splitting his suggestion, because the two sentences do different work:

- **"Two qualifications belong with that use."** — Delete. This is scaffolding: it announces a list instead of
  delivering it, it is the kind of meta-sentence that makes prose feel machine-assembled, and both qualifications read
  perfectly well without an announcement. Germano is right. (It also uses the odd
  "belong with that use" construction flagged under F30.)

- **"HGI is the place-level baseline representation the later chapters measure against, and it is the direct base of the
  representation the dissertation contributes."** — **Keep**, possibly reworded. This sentence does indispensable work:
  it is the only place in §2.2 that tells the reader HGI plays *two*
  roles in this dissertation (baseline to be measured against, and ancestor of our contribution). Delete it and the
  chapter loses the link between the representation lineage and the experimental design, and the lineage table's HGI row
  loses its explanation. It is also, as noted under G2, the sentence that should be *expanded* slightly to make the
  DGI/HGI roles explicit. Deleting it would make G2 worse.

If the goal is brevity, merge: *"In this dissertation HGI plays two roles: it supplies the place-level baseline the
later chapters measure against, and it is the direct base of the check-in-level representation proposed here."*

### G5. The "Before that step, several general encoders..." paragraph — works listed without connection, FiLM is MTL not mobility, and the Ch.3/Ch.4 methodology discussion belongs elsewhere

**Verdict: agree on all three counts. This is the weakest paragraph in the chapter. Required.**

Three distinct defects, all real:

1. **Catalogue structure.** Time2Vec, SIREN, Space2Vec, Sphere2Vec, and the spherical-harmonics encoder arrive as five
   consecutive one-sentence descriptions with no organizing claim. The reader is told what each does but not why they
   are grouped, which is the more so a problem because — as our own ledger records — **Space2Vec is adopted in neither
   chapter**. A fundamentals chapter may name background it does not use, but then it must say what the group is *for*.
   Fix: open the paragraph with the organizing claim (these encode continuous time and continuous space, the two context
   dimensions a static place vector omits), then split time (Time2Vec, SIREN) from space (Space2Vec, Sphere2Vec,
   spherical harmonics), and say plainly which are adopted and which are named as background.

2. **FiLM is misfiled.** He is right that FiLM is a conditioning/architecture mechanism, not a mobility representation,
   and it currently sits at the end of a paragraph about spatial and temporal encoders purely because the following
   sentence needed it. Its natural home is §2.3, in the sharing-topology discussion, where cross-stitch, MMoE, PLE and
   DSelect-k already are — FiLM conditioning is precisely what the joint model *replaces* with cross-attention, so §2.3
   is where it earns its keep. Moving it also repairs §2.3, which currently describes the MTLnet-to-joint-model change
   without having introduced FiLM.

3. **Chapter 3/4 methodology in a fundamentals chapter.** Agreed, with one qualification. The sentences
   "Chapter 3 feeds a single place-level embedding..." and "Chapter 4 keeps that model but decomposes the input..." are
   method description, and §2.2 is not the place for a walk-through. But the *claim* those sentences carry — that how
   context enters is the turning point of the dissertation — is the chapter's thesis and must stay somewhere in Chapter
    2. Recommendation: keep one sentence of forward-pointing claim in §2.2 ("How that context enters the model, rather
       than which encoder produces it, is what separates the three studies; Chapters~\ref{ch:cbic} and~\ref{ch:courb}
       differ in exactly this respect."), and move the per-chapter mechanics to §2.5 or to the chapters themselves. Note
       this is the same over-reach the panel review already corrected once in this paragraph (it previously
       mis-attributed CoUrb's encoders to MTLnet); the paragraph keeps attracting method detail, which is a sign the
       detail wants to live elsewhere.

The same objection applies with more force to the **two long passages further down §2.2** — the Check2HGI loss (three
display equations) and the "joint model is a specialization of the MTLnet class" paragraph. Both are method, not
fundamentals; both carry `[NEEDS SIGN-OFF]` markers; and the second is written from the *source code* (class
inheritance, overridden methods). See M1 below: I think Germano's objection here is the local instance of a chapter-wide
boundary problem.

### G6. "Já definimos o que é Check2HGI?"

**Verdict: agree. Required.** Same defect as F26, from a different reader — see F26 for the fix. Two independent
reviewers stopping at the same sentence is the strongest possible signal that it needs rewriting. Germano's phrasing
also isolates the precise failure: the name arrives *before* any definition, in a chapter that has defined every other
named method at first use.

### G7. "Falta uma definição formal para vários conceitos, por exemplo como definimos um check-in? Isso é importante pois nas fórmulas dos nossos modelos podemos usar esses conceitos."

**Verdict: strongly agree. This is the single most important comment in either review. Required.**

Germano has found the chapter's structural gap, and his reasoning for *why* it matters is exactly right and is the part
I would emphasize to the author: the later chapters' equations need symbols, and those symbols have no origin. Chapter 2
currently defines a check-in in prose only — "a user, a point of interest (POI), and a timestamp" — and then Chapter 2
itself writes $\mathcal{L}_{c2p}$ over check-in and place embeddings with no notation for a check-in, a user, a place, a
category, or a region anywhere in the document. The chapter that exists to supply shared concepts supplies no shared
**notation**.

The comparative evidence is decisive here, and it comes from Germano's own dissertation. In
`exemples/germano/.../2_havana.tex` he writes:

> "A location-based social network contains check-ins $C = \{ (p_i, t_i)\}$, which are events characterizing
> a user's visit to a place $p_i$ on a timestamp $t_i$. This place is known as a Point of Interest (POI)
> $p = \langle l, cat \rangle$, which is represented by a location $l$ and a category $cat$."

That is the bar he is asking us to meet, and he cleared it himself in the same program. Our chapter is weaker than the
precedent on precisely this axis.

**Concrete proposal.** Add a short formal block at the end of §2.1 — a "Notation and problem statement"
subsection of roughly half a page — that introduces, once, the symbols the whole document then uses:

> A check-in is a triple $c = \langle u, p, t \rangle$: a user $u \in \mathcal{U}$, a place $p \in
> \mathcal{P}$, and a timestamp $t$. A place carries a location and a category, $p = \langle \ell_p,
> \kappa_p \rangle$ with $\kappa_p \in \mathcal{K}$, $|\mathcal{K}| = 7$, and falls in exactly one region
> $r_p \in \mathcal{R}$ under the partition of Section~\ref{sec:fund:eval}. The history of user $u$ up to
> time $t$ is the time-ordered sequence $H_u^t = (c_1, \ldots, c_n)$ of that user's check-ins with $t_i <
> t$. Given $H_u^t$, **next-category prediction** estimates $P (\kappa_{p_{n+1}} \mid H_u^t)$ over
> $\mathcal{K}$ and **next-region prediction** estimates $P (r_{p_{n+1}} \mid H_u^t)$ over $\mathcal{R}$.
> **Next-place prediction**, which this dissertation does not address, would estimate $P (p_{n+1} \mid
> H_u^t)$ over $\mathcal{P}$; the three differ in their output space, and $|\mathcal{P}| \gg |\mathcal{R}|
> > |\mathcal{K}|$ is the reason they differ in difficulty.

This single block would pay for itself four times over: it gives §2.1's task distinctions a formal edge instead of a
prose one; it gives §2.2's Check2HGI equations their symbols; it lets §2.4 define the metrics over named sets; and it
lets Chapters 3-5 write their equations against a notation the reader already holds. It also states
the $|\mathcal{P}| \gg |\mathcal{R}| > |\mathcal{K}|$ relation that §2.1 currently conveys with the vaguer "tens of
thousands ... seven ... a few hundred to several thousand".

Two cautions for whoever drafts it. First, the notation must be **checked against Chapters 3-5 as committed** and
adopted consistently, or the chapter will introduce symbols the papers contradict — this is a cross-chapter edit, not a
Chapter 2 edit. Second, `GLOSSARY.md` is fail-closed and the terms used in the block must be registered before they
appear.

### G8. §2.3 lacks formal definitions of MTL, formulas, and elaborated debate; too much MTL+POI and too little MTL itself; and the loss-conflict / gradient-cosine discussion is missing, which leaves MobiWac's orthogonal-loss-cosine result uncontextualized

**Verdict: strongly agree, all four parts. Required. This is the most consequential content gap in the chapter.**

Taking his four claims in turn, because they are separable and the last is the sharpest:

1. **No formal definition of MTL.** Correct. §2.3 defines MTL in one prose clause ("trains one model on several related
   tasks at once, in the expectation that a representation shared among them generalizes better") and never writes the
   objective. For a dissertation whose research question is whether MTL helps, the total loss is the one equation the
   reader most needs. It should appear here:
   $\mathcal{L}_{\text{total}} = \sum_{i=1}^{T} w_i \mathcal{L}_i$ over $T$ tasks with weights $w_i$ — because every
   balancer the section then names is a different answer to "how are the $w_i$ set", and without the equation that
   entire family has nothing to attach to. This is also what makes
   `sener2018mgda`'s multi-objective point legible: the criticism is precisely that this scalarization presumes a single
   optimum.

2. **Too little MTL itself.** Partially correct as stated, and I would sharpen it. §2.3 actually spends most of its
   length on MTL machinery — a sharing-spectrum paragraph and a twelve-method balancer paragraph — and only one
   paragraph on MTL+POI, so the raw proportion is the opposite of his impression. But his underlying point stands: the
   section *lists* MTL rather than *treating* it. The balancer paragraph names uncertainty weighting, GradNorm, DWA,
   PCGrad, CAGrad, Nash-MTL, Aligned-MTL, and FAMO in eight consecutive sentences of identical shape, with no taxonomy
   and no equation. It reads as a catalogue, which is why it leaves an impression of thinness despite its length. Fix:
   group them under the two mechanisms they actually divide into — **loss-weighting** methods that set $w_i$
   (uncertainty weighting, DWA, RLW) versus **gradient-surgery** methods that modify the update direction (PCGrad,
   CAGrad, Nash-MTL, Aligned-MTL, MGDA), with FAMO as the efficiency-motivated case — and give one representative its
   formulation rather than giving twelve a sentence each. Depth over enumeration.

3. **Who defined what.** Agreed and easy: the section cites architectures and balancers without ever crediting the
   lineage. `caruana1997multitask` is cited once at the top and `ruder2017mtloverview` once for the hard/soft
   distinction, and thereafter methods appear without provenance. One or two sentences of intellectual history (hard
   sharing from Caruana's original formulation; the soft/structured line through cross-stitch to MMoE and PLE; the
   balancer line as a response to negative transfer) would give the catalogue a spine.

4. **Loss conflict, how it is measured, and the gradient cosine — the sharpest point.** He is right, and the consequence
   is concrete. §2.3 states that tasks "pull the shared parameters in different directions" and that they "conflict",
   but **never defines what conflict is or how it is measured**. The standard measure is the cosine similarity between
   per-task gradients, negative cosine meaning conflict; that definition is what PCGrad's projection, CAGrad's ball
   constraint, and Aligned-MTL's condition number are all built on, so the balancer paragraph is currently describing
   solutions to an unquantified problem. And as Germano says, MobiWac reports a gradient-cosine value — the project's
   own records carry a near-zero figure (+0.001) for the joint model — which lands in that paper as a bare number with
   no definition behind it. A reader who wants to know whether +0.001 is good, bad, or meaningless has nowhere to look.

   This is the cleanest example in either review of a fundamentals chapter failing at its actual job: a shared concept
   used by a paper chapter is undefined in the frame. Fix: two or three sentences in §2.3 defining gradient conflict as
   the cosine between task gradients, stating that near-zero means the tasks are close to orthogonal (neither
   reinforcing nor conflicting), and noting that this is the quantity the gradient-surgery balancers act on. Chapter 5's
   number then has a definition to point back to.
   **[VERIFY: the +0.001 figure and its exact convention must be re-read from the Chapter 5 source before Chapter 2 describes what it measures — I did not re-derive it this session.]**

### G9. "O foco na fundamentação teórica tem que ser em criar uma narrativa lógica, com blocos de definições formais"

**Verdict: agree, and this is the correct synthesis of his other points. Required, as a drafting principle.**

This sentence is the whole review in one line, and it names the axis on which our chapter is weakest. The chapter has
the narrative — it is, if anything, unusually strong on narrative, because it was written to make three papers read as
one argument. What it lacks is the **formal blocks**: no notation, no task formalization, no MTL objective, no conflict
measure, no metric definitions in symbols. The result is a chapter that reads like a well-argued essay rather than a
reference the later chapters can lean on.

The comparative evidence (Part III) says the same thing from the outside: our chapter has five sections and **zero
subsections**; the approved same-advisor precedent has five sections and **nineteen subsections**. Narrative and formal
blocks are not in tension — Viegas has both, and so does Germano's own review chapter. Recommend treating G7, G8 and G9
as one work item: add the formal blocks, and let them carry the definitional load the prose is currently carrying alone.

---

## Part III — Comparative analysis against `exemples/`

I read all five. Four are PDFs (Canesche 2021, LapsusVGI/Dorigueto, Passe, Viegas) and one is a LaTeX source tree
(Germano). Measurements below were taken this session; page and word counts are from the PDFs' extracted text, so treat
them as close approximations.

**The calibration point that matters most is Viegas** — same advisor, same program, English, coletânea, approved 2026 —
and it is measurably different from our chapter in one respect:

|                            | Viegas Ch.2              | Germano review ch. | **Our Ch.2**        |
|----------------------------|--------------------------|--------------------|---------------------|
| Sections                   | 5                        | 6                  | **5**               |
| Subsections                | **19** (3-5 per section) | **18**             | **0**               |
| Length                     | ~13 pages / 4,183 words  | ~15,700 words      | ~4,456 words        |
| Citation density           | ~1 per 37 words          | dense              | **~1 per 64 words** |
| Numbered equations         | 3                        | 20                 | 3                   |
| Closes each area with role | §2.1.5 "Relevance"       | -                  | one §2.5 for all    |

Five observations worth acting on, and one pattern I would **not** copy.

**1. Two heading levels, not one. (Required.)** This is the clearest single lesson. Viegas's Ch.2 is about the same
length as ours but carries 19 subsections; ours carries none, so five long sections each run as continuous prose with
paragraph breaks as the only structure. In a chapter whose purpose is *reference*
— the reader arrives from Chapter 5 wanting the definition of Acc@10 or of negative transfer — the absence of subsection
headings makes it unnavigable, and it is the reason G7's and G8's missing definitions have nowhere obvious to go.
Concretely: §2.1 splits into task definitions / notation and problem statement / next-place literature; §2.2 into
symbolic-to-distributed / graph representations / infomax objectives / the static-vector limit / the check-in level;
§2.3 into definition and objective / sharing architectures / conflict and negative transfer / balancing methods / MTL in
mobility; §2.4 into datasets / metrics and reference points / validation protocol / statistical tests. The prose barely
changes; the chapter becomes usable.

**2. Close each area by stating its role. (Recommended.)** Viegas ends §2.1 with an explicit "2.1.5 Relevance"
subsection rather than deferring all role-statement to the end of the chapter. We concentrate all of it in §2.5. Since
our §2.5 must also carry the pressing-need hinge, one or two sentences at the end of each of §2.2/§2.3/§2.4 saying what
that area contributes to *this* work would relieve §2.5 and stop the reader having to hold four sections' worth of
relevance in suspense. Our §2.2 partly does this already; §2.3 and §2.4 do not.

**3. Formal definition blocks in a mobility context. (Required — same as G7.)** Germano's `2_havana.tex`
supplies the model to follow: check-ins as a set, POI as a tuple, user history as a sequence, then the task stated over
those symbols. It is compact, it is in our exact domain, and it is from our own program.

**4. Citation density. (Recommended.)** Viegas cites roughly twice as often per word as we do (~1 per 37 words vs ~1 per
64). I would not chase the ratio for its own sake — our chapter is deliberately thin and every citation in it is
verified — but the gap is largest exactly where F28 and G8 independently found gaps: MTL-for-POI coverage and MTL
foundations. Closing those two gaps closes most of the density gap, so this is a consequence of acting on F28/G8 rather
than a separate task.

**5. Name the venue where a chapter's work was published, inline. (Optional.)** Passe's §1.3 names each article's venue
as it introduces the corresponding chapter. Our lineage table cites `silva2025mtlnet`
bibliographically but shows ST-MTLNet only as "Chapter 4", which is part of what makes F27's column look inconsistent.
Naming both published venues in the table or its caption would help the examiner see the publication record at a glance.

**The pattern I would not copy.** Canesche, LapsusVGI and Passe all place background *inside* the article chapters or in
a chapter titled "Background" that mostly serves one paper, and LapsusVGI has no shared theory chapter at all. That is a
legitimate coletânea shape at UFV, but it is not ours: our whole reason for a Chapter 2 is to de-duplicate theory across
three papers whose related-work sections overlap heavily. Viegas and Germano are the right models; the other three are
useful mainly as evidence that the program accepts a wide range of shapes.

---

## Part IV — My own review of the chapter

Findings the two reviewers did not raise. Numbered M1-M10 for reference; severity in bold.

### M1. Method content has migrated into the frame chapter. **Required.**

§2.2 now carries three display equations for the Check2HGI loss (the boundary-weighted sum, the bilinear discriminator,
the per-boundary term) and a paragraph deriving the joint model's relation to MTLnet from class inheritance in the
released code. Both are marked `[NEEDS SIGN-OFF]`, both are argued in their comments as belonging in the frame, and I
think that argument is half right and half wrong. It is right that the *relation* between two chapters' artifacts is the
frame's subject. It is wrong that the frame is the place for the artifacts' internals. As committed, §2.2 tells the
reader what $\mathbf{W}$ and $\sigma$
are in our discriminator before it has told them what a check-in is formally (G7) — internals before notation, method
before concept.

This is the same boundary problem Germano identified locally at G3 (the HGI sweep) and G5 (the Ch.3/4 walk-through).
Three separate instances in one section is a pattern, not three accidents. Recommendation:
adopt one explicit rule for Chapter 2 and apply it to all of them — *the frame states what a thing is and what role it
plays across chapters; the chapters state how their own thing is built.* Under that rule the Check2HGI equations and the
class-inheritance detail move to Chapter 5, the HGI sweep moves to Chapter 5, the Ch.3/4 mechanics compress to one
claim, and §2.2 keeps the conceptual line — which is what makes it the strongest section in the chapter when it is not
carrying method.

I note the counter-argument recorded in the source comments: Chapter 5 is under review, so adding an equation there is a
change to submitted text. That is a real constraint but it argues for putting the equation in an **appendix of the
dissertation** (there are already five), not for putting method internals in the frame.

### M2. §2.5 contradicts §2.4 on the validation protocol. **Required.**

§2.4 does careful scoping work: it states that Chapter 3 does not identify its split axis, Chapter 4 is stratified by
sample rather than by user, and only Chapter 5 splits by user, and that significance tests license verbs "in Chapter~
\ref{ch:mobiwac} alone". §2.5 then writes, unqualified:

> "User-disjoint cross-validation, macro-F1 and Acc@10 read against named floors and the single-task
> ceiling, and verbs bound to paired tests and to non-inferiority testing are what separate a real
> improvement from a hopeful one."

Read on its own — and §2.5 is the section a hurried examiner reads — this asserts user-disjoint cross-validation and
paired testing as the dissertation's practice, which §2.4 has just said is true of one of three studies. The honesty
machinery of this dissertation is one of its strengths and this sentence quietly spends it. Fix: "The protocol of the
final study is the last piece: user-disjoint cross-validation, ... Earlier studies used weaker protocols, as Section~
\ref{sec:fund:eval} records, and their conclusions are reported for the configurations they tested."

### M3. The chapter opening does not tell the reader what kind of chapter this is. **Recommended.**

The opening paragraph lists what the five sections do, which is a roadmap, but never states the chapter's *function*:
that it de-duplicates background shared by three papers written separately, so that a reader of Chapters 3-5 can find
the shared concepts in one place. Viegas's Ch.2 opens by naming its function ("establishes the theoretical foundation
for understanding..."), and ours would benefit more than most because the coletânea format makes the function unusual.
One sentence.

### M4. "Two check-in datasets serve as the ground" is still doing too much work. **Recommended.**

The panel review fixed the count (Gowalla + Massive-STEPS are the two used; Foursquare is context). The sentence that
remains is nonetheless odd in three ways: "serve as the ground" is the metaphor register F30 objects to; Gowalla is
called "the dataset of record" without saying record *of what*; and the paragraph gives no scale — no check-in counts,
no user counts, no date ranges — for datasets the whole dissertation rests on. A fundamentals chapter should let the
reader size the evidence. Recommend one sentence of scale per dataset, quoted from the chapters that compute it (not
recomputed here), or an explicit forward reference to where the numbers live.

### M5. Acc@10's choice of $k=10$ is unexplained. **Recommended.**

§2.4 defines Acc@10 and names it the primary region metric, but never says why ten. With region label spaces running
from a few hundred to several thousand classes, $k=10$ is a substantive choice — it is roughly 2% of Istanbul's label
space and a fraction of a percent of California's, so the same metric name means quite different things across datasets.
One clause justifying $k$ (a shortlist a mobility-aware service could act on) and acknowledging that its stringency
varies with $|\mathcal{R}|$ would close a question an examiner is likely to ask. This connects to the notation proposed
in G7: with $\mathcal{R}$
defined, the point can be made precisely.

### M6. The majority-class floor is named but not quantified; the Markov floor is cited for a different task.

**Recommended.**

Two small precision issues in the reference-points paragraph. First, the majority-class floor is defined ("always
predicts the most frequent category") but never given a value, though §2.4 states two sentences earlier that Food is
roughly a third of check-ins in a representative state — so the floor is roughly a third for accuracy, and much lower
for macro-F1, and saying so makes the floor useful rather than nominal. Second, `gambs2012mmc` is cited for the mobility
Markov chain as "the corresponding non-learned floor for the sequential targets", but our own ledger records that Gambs
et al. target next **place**. Adapting a place-level baseline to category and region prediction is legitimate and
probably what was done, but the sentence should say that it is an adaptation rather than implying the cited work
supplies a floor for our tasks.

### M7. "the relative multi-task performance change" is defined loosely for a metric that carries a sign.

**Recommended.**

§2.4 describes $\Delta m$ as "the average per-task percentage by which the joint model leads or trails the dedicated
single-task models" and adds that "a positive value is a lead only when each per-task change is itself established". The
care is welcome, but the definition is ambiguous exactly where $\Delta m$ is error-prone: Maninis et al. define it as an
average **drop** relative to single-tasking, so the sign convention is the opposite of the intuitive one, and our own
ledger records that we invert it. A chapter that defines the metric should state its own convention explicitly in the
prose — "positive values denote an advantage for the joint model, which inverts the sign convention of the original
definition" — rather than leaving it to an addendum. This is the kind of detail a reader checking Chapter 5's table
against Chapter 2's definition will catch.

### M8. `kohavi1995crossval` remains a soft citation for a load-bearing claim. **Recommended (author decision).**

The ledger records this one honestly: the claim is graded PLAUSIBLE, resolved through a Zenodo re-deposit identifier
rather than the original IJCAI-95 record, and the original text was never opened. It is cited for stratified k-fold
cross-validation, which is the backbone of the validation protocol. Either open the original and confirm, or cite a
source whose record is unambiguous for the stratification claim. Leaving a PLAUSIBLE grade on the protocol paragraph is
the one citation-integrity soft spot left in a chapter that is otherwise clean.

### M9. `wongso2025massivesteps` is a preprint carrying a dataset the dissertation evaluates on. **Recommended.**

Massive-STEPS supplies the Istanbul data, i.e. one of the two evaluation grounds, and it is cited as arXiv:2505.11239.
Before the defense, check whether a peer-reviewed version exists and cite that; if none does, the chapter should say the
benchmark is a preprint at the point where it introduces the data, so the examiner learns it from us rather than from
the bibliography.

### M10. Metaphor density is the chapter's most identifiable stylistic signature. **Recommended.**

Extending F30 with a full sweep: "serve as the ground", "that protocol is the last piece", "belong with that use", "is
the hinge of the representation argument", "the representation is the lever" (twice), "not a catalog", "only pays off
if", "a balancer earns its place", "the opening the dissertation addresses",
"license the verbs" (twice). Each is defensible alone; at this density in 4,500 words they are a signature, and F30
shows a reviewer reacting to it. One pass converting the load-bearing ones to plain statements — keeping one or two as
deliberate rhetoric — would remove the tell without flattening the prose. Note the chapter is already clean on the
mechanical checks (no em-dashes, no contractions, no banned vocabulary list items), so this is the layer below the
checklist, which is exactly where a human reviewer's judgment is worth more than a script's.

---

## Consolidated work list

Ordered by what I would do first. "R" = Required, "Rec" = Recommended, "O" = Optional.

| #  | Item                                                                                                             | Source       | Sev   |
|----|------------------------------------------------------------------------------------------------------------------|--------------|-------|
| 1  | Name Check2HGI as our contribution in its first clause                                                           | F26, G6      | **R** |
| 2  | Add the notation / problem-statement block (check-in, place, region, history, the three tasks)                   | G7, Part III | **R** |
| 3  | Add subsections throughout (two heading levels)                                                                  | Part III     | **R** |
| 4  | §2.3: MTL objective equation; group balancers by mechanism; define gradient conflict via the cosine              | G8           | **R** |
| 5  | Move the HGI sweep numbers out of §2.2 (keep the conceptual qualification)                                       | G3           | **R** |
| 6  | Fix the §2.5 / §2.4 protocol contradiction                                                                       | M2           | **R** |
| 7  | Restructure the encoder paragraph; move FiLM to §2.3; compress the Ch.3/4 mechanics                              | G5           | **R** |
| 8  | Extend MTL-for-POI coverage (`Zhang2020`, `wang2025hamtl`, `Halder2021/2022`, `Xu2023` as MTL) — abstracts first | F28          | **R** |
| 9  | Add Scarselli 2009 and Bruna 2014 to the GNN paragraph (two new bib entries)                                     | G1           | **R** |
| 10 | Split the lineage table's Reference column; confirm F27's intent with Fabrício                                   | F27          | **R** |
| 11 | Replace "fixes both"                                                                                             | F29          | **R** |
| 12 | Replace "license the verbs" (both instances), keeping the verb-to-test rule                                      | F30          | **R** |
| 13 | Standardize POI by the compound-modifier rule; register it in `GLOSSARY.md`                                      | F25          | **R** |
| 14 | Decide the frame/method boundary and apply it to all method content in §2.2                                      | M1           | **R** |
| 15 | Make the DGI/HGI roles explicit; keep "extends"                                                                  | G2           | Rec   |
| 16 | Delete "Two qualifications belong with that use."; keep and merge the HGI-roles sentence                         | G4           | Rec   |
| 17 | State the chapter's function in the opening paragraph                                                            | M3           | Rec   |
| 18 | Dataset scale sentences; justify $k=10$; quantify the majority floor; mark the Markov floor as adapted           | M4, M5, M6   | Rec   |
| 19 | State the $\Delta m$ sign convention in prose                                                                    | M7           | Rec   |
| 20 | Metaphor-density pass                                                                                            | F30, M10     | Rec   |
| 21 | Resolve `kohavi1995crossval`; re-check Massive-STEPS for a peer-reviewed version                                 | M8, M9       | Rec   |
| 22 | Close each of §2.2/§2.3/§2.4 with its role                                                                       | Part III     | Rec   |
| 23 | Name both published venues in the lineage table                                                                  | Part III     | O     |

### Open `[VERIFY]` flags this audit raises

1. **`wang2025hamtl` and `Zhang2020` abstracts were not opened** (OpenAlex search returned empty for these titles;
   Semantic Scholar returned HTTP 429). Their attributes above come from `src/references.bib`. Open both before either
   is cited for a claim — in particular, check whether `wang2025hamtl` treats a region-like unit as an end target, since
   §2.3's novelty sentence turns on it.
2. **Scarselli author list** — I read four authors from Crossref; the paper has five (Monfardini). Complete from IEEE
   Xplore before committing the entry.
3. **The gradient-cosine figure** referenced under G8 must be re-read from the Chapter 5 source with its exact
   convention before §2.3 describes what it measures. I did not re-derive it this session.
4. **The HGI sweep's F1 averaging convention** (macro vs weighted) is still unresolved in the source
   `[VERIFY]`. It must be settled before those numbers appear anywhere, including after a move to Chapter 5.
5. **F27's intent** — confirm with Fabrício whether he saw unresolved `??` references in a built PDF or was reacting to
   the mixed Reference column. The `\ref` keys themselves are correct as committed.

_Audit performed by the Claude Science research assistant. Nothing above was applied to the chapter; every item is a
proposal for the author. The comparative measurements and every citation attribute stated as verified were derived this
session from the repository or from the source of record, and the five
`[VERIFY]` flags mark exactly what was not._

---

# Codex Audit — Addendum (2026-07-28): Germano's flow point, and item G10

Two additions in response to the author's clarification: (1) G3 is a **flow** complaint, not a placement complaint, and
it generalizes — so this addendum audits paragraph-to-sentence connective tissue across the whole chapter; (2) the item
added at `CONSIDERATIONS.md:54-57` (the task-conflict discussion) was not covered by the original audit and is treated
here as **G10**.

## Part V — The flow audit (generalizing G3)

**Re-reading the objection.** I first read G3 as "this passage sits in the wrong chapter" and recommended moving it.
That reading was too narrow. The author's clarification is that the sentence *"está jogado no texto e não tem conexão
com o resto"* points at something more general: the chapter accumulates correct information without building a
continuous line of argument between the pieces. That is a different and more serious finding than a misplaced paragraph,
because moving one passage would not fix it.

To test the claim rather than assert it, I measured the chapter's connective structure: 27 paragraphs across the five
sections, tracking each paragraph's length, its opening sentence, its closing sentence, and — inside the longest
paragraphs — every sentence that begins a new topic with no stated relation to the sentence before it. Numbers below are
from that pass.

### V.1 The chapter's paragraphs are long, and five are outliers. **Required.**

Mean paragraph length is **161 words**, median 150. Five paragraphs exceed 240 words:

| Section | Para | Words   | Sentences | What it covers                                                                                                      |
|---------|------|---------|-----------|---------------------------------------------------------------------------------------------------------------------|
| §2.2    | P3   | **323** | 12        | MINE -> Deep InfoMax -> DGI -> HGI -> HGI's role here -> repurposing caveat -> the w_r sweep                        |
| §2.4    | P5   | 311     | 9         | user-disjoint splitting -> per-chapter protocol scoping -> Wilcoxon -> the p floor -> Holm -> TOST -> the verb rule |
| §2.4    | P3   | 277     | 9         | class imbalance -> macro-F1 -> class-weighting finding -> Acc@10 -> OOD regions -> Delta_m                          |
| §2.3    | P4   | 273     | 9         | eight balancers -> three skeptical results -> two surveys -> the dissertation's position                            |
| §2.2    | P5   | 257     | 11        | five encoders -> FiLM -> Ch.3 and Ch.4 mechanics                                                                    |

A 300-word paragraph carrying six or seven topics has no controlling idea, which is precisely the reading experience
Germano reports. **The sentence he objected to is the twelfth sentence of the chapter's longest paragraph** — by the
time the reader reaches it, the paragraph has already changed subject three times, so the sweep does not feel "thrown
in" because of its content but because nothing has prepared its arrival. This is why the flow diagnosis matters more
than the placement one: fixing the paragraph structure fixes the symptom he reported *and* four others he did not reach.

### V.2 §2.2 P3 is the worst case and should become three paragraphs. **Required.**

Its twelve sentences, in order: (s1-s2) labels are scarce so the objective must be unsupervised; (s3-s4)
MINE and Deep InfoMax, then DGI; (s5) DGI's role in this project; (s6-s7) HGI extends the objective; (s8)
HGI's two roles here; (s9) an announcement of two qualifications; (s10) the repurposing caveat; (s11-s12)
the retuning and the sweep. Three distinct jobs are being done: **defining the infomax family**, **stating what this
project uses each member for**, and **qualifying the baseline**. Split accordingly:

- **P3a (the objective).** Labels are scarce; MI can be estimated and maximized by gradient descent; Deep InfoMax makes
  it a representation learner; DGI carries it to graphs; HGI extends it across the POI-region-city hierarchy. One topic:
  how a representation is learned without labels. Ends at the hierarchy, which sets up the next paragraph.
- **P3b (what this dissertation uses them for).** DGI supplies the place embeddings of the first study; HGI supplies the
  place-level baseline the later chapters measure against and is the direct base of the check-in-level representation.
  One topic: roles in this work. This is also where G2's role clarification belongs, and where G4's announcing sentence
  can simply be deleted.
- **P3c (the qualifications).** Huang et al.\ built HGI for urban region representation, so its POI-level output is
  repurposed here; and the baseline was retuned rather than taken as published, with the sweep reported where the
  numbers live (see the G3 follow-up: an appendix). One topic: the caveats attached to using someone else's
  representation as a baseline.

Under this split the sweep sentence has a home with a stated purpose, and even if the author chooses to keep the numbers
in Chapter 2, they no longer read as thrown in — they are the evidence for the paragraph's own claim. That is the more
important point: **P3c is the fix for G3 even without moving anything.** The move remains preferable, but the split is
what removes the incoherence.

### V.3 Sixteen of 27 paragraphs open without a back-link. **Recommended.**

An opening sentence that begins with `This`, `That`, `Two observations from that line`, `Before that step`
carries the reader forward; one that opens on a fresh noun phrase makes the reader supply the connection. Sixteen
paragraphs do the latter, including several where a link exists and is simply unstated:

- §2.2 P4 "A place embedding, however it is trained, shares one property..." — follows the HGI paragraph and is *about*
  the limitation of what preceded, but does not say so. Compare: "Every representation in that line, however it is
  trained, shares one property..."
- §2.4 P3 "The category label distribution is imbalanced." — follows the datasets paragraph; the imbalance is a property
  of those datasets, which the sentence does not say. Compare: "In those datasets the category labels are unevenly
  distributed."
- §2.3 P2 "Deep MTL is organized around how much the tasks share." — follows the paragraph that poses the research
  question; the organizing axis is the answer's precondition, unstated.
- §2.5 P3 "Multi-task learning is the mechanism that would let the two tasks share..." — follows the representation
  paragraph; the two are the second and third steps of one argument.

Not every paragraph needs a back-link, and a chapter where all 27 began with "This" would be worse. But 16 of 27 is the
mechanical signature of what Germano is describing: paragraphs assembled as independent units rather than written as a
sequence.

### V.4 Catalogue paragraphs: eight consecutive cold-start sentences in §2.3 P4. **Required.**

The balancer paragraph runs: *Uncertainty weighting sets... GradNorm rescales... Other methods act on the gradient
directions: PCGrad projects... CAGrad maximizes... Nash-MTL treats... Aligned-MTL aligns... FAMO reduces...* Eight
sentences of identical shape, each introducing a method with no relation to the previous one except membership in the
list. Only s4 ("Other methods act on the gradient directions") supplies any structure. §2.2 P5 has the same shape for
the five encoders.

This is the same defect as G5's "artigos aparecem jogados um atrás do outro" and G8's "pouco sobre MTL em si", and the
fix is the one proposed there: replace enumeration with a stated taxonomy plus depth on one representative. Concretely
for §2.3 P4 — two paragraphs, one per mechanism, each opening with the mechanism rather than with a method name:

> "One family sets the weights $w_i$ and leaves the gradients alone. Uncertainty weighting derives each
> weight from the task's homoscedastic uncertainty, learned jointly with the model \cite{kendall2018uncertainty};
> dynamic weight averaging derives it from the recent rate of change of each loss \cite{liu2019dwa}; and
> random loss weighting shows how strong a naive version of this idea already is \cite{lin2022rlw}.
>
> A second family leaves the weights alone and modifies the update direction, acting on conflict as defined
> above. PCGrad projects one task's gradient off any conflicting task's gradient \cite{yu2020pcgrad}; CAGrad
> maximizes the worst per-task improvement within a ball around the average gradient \cite{liu2021cagrad};
> Nash-MTL treats the combination as a bargaining game \cite{navon2022nashmtl}; and Aligned-MTL aligns the
> principal components of the gradient system \cite{senushkin2023aligned}. FAMO belongs to neither family
> in spirit: it targets the cost of balancing rather than the conflict itself \cite{liu2023famo}."

The reader now has two boxes to put twelve methods in, and each sentence says how its method relates to the family it is
in. Same citations, same length, continuous line.

### V.5 A concrete flow check to run before the chapter is considered done. **Recommended.**

For the future editing agent, a test that is cheap and catches exactly this class of defect. For each paragraph, in
order: (a) state its controlling idea in one clause — if that takes two clauses, the paragraph holds two paragraphs; (b)
check that its first sentence names or implies the previous paragraph's subject; (c) check that its last sentence sets
up the next paragraph's subject; (d) inside the paragraph, check that no sentence introduces a proper noun or a number
whose relevance the paragraph has not established. The sweep sentence fails (d) and its paragraph fails (a) — which is a
compact statement of Germano's objection and shows the objection is testable rather than a matter of taste.

## Part VI — Item G10: the task-conflict finding (`CONSIDERATIONS.md:54-57`)

> "Discussão extra trazida pelo Germano: o nosso achado que as duas tarefas next-region e next-category
> sobre os nossos modelos não entram em conflito no nosso modelo MTL pode ser estendido em um trabalho
> futuro sobre se isso é algo que podemos afirmar de forma mais global. O Germano ainda argumenta que ele
> sente falta de uma argumentação mais técnica e com dados sobre a prova que em nosso modelo essas tarefas
> não entram em conflito."

**Verdict: agree on both halves, and the second half is a live risk that should be treated before the defense.
Required (the evidence framing); Recommended (the future-work item).**

Two claims to separate: that the non-conflict finding should be flagged as future work, and that the current evidence
for it is technically thin.

### G10.1 The evidence is thinner than the claim, and I can state exactly how thin. **Required.**

I traced where this claim lives. It is **not** in Chapter 2 or Chapter 5 — it is in
`6_conclusion.tex:202-210`, and reads:

> "The gradient-level picture is consistent with this reading, within its measurement scope. During
> development, on an earlier preparation of the data, the cosine similarity between the two tasks' gradients
> averaged $+0.001$ over four seeds on four Gowalla states, three of which are among the five we report,
> directional conflict only, a finding for this pair of tasks rather than a general rule. Under the
> check-in-level representation the two sequential tasks coexist with essentially orthogonal gradients:
> sharing stopped hurting."

The passage is already commendably hedged — "within its measurement scope", "an earlier preparation of the data", "a
finding for this pair of tasks rather than a general rule" — and a source comment records that the pool is four Gowalla
states (AL, AZ, GA, FL) of which **GA is not one of the dissertation's six datasets**. So Germano's instinct is correct,
and the specific gaps are:

1. **The measurement is off the reported configuration.** It was taken during development on an earlier data
   preparation, on a state set that only partly overlaps the six datasets, over four seeds. The dissertation's results
   are not computed on that pool.
2. **Istanbul is absent.** The claim is about "the two tasks", but the evidence is Gowalla-only. The non-United-States
   dataset — the one that tests whether anything generalizes — contributes nothing to it.
3. **A single averaged number cannot support "essentially orthogonal".** $+0.001$ is a mean; without a spread, a
   distribution over training steps, or a per-state breakdown, the reader cannot tell whether the gradients are
   consistently orthogonal or strongly conflicting in both directions and cancelling in the average. Those are different
   findings with different implications, and the mean does not distinguish them. This is, I think, the technical gap
   Germano is pointing at.
4. **Chapter 2 never defines the quantity.** This is G8's fourth point and it compounds the problem: the frame chapter
   discusses conflict qualitatively for a whole paragraph and defines the cosine nowhere, so when $+0.001$ appears in
   Chapter 6 the reader has no definition to read it against, and no basis for knowing that zero is the interesting
   value.

**Recommendation, in order.** (a) Define gradient conflict in §2.3 as the cosine between per-task gradients, state that
negative means conflicting and near-zero means close to orthogonal — this is G8.4 and it is the prerequisite for
everything else. (b) In Chapter 6, either strengthen the evidence or weaken the sentence. Strengthening means
recomputing the cosine on the reported configuration, over the six datasets including Istanbul, and reporting a
distribution rather than a mean — a per-dataset figure with a spread, ideally a histogram over training steps, would
turn an anecdote into a result and is a genuinely interesting one. Weakening means calling it explicitly what it is: *"a
development-time observation on an earlier data preparation, offered as consistent with the interpretation rather than
as evidence for it."* (c) Do not leave it in the middle: an unqualified "essentially orthogonal gradients" resting on
one mean from a partly-different data pool is the kind of sentence a committee asks about, and the answer would have to
be the qualification, so it is better to write the qualification first.

**[VERIFY]** I did not re-derive the $+0.001$ figure, its spread, or its provenance beyond the chapter source and its
comments. The referenced pool file (`R0_matched_metric_bar.json`) and the per-state values must be re-read before any
strengthened statement is written.

### G10.2 The generalization question is a good future-work item, and it is better than most. **Recommended.**

Germano's suggestion — ask whether task non-conflict is a property of this task pair or something more general — is the
strongest future-work direction to come out of either review, for three reasons. It follows directly from the
dissertation's own answer (the arc concludes that the *representation* decides whether MTL helps, and the gradient
geometry is the mechanism that would explain why); it is measurable with machinery the project already has (the cosine
instrument exists; what is missing is coverage, not capability); and it inverts the dissertation's contribution in a
productive way — from "here is a representation that makes these two tasks compatible" to "here is a diagnostic for
predicting which task pairs a representation will make compatible", which is a more general claim than the thesis makes
and therefore a real research question rather than an increment.

Suggested framing for the future-work section, deliberately narrower than "study conflict in general":

> "Whether the near-orthogonality observed for this task pair is a property of the check-in-level
> representation or of these two targets specifically is open. A study that measured gradient alignment
> across several task pairings under the same representation, and across representations for a fixed
> pairing, would separate the two explanations and would test whether gradient alignment can be used to
> predict in advance which task pairs benefit from sharing."

Note this also gives the dissertation a principled reason for the negative result of Chapter 3 to be part of the story
rather than an embarrassment: if alignment depends on the representation, then a place-level representation producing
conflict and a check-in-level one producing orthogonality is the same finding measured twice. **If the author wants one
addition to the conclusion, this is the one I would make.**

### G10.3 Where G10 touches Chapter 2. **Required.**

Chapter 2 owns one piece of this: the definition. Adding the cosine definition to §2.3 (G8.4) is what makes Chapter 6's
number legible and what a future-work sentence about "gradient alignment" would point back to. Chapter 2 should **not**
report the $+0.001$ value or argue the finding — that belongs to the chapters that measured it. This keeps the
frame/method boundary of M1 intact: the frame defines the quantity, the chapters report their measurements of it.

## Revised work-list additions

| #  | Item                                                                                                                                                                   | Source             | Sev   |
|----|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|-------|
| 24 | Split §2.2 P3 into three paragraphs (objective / roles in this work / qualifications) — this is the structural fix for G3                                              | V.2                | **R** |
| 25 | Split the other four outlier paragraphs (§2.4 P5, §2.4 P3, §2.3 P4, §2.2 P5) by controlling idea                                                                       | V.1                | **R** |
| 26 | Rewrite §2.3 P4 and §2.2 P5 as taxonomy-plus-depth rather than enumeration                                                                                             | V.4                | **R** |
| 27 | Add back-links to the paragraphs where the connection exists but is unstated (§2.2 P4, §2.4 P3, §2.3 P2, §2.5 P3 at minimum)                                           | V.3                | Rec   |
| 28 | Define gradient conflict (cosine between per-task gradients) in §2.3; do not report the value in Ch.2                                                                  | G10.1, G10.3, G8.4 | **R** |
| 29 | Chapter 6: either recompute the cosine on the reported configuration with a per-dataset spread, or explicitly downgrade the sentence to a development-time observation | G10.1              | **R** |
| 30 | Add the gradient-alignment generalization to future work                                                                                                               | G10.2              | Rec   |
| 31 | Run the four-point flow check (V.5) over the chapter after the edits                                                                                                   | V.5                | Rec   |

_Addendum by the Claude Science research assistant, 2026-07-28. The paragraph and sentence measurements in Part V were
computed this session from `2_fundamentals.tex` as committed; the Chapter 6 passage in Part VI was read from
`6_conclusion.tex:202-210` and its source comments. Nothing has been applied to any chapter._

--

# Add by author after the last reviewers

1. On the MTL fundamentals that we need to improve do we talk about the optimality of pareto, and do we need to talk
   about it ? I have a feeling that since we talk a bit of the balancers we need at least breif take about this. 


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
