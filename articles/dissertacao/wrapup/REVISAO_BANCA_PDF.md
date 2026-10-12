# Revisão da banca — anotações do PDF

As 27 anotações do arquivo `dissertacao - vitor hugo (1).pdf` (revisor `alexb`, 26/08/2026).
Cada item traz **o trecho exatamente como foi destacado**, **o parágrafo em volta** (para o
comentário se ler sozinho, com o trecho destacado em negrito) e **o comentário do revisor**,
transcrito literal.

- **Fonte**: `~/Downloads/dissertacao - vitor hugo (1).pdf` — 119 páginas, 27 destaques (`/Highlight`),
  todos do mesmo revisor, feitos entre 08:06 e 10:58 de 26/08/2026.
- **IDs**: `B-01` … `B-27`, na ordem em que as anotações estão no arquivo (que é a ordem em que
  foram feitas). O número é fixo — se um item for resolvido ou descartado, marque o estado,
  **não renumere**.
- **Escopo**: o registo do PDF é literal e não se altera. Desde 2026-09-02 cada item traz também
  um **Parecer** com o que foi medido contra a árvore viva. Quatro itens foram tratados; a
  resposta dos restantes é decisão do autor antes do depósito.
- Dos 27 destaques, **19 têm comentário escrito** e **8 são apenas marcação de trecho** — estes
  aparecem como *destaque sem comentário*. (O cabeçalho dizia 18/9 até 2026-09-02: o B-20 tem
  comentário — a etiqueta "conclusão" — mas estava indexado como marcação. O verificador não
  apanha a discrepância porque confere o `/Contents` item a item, nunca a soma.)
- **Parecer (2026-09-02).** Cada item passou a trazer um bloco **Parecer** no fim: alvo em
  `ficheiro:linha`, o que foi medido, o custo, quem fecha e a recomendação. Onde diz ✅ FEITO, a
  alteração já está na árvore de trabalho. O parecer é uma leitura, não uma decisão — a decisão
  continua a ser do autor.

## Índice

Marque o `status` na tabela abaixo — é o único lugar de marcação, para não haver duas versões do
mesmo estado. Legenda:

> ## ✅ Os 27 estão decididos E aplicados. Nada aqui está pendente.
>
> Verificado a **2026-09-08 contra o texto vivo**, não contra este ficheiro. Os seis que ainda
> liam `✎` (*"vira errata no depósito"*) foram aplicados no commit **`3c0e4871`** de 02/09, cujo
> título é *"as seis últimas decisões do autor — nenhum dos 27 itens fica por decidir"*. O símbolo
> estava no futuro e o trabalho já era passado: **um registo que descreve um estado que já passou
> engana quem o lê**, e é a mesma família das armadilhas §13-14.
>
> | | pedia | está |
> |---|---|---|
> | B-08 | a §2.4 parece metodologia | o Cap. 2 diz porquê: *"…reads as a methods section, which is what it is"* |
> | B-14 | — | remissão para o B-15; nunca foi item |
> | B-15 | contra que alvo mediram o MTL? | a legenda declara a lacuna: *"which of the two targets stopped its clock is not recorded"* |
> | B-20 | *"consistently outperforms"* | *"in **most** of the evaluated combinations"* |
> | B-22 | cautela **do quê**? | *"**Two things age** with such a dataset…"* |
> | B-23 | melhorias **em relação a quê**? | *"two enhancements **to that earlier model**"* |
>
> O `verify_revisao_banca.py` passa: 27 itens, 27 destaques, 27 linhas de índice, zero falhas.

| marca | significado |
|---|---|
| `☐` | aberto — ainda não decidido |
| `✔` | resolvido no texto |
| `✎` | vira errata no depósito |
| `✅` | **errata já aplicada** — commit `3c0e4871`; nada por fazer |
| `✖` | dispensado — decisão de não mexer |
| `?` | precisa de medição ou consulta antes de decidir |

### O que falta decidir — estado a 2026-09-02, fim do dia

> **Fora destes 27, fecharam hoje**, e mudam o que alguns pareceres diziam: a errata do B-13
> (aplicada e registada em quatro sítios); as contagens de parâmetros, que estavam erradas **nos dois
> volumes**; a convenção de ênfase em seis tabelas, que é o que resolve o B-27 a sério; a promessa do
> Wilcoxon, retirada de quatro sítios; o Resumo e o Abstract, reescritos e aprovados; a frase do
> controlo de concatenação no Cap. 5, desmentida pela tabela da mesma página; e o TME.
>
> Nenhum resultado medido mudou em nenhum deles.


**Oito fechados** (`✔`): B-02, B-05, B-06, B-11, B-12, B-13, B-18, B-27.
**Dez dispensados** (`✖`) com razão medida e registada em cada parecer.
**Nove à espera do autor** (`?`), agrupados por custo:

| | itens | o que é preciso |
|---|---|---|
| **uma palavra ou três** | B-20, B-23 | B-20: *"consistently outperforms"* contra os 15/21 que o próprio parágrafo dá seis linhas abaixo. B-23: *"duas melhorias"* sem dizer em relação a quê. Ambos são prosa de artigo publicado, logo errata. |
| **uma frase no prefácio** | B-10, B-22 | Território da moldura, **custo de errata zero**. B-10: reconhecer a sobreposição com o Cap. 2. B-22: dizer o que envelhece com o Gowalla — a resposta é empírica e está no Cap. 5 (Istambul). |
| **uma frase na legenda** | B-14 + B-15 | São um item. A ambiguidade está na tabela de convergência, que tem **uma só linha MTL** sem dizer contra qual alvo. A resposta já está escrita duas linhas abaixo. Fica em aberto se o MTL tinha de atingir os dois alvos na mesma época — isso eu não consegui confirmar no código. |
| **precisa de literatura** | B-16 | O eixo espacial tem quatro alternativas citadas; o temporal tem só Time2Vec, em todo o documento. ⚠ Escrever no Cap. 4 colide com **LO-12, aberto**; escrever no Cap. 2 evita a colisão. |
| **estrutural** | B-08 | A §2.4 parece metodologia, e é. A rota barata existe e eu tinha-a descartado por engano: a secção é referenciada **cinco vezes, todas dentro do Cap. 2**. A rota cara (capítulo novo) parte os nove rótulos congelados do suplemento. |
| **reabre uma decisão tua** | B-01 | O Resumo não diz que o par de tarefas muda entre os estudos — e isso foi **escolha tua** (FAB-08, `content.tex:115-122`). A reformulação do Resumo de 02/09 nomeia as tarefas de cada estudo e define a região, portanto responde em parte sem tocar na omissão. Decidir se basta. |


| ID | status | pág. | seção | assunto do comentário | tipo |
|---|---|---|---|---|---|
| [B-01](#b-01) | ✔ | 4 | Resumo | "essas tarefas" — quais? frase ampla demais para o resumo | pergunta |
| [B-02](#b-02) | ✔ | 4 | Resumo | tese central do resumo | destaque sem comentário |
| [B-03](#b-03) | ✖ | 16 | 1 Introduction · Organization | resultado nulo tratado como achado | destaque sem comentário |
| [B-04](#b-04) | ✖ | 16 | 1 Introduction · Organization | representação de entrada como gargalo | destaque sem comentário |
| [B-05](#b-05) | ✔ | 16 | 1 Introduction · Organization | exemplo do almoço de terça vs. sábado à noite | clareza |
| [B-06](#b-06) | ✔ | 20 | 2.1.1.1 Check-ins and histories | dar exemplos concretos dos elementos de U, P, C, R | sugestão |
| [B-07](#b-07) | ✖ | 20 | 2.1 Point-of-interest prediction tasks | seção confusa, subníveis demais; fundamentar MTL antes | organização |
| [B-08](#b-08) | ✅ | 31 | 2.4 Datasets and evaluation | "Datasets and evaluation" parece metodologia, não fundamentação | organização |
| [B-09](#b-09) | ✖ | 37 | 3.1 Introduction (CBIC) | MTL não entrega os ganhos esperados | destaque sem comentário |
| [B-10](#b-10) | ✔ | 38 | 3.2 Theoretical Foundations and Related Work | redundância entre capítulos por ser coletânea de artigos | organização |
| [B-11](#b-11) | ✔ | 46 | 3.4.1 Dataset and Evaluation Metrics | por que 5-fold? | pergunta |
| [B-12](#b-12) | ✔ | 46 | 3.4.1 Dataset and Evaluation Metrics | check-ins do mesmo usuário em treino e validação | metodologia |
| [B-13](#b-13) | ✔ | 47 | 3.4.2.1 POI Category Classification | superação do HMRM em todas as categorias | destaque sem comentário |
| [B-14](#b-14) | ✅ | 49 | 3.4.3 Convergence Comparison | F1 alvo de 47 e 32,2 | destaque sem comentário |
| [B-15](#b-15) | ✅ | 50 | 3.4.3 Convergence Comparison | o alvo vale só para um dos modelos? | pergunta |
| [B-16](#b-16) | ✖ | 53 | 4.1 Introduction (CoUrb) | Time2Vec — havia alternativas? | discussão |
| [B-17](#b-17) | ✖ | 57 | 4.3 Methodology (Figura 2) | arquitetura parece igual à anterior; apontar as diferenças | apresentação |
| [B-18](#b-18) | ✔ | 62 | 4.4.1 Experimental Setup | por que 80/20? | pergunta |
| [B-19](#b-19) | ✖ | 63 | 4.4.2 POI Category Classification (Figura 3) | empilhar as figuras para aumentá-las | editorial |
| [B-20](#b-20) | ✅ | 65 | 4.5 Conclusion and Future Work | "conclusão" — ST-MTLNet supera o baseline DGI | marcação |
| [B-21](#b-21) | ✖ | 66 | 4.5 Conclusion and Future Work | DGI ainda captura melhor os deslocamentos longos | destaque sem comentário |
| [B-22](#b-22) | ✅ | 66 | 4.5 Conclusion and Future Work | o que é dependente entre modelo e dataset? | pergunta |
| [B-23](#b-23) | ✅ | 68 | 5.1 Introduction (MobiWac) | "duas melhorias" — em relação ao primeiro trabalho? | clareza |
| [B-24](#b-24) | ✖ | 72 | 5.4.1 The check-in-level representation | região e lugar da região não são dependentes? | pergunta |
| [B-25](#b-25) | ✖ | 72 | 5.4.1 The check-in-level representation | a palavra "tempo" | destaque sem comentário |
| [B-26](#b-26) | ✖ | 74 | 5.5.2 Windows, splitting, and the integrity of the representation | "Windows." solto — só fez sentido na página seguinte | editorial |
| [B-27](#b-27) | ✔ | 81 | 5.6.2 One model, two tasks (Tabela 10) | dois destaques em negrito embaixo e um só em cima | tabela |

---

## Resumo

### B-01
**Página 4 · Resumo · 26/08 08:06**

**Trecho destacado**

> Esta dissertação investiga se o aprendizado multitarefa (MTL) pode combinar essas tarefas em um único modelo e de quais escolhas de projeto depende o sucesso desse treinamento conjunto.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> Redes sociais baseadas em localização produzem registros de check-in, que associam um usuário, um ponto de interesse (POI) e um instante. Esses registros permitem tanto classificar a categoria de um POI quanto antecipar propriedades da próxima visita, como sua categoria e sua região. **Esta dissertação investiga se o aprendizado multitarefa (MTL) pode combinar essas tarefas em um único modelo e de quais escolhas de projeto depende o sucesso desse treinamento conjunto.** Embora as tarefas compartilhem dados e contexto, em um modelo multitarefa o compartilhamento de parâmetros também pode provocar transferência negativa. A investigação foi desenvolvida em três estudos sucessivos, organizados como um resultado negativo, seu diagnóstico e sua resolução. O primeiro estudo propôs o MTLnet, que utilizava uma representação em nível de POI e compartilhamento rígido de parâmetros para realizar classificação de categoria e previsão da próxima categoria. […]

**Comentário do revisor**

> quais tarefas?
>
> acho que a frase ficou muito ampla para o resumo

**Parecer** — *decisão tua · uma frase, em duas línguas*

Alvo: `src/content.tex:128-130`, com espelho inglês em `:220-223`.

Ele tropeçou numa omissão que **tu decidiste manter**. A nota em `content.tex:111-121` regista, sob
pedido teu (round 10, FAB-08), que o Resumo deliberadamente não diz que o par de tarefas muda entre
os estudos — os Caps. 3/4 pareiam classificação estática + próxima categoria, o Cap. 5 pareia próxima
categoria + próxima região. Corrigir reabre essa decisão.

Se corrigires, a alteração tem de aterrar **nas duas línguas no mesmo commit** (WRITING_LAW §6,
registada em `content.tex:214-216`), e entra no mesmo bloco já mexido pela errata do Resumo de 21/08.

Nota de âmbito, medida: o bloco do Resumo está dentro de `\ifdefensebuild`, portanto **não aparece no
`build/main_academico.pdf`, que é o corpo do depósito**. Uma correcção aqui muda o PDF da defesa e o
texto que colas no formulário AcademicoPG, não o corpo depositado.

Nenhuma probe na janela.

> AUTHOR - Já foi resolvido no novo resumo.


### B-02
**Página 4 · Resumo · 26/08 08:08**

**Trecho destacado**

> MTL não constitui um benefício automático: sua efetividade depende da representação de entrada e da topologia de compartilhamento construída para as tarefas consideradas.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> […] Essas análises mostraram que o modelo conjunto superou os modelos dedicados na previsão da próxima categoria em todos os conjuntos e, na previsão da próxima região, superou-os ou foi estatisticamente não-inferior dentro da margem de dois pontos de Acc@10. Em ambas as tarefas, os resultados do modelo conjunto também ficaram acima dos reportados pelos métodos externos usados como referência. Os resultados mostram que o **MTL não constitui um benefício automático: sua efetividade depende da representação de entrada e da topologia de compartilhamento construída para as tarefas consideradas.**

**Comentário do revisor** — *nenhum: o revisor grifou o trecho sem escrever nada.*

**Parecer** — *nada a fazer, mas há um facto que precisas de saber*

Alvo: `src/content.tex:166`, espelho EN em `:262-267`. É a frase-tese do documento; marcação sem
comentário lê-se como sublinhado do ponto central, não como objecção.

**O que importa aqui não é o destaque — é o que está imediatamente antes dele.** O contexto
transcrito acima contém *"superou-os na previsão da próxima categoria **em todos os conjuntos**"*.
Essa é exactamente a frase que a errata de 21/08 corrigiu. Confirmado por extracção dos dois PDFs:

| | Resumo, próxima categoria |
|---|---|
| `src/banca.pdf` (16/08 — o que ele anotou a 26/08) | "superou-os … **em todos os conjuntos**" |
| `src/dissertacao.pdf` (21/08 — com a errata) | "**ele os superou em um conjunto**, enquanto as cinco diferenças restantes são equivalentes a zero dentro de meio ponto" |

**O revisor leu o Resumo por corrigir.** A errata entrou a 21/08 e o `banca.pdf` nunca foi
reconstruído — por desenho, é o registo congelado do que a banca recebeu.

A direcção é segura: a correcção **estreita** a afirmação, logo o texto aprovado dizia *mais* do que
o depositado vai dizer, e ninguém foi prejudicado. Mas se algum membro leu o Resumo como "funciona
em todo o lado", leu uma afirmação que tu já retiraste. Convém saberes isto antes de responderes ao
B-01 e ao B-02, que caem os dois nesse parágrafo.

A probe `A11-frame` cai na janela mas pina o parágrafo **anterior**, não esta frase.


---

## Capítulo 1 — Introduction

### B-03
**Página 16 · 1 Introduction · Organization · 26/08 08:12**

**Trecho destacado**

> The study treated this null result as a finding and proposed three possible explanations, including an input representation that might not provide enough information for both

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> Chapter 3, published at CBIC 2025, introduces MTLnet, the first joint model developed in this research. It combines a place-level graph embedding with hard parameter sharing, in which the tasks share one trunk of hidden layers and separate only at their output heads, and predicts category classification and the next category in a sequence. For that configuration, the joint model did not consistently outperform the two dedicated single-task models and required more training time. **The study treated this null result as a finding and proposed three possible explanations, including an input representation that might not provide enough information for both** tasks.

**Comentário do revisor** — *nenhum: o revisor grifou o trecho sem escrever nada.*

**Parecer** — *dispensar · a defesa já está escrita, noutro sítio*

Alvo: `chapters/1_introduction.tex:156-159`.

Duas leituras. Se ele estava só a marcar o momento retórico do arco (resultado negativo → diagnóstico
→ resolução), não há nada a fazer. Se estava a questionar se um resultado nulo pode ser apresentado
como "achado", **a resposta já existe**: o prefácio do Cap. 3 (`chapters/3_cbic.tex:30-34`) indexa a
conclusão no tempo — *"Its conclusions are the conclusions of the time, for the configuration studied
here"* — e `:35-39` nomeia os capítulos que revêem o veredicto. O prefácio está antes deste parágrafo
na ordem de leitura.

Par natural com o B-04: mesma página, mesmo minuto (08:12), os dois parágrafos do arco Cap. 3 → Cap. 4.


### B-04
**Página 16 · 1 Introduction · Organization · 26/08 08:12**

**Trecho destacado**

> Because the architecture remains fixed, the study identifies the input representation as the bottleneck for that stage of the research.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> Chapter 4, published at CoUrb 2026, examines that explanation through a controlled comparison. The study keeps MTLnet unchanged and replaces its monolithic 64-dimensional place embedding with separate spatial, temporal, and categorical encoders. Category performance then increases substantially in every scenario evaluated. **Because the architecture remains fixed, the study identifies the input representation as the bottleneck for that stage of the research.**

**Comentário do revisor** — *nenhum: o revisor grifou o trecho sem escrever nada.*

**Parecer** — *dispensar · a qualificação já está na própria frase*

Alvo: `chapters/1_introduction.tex:165-166`.

A objecção possível seria que a inferência "arquitectura fixa ⇒ a representação é o gargalo" só vale
*daquele estágio* — e a frase **já diz isso**: "for that stage of the research".

Uma observação que vale mais do que o item: este destaque é provavelmente a âncora que ele carrega
até ao **B-17** (*"ficou igual à arquitetura anterior; dá para apontar as diferenças?"*). Ele
percebeu que a arquitectura é mantida fixa de propósito, e o que quer é que a figura o mostre. Os
dois itens são o mesmo pensamento, a cinquenta páginas de distância.


### B-05
**Página 16 · 1 Introduction · Organization · 26/08 08:13**

**Trecho destacado**

> a representation that cannot tell a weekday lunch from a Saturday night out at the same place is working against both tasks at once.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> Chapter 5, submitted to MobiWac 2026 and under review, develops the resolution. Any place-level embedding assigns a place the same vector on every visit; **a representation that cannot tell a weekday lunch from a Saturday night out at the same place is working against both tasks at once.** That observation is the hypothesis the final study tests. It moves the representation to the check-in level: one vector per visit. Acting on another of the first study’s candidate explanations, it also replaces the shared hidden layers with cross-attention between task-specific streams, addressing the earlier concern about hard parameter sharing. […]

**Comentário do revisor**

> não entendi bem

**Parecer** — *✅ FEITO (2026-09-02)*

Alvo: `chapters/1_introduction.tex:172-174`. Reescrito.

Dois defeitos diagnosticados, ambos corrigidos:

1. **Ordem invertida.** A metáfora (almoço de terça vs. sábado à noite) chegava *antes* de o leitor
   saber o que é "check-in level"; a definição ("one vector per visit") só vinha duas frases depois.
   Agora o nível de check-in é definido primeiro e o exemplo ilustra-o.
2. **Personificação.** *"is working against both tasks at once"* — uma representação não trabalha
   contra nada. É a classe que a WRITING_LAW §1 já mandou corrigir noutro sítio
   (`2_fundamentals.tex:1727-1729`). Substituída pela cadeia causal: um vector para duas visitas ⇒
   as duas tarefas recebem a mesma entrada para contextos diferentes.

`:192-194` intacto — é a string sancionada pelo NORTH_STAR §6 e a probe `R13-aut08` pina-a à letra.
Portão sem movimento: as mesmas 16 probes que já falhavam no HEAD, set-diff vazio nos dois sentidos.

Prosa de moldura (Cap. 1), sem alegação nova e sem número novo — por isso não precisa de errata.


---

## Capítulo 2 — Fundamentals

### B-06
**Página 20 · 2.1.1.1 Check-ins and histories · 26/08 08:19**

**Trecho destacado**

> Let U, P, C, and R denote the sets of users, POIs, category classes, and region classes. Each POI 𝑝 ∈ P carries a category 𝑐 𝑝 ∈ C and lies in a region 𝑟 𝑝 ∈ R.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> **«Let U, P, C, and R denote the sets of users, POIs, category classes, and region classes. Each POI 𝑝 ∈ P carries a category 𝑐 𝑝 ∈ C and lies in a region 𝑟 𝑝 ∈ R.»**
>
> Logo em seguida vem a Definition 2.1 (Check-in): «The 𝑖th check-in of user 𝑢 is the tuple» 𝑥𝑖 = (𝑢, 𝑝𝑖 , 𝑡𝑖 , 𝑐𝑖 , 𝑟𝑖 ), «where 𝑝𝑖 ∈ P is the visited POI, 𝑡𝑖 is its timestamp, 𝑐𝑖 = 𝑐 𝑝𝑖 is its category, and 𝑟𝑖 = 𝑟 𝑝𝑖 is its region.»
>
> Os quatro conjuntos são introduzidos só por definição — nenhum elemento concreto (um usuário, um POI, uma categoria, uma região) aparece como exemplo. É isso que o comentário pede.

**Comentário do revisor**

> talvez., para um publico mais geral, mostrar exemplos de elementos para os conjutnso. para ficar mais paupável

**Parecer** — *✅ FEITO (2026-09-02)*

Alvo: `chapters/2_fundamentals.tex:80-82`. Frase de instância acrescentada **depois** da frase de
ligação.

A medição que justificou o pedido dele, e que eu não esperava que fosse tão extrema: as sete
categorias concretas aparecem **uma única vez** no capítulo, e já em §2.1.1.3, páginas à frente;
"census tract" e *mahalle* só em §2.4.1; $\mathcal{U}$ e $\mathcal{P}$ **nunca recebem instância
nenhuma**; e a expressão "for example" **não ocorre uma única vez em todo o Cap. 2**. Ele tem razão.

⚠ Constrangimento respeitado: a probe `R12-s1bind` pina a frase de ligação à letra, incluindo a
quebra de linha entre "carries a" e "category". O exemplo entrou como **frase nova a seguir** — nada
interpolado, nada reescrito. As probes `R12-s2type` e `R12-ad6fwd` também intactas, e a estrutura do
round 12 (os três `\subsubsection`, o bloco de definições) não foi tocada.

Portão sem movimento.


### B-07
**Página 20 · 2.1 Point-of-interest prediction tasks · 26/08 08:24**

**Trecho destacado**

> 2.1 Point-of-interest prediction tasks

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> O destaque cobre só o título da seção; o comentário é sobre a seção inteira e sobre a ordem do capítulo.
>
> Abertura da seção: «This section establishes what each model predicts before reviewing how those predictions are made. Location-based social networks (LBSNs) record mobility as check-ins, each linking a user, a POI, and a timestamp.»
>
> Estrutura que o revisor tinha à frente — quatro níveis de numeração: «2.1 Point-of-interest prediction tasks» → «2.1.1 Task boundaries and notation» → «2.1.1.1 Check-ins and histories», «2.1.1.2 Check-in and place embedding», «2.1.1.3 The three experimental tasks»; depois «2.1.2 Related sequential prediction settings» e «2.1.3 Category and region as end targets».
>
> E a ordem do capítulo 2 hoje: 2.1 tarefas → 2.2 representações → 2.3 multitask learning → 2.4 datasets e avaliação. MTL, que é o objeto da dissertação, só aparece na terceira seção.

**Comentário do revisor**

> fiquei um pouco perdido nesta seção.
> são muitos subníveis
>
> me parece que, como fundamentação, voce deveria primeiro fundamenta MTL

**Parecer** — *não mexer · responder com um parágrafo, não com uma reorganização*

Alvo: `chapters/2_fundamentals.tex:23`, subníveis em `:65`/`:160`/`:240`, bloco MTL em `:893-1425`.

São dois pedidos num só, e os dois têm problema.

**(a) "Subníveis demais".** Os três `\subsubsection` sob 2.1.1 **são o produto directo do redesenho do
round 12**, aplicado sob ruling tua de 2026-08-03 ("opção (a), manter a ordem das secções, e aplicar o
redesenho das definições" — registada em `2_fundamentals.tex:78-79`). Colapsá-los reabre uma decisão
tua de há um mês. E a probe `R12-s3head` pina **literalmente o comando `\subsubsection`** de `:160`:
promover esse nível põe a suite a vermelho.

**(b) "Fundamentar MTL primeiro".** Nunca foi estudado — o `src_utils/_history/_round12/53_order_comparison.md`
que encomendaste comparou **§2.1 ↔ §2.2** e concluiu "manter". A pergunta dele é uma **terceira**
opção que esse estudo não considerou.

E o custo real não são os `\ref` (**11 vivos no total, e só 1 sai do Cap. 2** — `6_conclusion.tex`,
para `sec:fund:mtl`; nenhum rótulo congelado é afectado. Corrigido 2026-09-02: a primeira versão dizia
15 e 2, contados sem filtrar comentários). **É a prosa.** A abertura da §2.3 (`:896-908`) já usa, sem os definir, "place embedding",
"check-in history", "static category classification" e "next-category prediction" — todos definidos
em §2.1. Mover MTL para a frente **cria exactamente a classe de dependência para a frente que o round
12 gastou uma ronda inteira a eliminar** (o defeito que `:73-76` regista: um símbolo "em USO e
indefinido"). Reordenar sem reescrever a §2.3 troca um problema por um pior.

Recomendação: o incómodo dele é legítimo para quem lê em modo monografia. A cura é **dizer-lhe a
forma** — um parágrafo de abertura no Cap. 2 a justificar que a ordem segue a dependência (tarefas →
representações → partilha, que se define sobre tarefas → protocolo). Seis linhas, contra uma
reorganização de 119 páginas.


### B-08
**Página 31 · 2.4 Datasets and evaluation · 26/08 08:26**

**Trecho destacado**

> 2.4 Datasets and evaluation

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> O destaque cobre só o título da seção.
>
> Abertura da seção: «This section defines the datasets, metrics, reference points, and validation protocol used to interpret the results. It also states which statistical tests support the comparison verbs used in the final study.»
>
> Conteúdo: «2.4.1 Datasets» (Gowalla em cinco estados + Istambul via Massive-STEPS), «2.4.2 Metrics and reference points», «2.4.3 Preparation and data split», «2.4.4 Comparison and statistical decisions». É esse conteúdo — protocolo, split, testes estatísticos — que o revisor lê como materiais e métodos dentro de um capítulo de fundamentação.

**Comentário do revisor**

> como organização, não sei se ficou em uma boa seção.
>
> entendo que voce queira definir e caracterizar o dataset utilizado para o restante do trabalho
>
> lendo toda esta subseção, ficou bem parecida com uma seção de metodos e materiais (metodologia)

**Parecer** — *decisão tua · e a rota barata existe, ao contrário do que eu pensava*

Alvo: `chapters/2_fundamentals.tex:1426-1427` (§2.4), com §2.4.3 em `:1724` e §2.4.4 em `:1769`.

**A observação dele é factualmente correcta.** §2.4.3 descreve o splitter e a definição de *seed*;
§2.4.4 fixa t pareado / Wilcoxon / Holm / TOST. Isso é metodologia dentro de um capítulo de
fundamentação.

A medição que me fez mudar de opinião: a §2.4 é referenciada por **cinco `\ref{sec:fund:eval}` vivos, todos
dentro do próprio Cap. 2 — zero dos Caps. 3, 4, 5 ou 6** — e ela própria não referencia §2.1/2.2/2.3.
(Corrigido 2026-09-02: a primeira versão dizia *oito*. Oito é o grep **sem filtrar comentários**; três
das ocorrências estão dentro de `%`. A conclusão — todas internas ao Cap. 2 — mantém-se.)
Em termos de grafo é um bloco quase solto. **Movê-la para o fim do capítulo, renomeá-la, ou dividi-la
(dados → §2.1, protocolo → secção própria) custa quase nada.**

A rota cara é que é bloqueante: um **capítulo novo de Metodologia** desloca `ch:cbic` de 3 para 4,
`ch:courb` 4→5, `ch:mobiwac` 5→6 — e **parte os nove rótulos congelados** em
`wrapup/material_extra/main_extra.tex:168-176`, invalidando as referências impressas do volume
suplementar, mais cada "Cap. 3/4/5" escrito no corpus de `wrapup/` (27 ocorrências só no
`ESTUDOS_DEFESA.md`, incluindo `ARGUICAO.md` e as erratas Q13/Q14).

Contra-argumento a pesar: a norma de coletânea (UFV §2.3(iii)) não pede capítulo de metodologia, e a
§2.4 **é** o dispositivo da coletânea — existe para dizer o protocolo partilhado uma vez só, o que é,
ironicamente, a resposta ao B-10.

> AUTHOR - uma frase: não mover nada — dizer ao leitor porque é que aquilo está ali. Um parágrafo de abertura no Cap. 2
> explicando que a ordem segue a dependência (tarefas → representações → partilha, que se define sobre tarefas →
> protocolo), e que o protocolo vive na moldura porque é partilhado pelos três artigos e tem de ser dito uma vez só.


---

## Capítulo 3 — Multitask Learning for POI Category and Next-POI Prediction (CBIC 2025)

### B-09
**Página 37 · 3.1 Introduction (CBIC) · 26/08 10:01**

**Trecho destacado**

> the proposed models perform well, particularly in POI category classification, the MTL framework does not deliver the consistent gains often expected.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> To test this hypothesis, we conducted experiments on the Gowalla LBSN dataset [10, 75], comparing our MTL model against strong single-task baselines (HMRM [76] and MHA+PE [77]). Our results lend weight to our hypothesis. While **the proposed models perform well, particularly in POI category classification, the MTL framework does not deliver the consistent gains often expected.** The performance differences between the MTL and single-task models were frequently marginal and fell within standard deviations, suggesting their statistical performance was largely comparable. This outcome indicates that, for this problem, the architectural constraints and task dissimilarities may have offset the potential benefits of joint learning.

**Comentário do revisor** — *nenhum: o revisor grifou o trecho sem escrever nada.*

**Parecer** — *dispensar*

Alvo: `chapters/3_cbic/intro.tex:26`.

Mesmo gesto do B-03: marcar o resultado negativo. Se a objecção fosse que o Cap. 3 declara um nulo
que o Cap. 5 inverte, **a resposta já está no prefácio do capítulo** (`3_cbic.tex:30-39`), que indexa
a conclusão no tempo e nomeia os capítulos que a revêem.

Nota: ele marcou esta frase **depois** de a ronda de erratas já lhe ter tirado o "significantly". Não
é convite para o repor.

Zero probes neste ficheiro.


### B-10
**Página 38 · 3.2 Theoretical Foundations and Related Work · 26/08 10:02**

**Trecho destacado**

> 3.2 Theoretical Foundations and Related Work

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> O destaque cobre só o título da seção.
>
> Ela abre em «3.2.1 POI Classification and Next-POI Prediction»: «POI Category Classification refers to the task of inferring the semantic category of a location based on contextual information such as geographic coordinates, visit frequency, or user behavior. Next-POI Prediction, in contrast, aims to predict which specific location a user is likely to visit next, given their past movement history.»
>
> Subseções: «3.2.1 POI Classification and Next-POI Prediction», «3.2.2 Multitask Learning», «3.2.3 Multitask learning applied in POI». Os mesmos três assuntos já foram cobertos no capítulo 2 (2.1 Point-of-interest prediction tasks, 2.3 Multitask learning, 2.3.6 Multitask learning for mobility prediction) — é a redundância que o comentário aponta, e ela se repete também em 4.2 Related Work e 5.2 Background and Related Work.

**Comentário do revisor**

> uma pequena crítica. o ruim de juntar artigos em um texto único é que aparecem redundancias, como esta seção.

**Parecer** — *decisão tua · uma frase no prefácio, custo de errata zero*

> **FECHADO 2026-09-03, e não onde eu tinha proposto.** O orientador foi consultado sobre este item
> e sobre o B-08 juntos, e decidiu os dois de uma vez: *"o capítulo está bom… como a secção se chama
> 'Fundamentals' e não 'Related Work', acho que não ficou ruim. **Tenta só deixar mais claro na
> primeira parte do capítulo, antes do 2.1 mesmo**, sobre isso, e por mim está ok."* Sobre a ideia de
> uma frase no prefácio de cada artigo: *"acho que não precisa."*
>
> Uma frase de orientação chegou a estar no prefácio do Cap. 3 durante um dia e **foi retirada**. A
> razão não é só a decisão dele: **a mesma sobreposição existe nos Caps. 4 e 5**, que têm as suas
> próprias secções de trabalhos relacionados. Mantê-la só no 3 é assimétrico; repeti-la nos três
> passaria a dizer localmente o que o Cap. 2 agora diz globalmente — triplicando uma frase dentro de
> um documento cuja crítica era a repetição. E o prefácio do Cap. 4 carrega a divulgação da fuga de
> rótulo; conselho de navegação ao lado disso dilui a coisa mais séria que aquele prefácio diz.
>
> **O item continua respondido**, no sítio que o orientador escolheu: a abertura do Cap. 2 diz que os
> datasets, as métricas e o protocolo estão ali *"porque os três estudos os partilham"*, e que *"cada
> capítulo de artigo mantém a descrição que o seu texto original deu"*.

Alvo: `chapters/3_cbic/basis.tex:9`.

A redundância é **estrutural à coletânea** e repete-se em `4_courb/related.tex` e
`5_mobiwac/02_related.tex`. Remover a §3.2 seria mutilar o artigo publicado, o que a política do
projecto proíbe (`CLAUDE.md §3`: "re-typeset reproductions"; NORTH_STAR §4).

A rota é uma frase no **prefácio** do Cap. 3 (`3_cbic.tex:25-45`) a reconhecer a sobreposição e a
dizer que o Cap. 2 é a fundamentação unificada. O prefácio já faz este tipo de trabalho três vezes, e
`3_cbic.tex:68-69` regista-o como "dissertation-authored preface prose, not reproduced published
text, so it carries no Appendix B errata row" — **custo de errata zero**.

Ironia a registar: a §2.4, de que ele se queixa no B-08, existe precisamente para dizer o protocolo
partilhado uma vez só. Ou seja, a estrutura que ele critica num item **é** a resposta ao outro.
Ninguém lho disse na página.

Zero probes neste ficheiro.

> AUTHOR - Primeiro, nõa podemos citar as erratas, pois não fazemo parte do corpo da dissertação; Segundo eu acho que o
> melhor e definir no preambulo a repetição, se possivel já até orientando o leitor o que ele precisa ler, lembrado que
> temos qeu ser breve é um preambulo.


### B-11
**Página 46 · 3.4.1 Dataset and Evaluation Metrics · 26/08 10:15**

**Trecho destacado**

> a 5-fold cross-validation methodology.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> To ensure a robust evaluation of our models, all experiments were conducted using **a 5-fold cross-validation methodology.** The folds are formed by a stratified splitter over the samples rather than over the users, so the check-ins of one user may appear in both training and validation. For the category task the sample unit is the place, so no place spans two folds. The code of record pins a single random seed, so the five folds constitute one repetition of the experiment rather than several, and the means and standard deviations reported below are the spread across those five folds at that seed rather than across independent repetitions. Within a […]

**Comentário do revisor**

> por que?

**Parecer** — *decisão tua · uma frase, e fecha também o B-18*

Alvo: `chapters/3_cbic/results.tex:30`.

Procurei em toda a árvore: **a justificação do *k* não existe em lado nenhum.** A §2.4.3
(`2_fundamentals.tex:1724-1739`) **descreve** o esquema e nunca justifica o número.

O material já cá está: `kohavi1995crossval` está no `references.bib:402` e já é citado em
`2_fundamentals.tex:1731` — é a referência clássica exactamente sobre esta escolha.

**A rota barata é o Cap. 2, não o Cap. 3.** A §2.4.3 é moldura e editável; o Cap. 3 é reproduzido.
Uma única frase lá fecha este item **e o B-18 ao mesmo tempo** (80/20 *é* k=5 — ele fez a mesma
pergunta duas vezes, a dezasseis páginas de distância, sem se aperceber).

A probe `STL-05` cai na janela mas pina a frase seguinte (`:36`), não esta.


### B-12
**Página 46 · 3.4.1 Dataset and Evaluation Metrics · 26/08 10:15**

**Trecho destacado**

> so the check-ins of one user may appear in both training and validation.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> To ensure a robust evaluation of our models, all experiments were conducted using a 5-fold cross-validation methodology. The folds are formed by a stratified splitter over the samples rather than over the users, **so the check-ins of one user may appear in both training and validation.** For the category task the sample unit is the place, so no place spans two folds. The code of record pins a single random seed, so the five folds constitute one repetition of the experiment rather than several, and the means and standard deviations reported below are the spread across those five folds at that seed rather than across independent repetitions. Within a […]

**Comentário do revisor**

> não é ruim isso?

**Parecer** — *o item mais substantivo dos 27 · e a resposta é "sim, é, e nós dizemos isso"*

Alvo: `chapters/3_cbic/results.tex:36`.

Ele encontrou sozinho a fraqueza metodológica que o projecto já conhece. Três factos que mudam como
isto se lê:

1. **A frase não é texto publicado.** O comentário `:37-42` regista-a como *"Declared ADDITION of
   protocol detail, not part of the published text"* (COD-007, round 6), já com linha no Appendix B.
   Foi acrescentada **exactamente para expor** a limitação que ele apanhou.
2. **A moldura já faz a comparação explícita**: `2_fundamentals.tex:1731-1735` — *"Chapters 3 and 4
   stratify samples, so one user's check-ins may occur in both training and validation. Chapter 5
   instead uses a grouped, stratified splitter that keeps each user on one side of a fold."*
3. O `NORTH_STAR §4` regista-a como **item de honestidade deliberado**, verificado no código da época
   (*"say so, it strengthens the arc"*, UW-3 fechado 2026-07-23).

**Mas há um porquê para ele ter tropeçado, e é nosso.** O round 14 removeu deste parágrafo os dois
ponteiros para o Cap. 5, "so the article body carries no dissertation structure" (`:30-35`).
Resultado: o Cap. 3 **confessa a limitação e não a resolve na página**; a resolução está quinze
páginas antes, num capítulo que ele folheou em sete minutos (pp. 20→31, 08:19–08:26). Ele não está a
reagir ao artigo — está a reagir a uma confissão sem saída.

Recomendação: repor o ponteiro no **prefácio** do Cap. 3, não no corpo. Território da moldura, não
desfaz a decisão do round 14, custo de errata zero.

⚠ A probe `STL-05` pina esta frase à letra — qualquer reescrita de "stratified splitter over the
samples rather than over the users" põe a suite a vermelho.


### B-13
**Página 47 · 3.4.2.1 POI Category Classification · 26/08 10:16**

**Trecho destacado**

> both our MTL and Single models outperform HMRM [76] in every POI category in terms of F1-score, precision, and recall.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> As shown in Table 2, **both our MTL and Single models outperform HMRM [76] in every POI category in terms of F1-score, precision, and recall.** For instance, in the ‘Shopping’ category, our MTL model achieves an F1-score of 62.51 ± 0.94 compared to HMRM’s 46.69 ± 0.81. Similarly, for ‘Food’, the MTL model scores 57.43±1.46 against HMRM’s 28.44±0.42. While both MTL and Single models are competitive, the Single model shows marginally better F1-scores in several categories like ‘Community’ (53.11 ± 0.58) and ‘Outdoors’ (47.75 ± 0.89), whereas the MTL model excels in ‘Food’ and ‘Shopping’. Overall, our approaches demonstrate a substantial improvement over the HMRM baseline for this task.

**Comentário do revisor** — *nenhum: o revisor grifou o trecho sem escrever nada.*

**Parecer** — ✅ *APLICADO 2026-09-02 · o único dos 27 que corrigia uma falsidade*

A frase passou a ler: *"…outperform HMRM in every POI category in terms of F1-score and precision,
and in every category except Nightlife in terms of recall."* O alcance foi reconciliado com a tabela;
nenhum resultado mudou, e a correcção enfraquece a favor do baseline — a mesma disciplina das linhas
B2/B3 do ledger. Registado em quatro sítios: linha 11 da Tabela B.1 do suplemento
(`src/tables/cbic/errata.tex`), entrada **B9** do `3_cbic_ADAPTATION_LEDGER.md`, o `ERRATA.md` do
artigo CBIC, e a contagem do apêndice (B.1 de 10 para 11, Total de 55 para 56, medidas pelo
`count_errata_rows.py` antes de serem escritas).

⚠ Foi a **segunda** edição a esta mesma frase publicada: a Tabela B.2 já a carregava, por lhe ter
tirado o *"significantly"* e trocado *"across all"* por *"in every"*. Essa linha **citava o texto do
capítulo**, por isso foi re-citada no mesmo commit — sem isso, o apêndice ficaria a descrever prosa
que já não existe, e nenhum portão apanharia (contam linhas, não conteúdo).

Alvo: `chapters/3_cbic/results.tex:125` contra `src/tables/cbic/category.tex:30`.

A frase afirma que os dois modelos superam o HMRM *"in every POI category in terms of F1-score,
precision, **and recall**"*. Varri as 21 células da tabela que a própria frase invoca:

| | MTL | Single | **HMRM** |
|---|---|---|---|
| F1, nas 7 categorias | — | — | sempre o menor ✓ |
| Precisão, nas 7 | — | — | sempre o menor ✓ |
| **Recall / Nightlife** | 25,80 | 36,77 | **42,13** ❌ |

O HMRM ganha aos dois. **A afirmação universal é falsa em exactamente uma célula das 21, e a tabela
que a desmente está impressa na página seguinte** — a prosa na p. 47, a Tabela 2 na p. 48.

Confirmado por quatro caminhos independentes: o `.tex` da dissertação, o `.tex` do artigo publicado
(`CBIC___MTL/tables/category_result.tex:25`, mesma ordem de colunas), o `banca.pdf` renderizado
(p. 48), e um parser mecânico sobre as 21 células (20 confirmam a frase, 1 não). A dissertação
reproduz a tabela publicada com fidelidade — o defeito vem do artigo.

> **CORRECÇÃO A ESTE PARECER (2026-09-02).** A primeira versão dizia que o número "não está registado
> em lado nenhum". **Era falso, e o erro foi meu**: procurei numa lista de ficheiros que não incluía
> os ledgers de adaptação, e reportei a ausência como facto.
>
> A célula **está** registada. `src_utils/adaptation_ledgers/3_cbic_ADAPTATION_LEDGER.md`, entrada
> **B7**, da ronda 4: *"The published category table bolds the better of MTL/Single per row and never
> bolds HMRM, even where HMRM is numerically highest (Recall/Nightlife: HMRM 42.13 > Single 36.77
> bold). Emphasis preserved exactly as published; the new caption states the convention explicitly so
> the bolding is not misread as 'best per row'."*
>
> O achado real é mais preciso do que eu tinha escrito, e melhor: **a ronda 4 viu esta célula,
> tratou-a como um problema de negrito, resolveu-o com a legenda — e não ligou a mesma célula à frase
> da p. 47 que promete superioridade universal.** O número era conhecido; a consequência para a prosa
> não.

E o detalhe que torna isto acionável: **a ronda de erratas já mexeu nesta frase.** O artigo publicado
dizia *"significantly outperform … across all POI categories"*
(`CBIC___MTL/sections/results.tex:29`); o capítulo tirou o "significantly" e **manteve o
quantificador universal**. Corrigiu-se metade.

Precedente exacto: os erratas **B2 e B3** do `src_utils/adaptation_ledgers/3_cbic_ADAPTATION_LEDGER.md`
— prosa publicada contradita pela tabela publicada, reconciliada *para a tabela*, com linha de ledger.
A frase de `:169` do mesmo ficheiro já é produto dessa operação. Este é o terceiro caso.

Rota: estreitar a frase (algo como *"…in every POI category in F1-score and precision, and in recall
in every category except Nightlife"*) + linha de ledger + linha de errata. Enfraquece a favor do
baseline, que é o padrão das outras linhas.

Nenhuma probe na janela. Na minha leitura isto não é uma escolha de gosto — é a tua própria lei sobre
uma frase falsa no texto que vai ser depositado.


### B-14
**Página 49 · 3.4.3 Convergence Comparison · 26/08 10:19**

**Trecho destacado**

> The target F1-score for the Category prediction task was set to 47, and for the Next POI category classification task, it was set to 32.2.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> To further evaluate the practical implications of the MTL approach compared to single-task models, we conducted a convergence experiment. We measured the wall time, number of epochs, and Mega Floating Point Operations (MFLOPs) required for the MTL model and the individual single-task models (SingleClass and SinglePred) to reach predefined target average F1-scores. **The target F1-score for the Category prediction task was set to 47, and for the Next POI category classification task, it was set to 32.2.** These specific F1 values were chosen […]

**Comentário do revisor** — *nenhum: o revisor grifou o trecho sem escrever nada.*

**Parecer** — *tratar em conjunto com o B-15; ver o parecer de lá*

> **Nota, 2026-09-02.** O autor perguntou o que havia aqui para decidir. **Nada** — e a culpa é minha
> por o ter listado como decisão. O B-14 é só onde o revisor pousou os olhos primeiro; o item é o
> B-15. Fica como remissão.

Alvo: `chapters/3_cbic/results.tex:163`.

Não é um item independente. Ele marcou os números às **10:19** e escreveu o comentário às **10:20**,
no destaque seguinte, começando por *"entendi o porquê"*. **B-14 é a pergunta e B-15 é a mesma
pergunta já meio respondida pela leitura.**

Proveniência, para o caso de alguém querer mexer nos números: o
`3_cbic_ADAPTATION_LEDGER.md:134` regista que "targets 47 and 32.2" são **verbatim** do artigo
publicado.

> AUTHOR - Não entendi o que temos que decidir aqui ?

### B-15
**Página 50 · 3.4.3 Convergence Comparison · 26/08 10:20**

**Trecho destacado**

> best-achieved results for each respective task, thereby representing a comparable and significant level of predictive performance for the models to attain.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> because they are close to the **best-achieved results for each respective task, thereby representing a comparable and significant level of predictive performance for the models to attain.** To ensure robust measurements for this experiment, all models were evaluated through a 5-fold cross-validation process. The specific metrics are detailed in Table 4.

**Comentário do revisor**

> entendi o porquê.
> No caso, só testa para um deles (single class ou singlepred)?

**Parecer** — *decisão tua · a ambiguidade é real, e está na tabela, não na frase*

Alvo: `chapters/3_cbic/results.tex:163` + `src/tables/cbic/convergence.tex:11-13`.

A pergunta dele (*"só testa para um deles?"*) é legítima e a causa é a tabela: ela tem três linhas —
`Category` 16,26 s, `Next` 18,71 s, `MTL` 80,88 s — e **a linha MTL é uma só**, sem dizer contra qual
dos dois alvos foi medida.

**A resposta já está escrita, duas linhas abaixo**, em `results.tex:169`: *"the MTL approach required
80.88 s of wall time, about 2.3 times the cumulative 34.97 s of the individual single-task models."*
Ora 34,97 = 16,26 + 18,71. Logo a comparação é *modelo conjunto contra ambos os alvos* vs. *dois
modelos dedicados, cada um contra o seu*. Falta dizê-lo onde o leitor o procura: na legenda da tabela.

Precedente aberto: `:169` **já foi reescrita** pelos erratas B2/B3 do ledger, exactamente pela mesma
razão (prosa contra tabela). A rota está estabelecida.

O que fica genuinamente em aberto e não consegui confirmar no código: se o MTL tem de atingir os dois
alvos **na mesma época** ou cada um por si. O texto não o diz. Se souberes de cabeça, fecha-se; se
não, fica `?`.

> AUTHOR - Na mesma epoca, eu usei o resultado de um checkpoint final para fazer a inferencia dos resutlados das duas
> tarefas

---

## Capítulo 4 — ST-MTLNet: Spatio-Temporal POI Representations (CoUrb 2026)

### B-16
**Página 53 · 4.1 Introduction (CoUrb) · 26/08 10:22**

**Trecho destacado**

> temporal representation (Time2Vec) for visitation patterns,

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> In this sense, this chapter proposes ST-MTLNet (Spatial-Temporal MTLNet), which integrates three independent representations: a continuous spatial representation for geographic coordinates, a **temporal representation (Time2Vec) for visitation patterns,** and a hierarchical categorical representation for regional and structural relationships between POIs. In the spatial dimension, we evaluate two architectures with distinct assumptions, SIREN and Sphere2Vec-M, originally validated in geospatial tasks of remote sensing and ecology [86], but still little explored in multitask learning of POIs in LBSNs.

**Comentário do revisor**

> como discussão, você viu se tem outras alternativas?

**Parecer** — *decisão tua · exige literatura, e colide com um item aberto*

Alvo: `chapters/4_courb/intro.tex:25`.

A assimetria que ele apanhou é real, e medi-a: o **eixo espacial** tem quatro alternativas citadas em
`2_fundamentals.tex:610-631` — SIREN, Space2Vec, Sphere2Vec, harmónicos esféricos. O **eixo temporal**
tem **só Time2Vec, em todo o documento**. Procurei `Date2Vec`, `Fourier feature`, `temporal encoding`:
zero ocorrências fora do próprio Time2Vec.

Custo: um parágrafo **em `2_fundamentals.tex:624-625`, que é moldura** — não no Cap. 4. Exige busca de
literatura ancorada, que é a mesma tarefa que o `NORTH_STAR §4b` ponto 1c deixou explicitamente por
fazer ("NOT ABSORBED. This is a live open item").

⚠ **Colide com LO-12, ABERTO** (`wrapup/open_points/LACUNAS.md:255-267`): a descrição do insumo
temporal do Cap. 4 tem uma contradição não resolvida — `:93` da metodologia implica um vector temporal
**por POI**, `:153` diz **por check-in**, e o artefacto que decidiria (`time_embedding.parquet` da
época) já não existe. **Escrever no Cap. 2 evita a colisão; escrever no Cap. 4 entra nela.**

> AUTHOR - Aqui vamos ter que deixar em aberto, vai ser um gargalo, mas de fato como não documentamos isso antes eu não
> lembro, e mesmo se fizermos uma busca agora na literatura, vai ser tentar arrumar uma justificativa para uma pergunta
> que não é critica, apesar de ser uma critica honesta, isso não impcat os resultados finais.

### B-17
**Página 57 · 4.3 Methodology (Figura 2) · 26/08 10:23**

**Trecho destacado**

> Figure 2 – Architecture based on MTLnet [1]. The spatial, temporal, and categorical encoders are trained in a decoupled manner and generate their respective embeddings, which are integrated as input to the model. The integrated input is processed by the model’s shared layers (Shared Layers Module) and by the task-specific layers, producing the Category Output and Next POI Output.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> **Figure 2 – Architecture based on MTLnet [1]. The spatial, temporal, and categorical encoders are trained in a decoupled manner and generate their respective embeddings, which are integrated as input to the model. The integrated input is processed by the model’s shared layers (Shared Layers Module) and by the task-specific layers, producing the Category Output and Next POI Output.**

**Comentário do revisor**

> ficou muito parecido ou igual a arquitetura anterior.
>
> dá para apontar as diferenças? na apresentação mesmo

**Parecer** — *dispensar · ele próprio disse onde queria a resposta, e ela já aconteceu*

Alvo: `chapters/4_courb/methodology.tex:20-21`.

Ele escreveu *"**na apresentação mesmo**"*. É um pedido de exposição oral, não uma alteração de texto
— e a defesa foi a 28/08 e foi aprovada. Cumprido ou dispensado.

Se ainda assim se quisesse tocar no documento: as duas figuras são de facto próximas
(`cbic_mtlnet_arch.png` 1200×336 px; `courb/arquitetura_modelo.png` 1102×348 px), mas **a legenda já
nomeia a diferença** — "based on MTLnet", com os três codificadores desacoplados como a mudança. E o
`wrapup/REVISION_PLAN.md:651` classifica ambas como *"published-chapter figures | do not touch"*.

Ver também o B-04: é o mesmo pensamento dele, cinquenta páginas antes.


### B-18
**Página 62 · 4.4.1 Experimental Setup · 26/08 10:26**

**Trecho destacado**

> using 80% of the data for training and 20%

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> The performance of the models is evaluated using the Average F1-Score per category, reported as mean and standard deviation over 5 folds with a stratified split, **using 80% of the data for training and 20%** for validation, preserving the proportion between categories.

**Comentário do revisor**

> por que?

**Parecer** — *o mesmo item que o B-11 · fecham com a mesma frase*

Alvo: `chapters/4_courb/results.tex:14`.

**80/20 *é* k=5** — o número de dobras determina a proporção. Ele fez a mesma pergunta duas vezes, a
dezasseis páginas de distância (B-11 na p. 46, este na p. 62), sem se aperceber de que era a mesma. A
frase aqui enuncia a *consequência* sem enunciar a *causa*, e a justificação do *k* não existe em
nenhum ponto do documento (ver o parecer do B-11).

Uma única frase na §2.4.3 do Cap. 2 — que é moldura, não capítulo reproduzido — fecha os dois itens.
O `kohavi1995crossval` já está no `.bib` e já é citado lá.

Que ele tenha perguntado duas vezes é o sinal: não é curiosidade, é uma lacuna que o incomodou o
suficiente para voltar a ela.

Nenhuma probe na janela.


### B-19
**Página 63 · 4.4.2 POI Category Classification (Figura 3) · 26/08 10:27**

**Trecho destacado**

> Figure 3 – [legenda completa no contexto abaixo]

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> **Figure 3 –** Spatial distribution of POIs of the Food (red) and Shopping (orange) categories in the densest sub-region of Florida, California, and Texas. The sub-regions were selected by density in a grid, with about 100 POIs per region. Each panel plots the POI coordinates (longitude on the horizontal axis, latitude on the vertical axis) for one state; the dense, overlapping clusters of the two categories illustrate the co-location pattern discussed in the text.

**Comentário do revisor**

> como voce tem espaço, coloca uma figura embaixo da outra para aumentar o tamanho delas

**Parecer** — *dispensar na política actual · mas a rota barata existe se mudares de ideias*

Alvo: `chapters/4_courb/results.tex:20-25`.

Medi o ficheiro: `src/figures/courb/distribuicao_estados.png` é **um único PNG de 5389×1643 px** com
os três painéis (Florida, Califórnia, Texas) lado a lado. **Não são três ficheiros** — não há
`\subfigure` a reorganizar.

Duas rotas:
- **Regenerar dos dados** — não há script fonte na árvore; o `archive/prompts/v1_assembly_prompt.md:97`
  já tinha registado que seria preciso reconstruir a partir dos dados *se* existisse script. É
  geração nova.
- **Recorte mecânico** — os três painéis são recortáveis do PNG existente
  (`\includegraphics[trim=…,clip]` ×3) e empilháveis. Cada painel ficaria ~1796×1643 px; a
  0,7\textwidth empilhados ganham **cerca de 2× em largura efectiva**. Nenhum pixel é recalculado.

Contra: o `REVISION_PLAN.md:651` diz "do not touch", e empilhar **reflui as páginas 63+**, o que parte
as referências de página das próprias erratas. Só vale se fores reconstruir de qualquer modo.

`fig:courb:distribuicao` está congelada no número **3** (`main_extra.tex:172`); empilhar não muda o
número, portanto o rótulo congelado sobrevive.


### B-20
**Página 65 · 4.5 Conclusion and Future Work · 26/08 10:31**

**Trecho destacado**

> By incorporating a continuous spatial encoder, a temporal encoder (Time2Vec), and a hierarchical categorical encoder (HGI), ST-MTLNet consistently outperforms the baseline based only on DGI.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> This chapter investigated whether replacing the monolithic embedding of DGI with decoupled and specialized representations could produce a base more suitable for the tasks of POI Category Classification and Next-POI Prediction. The results obtained in the three evaluated states indicate that it can. **By incorporating a continuous spatial encoder, a temporal encoder (Time2Vec), and a hierarchical categorical encoder (HGI), ST-MTLNet consistently outperforms the baseline based only on DGI.**

**Comentário do revisor**

> conclusão

**Parecer** — *decisão tua · uma palavra, e há uma tensão real por baixo*

Alvo: `chapters/4_courb/conclusion.tex:12`.

O "comentário" é a etiqueta "conclusão" — provavelmente marcou a frase-conclusão do capítulo para a
ter à mão na arguição, não uma objecção.

**Mas há uma tensão que um leitor atento apanha.** *"consistently outperforms"* é qualificado seis
linhas abaixo, em `:14`, por *"outperforms the baseline in 15 of the 21 evaluated combinations, with
one additional technical tie"*, e em `4_courb/results.tex:52` por *"the baseline retains six of
them"*. **"Consistently" contra 15/21 é uma tensão de grau.**

E o detalhe que a torna nossa: `:14` **já carrega os números auditados** (15/21 + 1 empate),
corrigidos contra o "16/21 (76%)" do texto publicado — correcção registada no `NORTH_STAR §4 Ch.4`.
Ou seja, **a moldura já baixou o número e deixou o advérbio.**

Custo: zero, ou uma palavra (`consistently` → `generally` / `in most`). É prosa publicada e toca um
verbo de comparação, por isso é tua.

Zero probes neste ficheiro.

> AUTHOR - Concordo podemos trocar

### B-21
**Página 66 · 4.5 Conclusion and Future Work · 26/08 10:32**

**Trecho destacado**

> long-distance movements and topological relationships between regions are still better captured by the graph structure used by DGI.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> A relevant limitation remains in the Travel category of the Next-POI Prediction task, in which the original MTLnet still obtains the best results in part of the scenarios. This suggests that **long-distance movements and topological relationships between regions are still better captured by the graph structure used by DGI.** In addition, since the three proposed components are used together, this chapter does not isolate the individual contribution of each encoder, which restricts a more detailed analysis of the relative weight of each source of information.

**Comentário do revisor** — *nenhum: o revisor grifou o trecho sem escrever nada.*

**Parecer** — *dispensar, ou uma palavra de hedge*

Alvo: `chapters/4_courb/conclusion.tex:18`.

A leitura que melhor explica o destaque: é uma **explicação mecanicista sem evidência**. A limitação
observada é empírica (o baseline ganha em parte dos cenários) e a frase salta daí para uma causa — a
estrutura de grafo do DGI capta movimento longo — que nenhuma medição do capítulo suporta.

O que a torna frágil é o próprio parágrafo: a frase **seguinte** confessa que os três componentes só
foram usados em conjunto e que o capítulo *"does not isolate the individual contribution of each
encoder"*. Isso remove a base para atribuir a causa a um componente.

O hedge "This suggests" já lá está. Se a objecção for essa, ela é que mesmo o hedge é generoso — mas é
prosa publicada, e uma palavra a mais de cautela é o máximo que eu faria.


### B-22
**Página 66 · 4.5 Conclusion and Future Work · 26/08 10:32**

**Trecho destacado**

> Consequently, the results should be interpreted with caution regarding their generalization to current urban mobility patterns.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> Another limitation is related to the exclusive use of Gowalla, a dataset commonly used in the literature but composed of mobility records collected between February 2009 and October 2010. **Consequently, the results should be interpreted with caution regarding their generalization to current urban mobility patterns.**

**Comentário do revisor**

> o que é dependented entre modelo e dataset?

**Parecer** — *decisão tua · barato, e a resposta é empírica*

Alvo: `chapters/4_courb/conclusion.tex:20`.

A frase diz "interprete com cautela" **sem dizer o quê** é que envelhece com o dataset. A pergunta
dele é legítima.

A resposta existe no documento, noutro capítulo, e é **empírica**: o Cap. 5 acrescenta **Istambul**
precisamente como teste de generalização fora dos EUA (`1_introduction.tex:238` regista a decisão de âmbito — *"Istanbul as a
non-United-States dataset"*; a primeira versão citava `:188-191`, que é outra passagem; `5_mobiwac/01_introduction.tex:27` diz *"two settings chosen to differ"*).

Rota barata: **prefácio do Cap. 4** (prosa de dissertação, custo de errata zero, mesmo mecanismo do
prefácio do Cap. 3) ou o Cap. 6 — não a conclusão publicada.

> AUTHOR - Eu acredito que podemos mudar o texto do capitulo para ficar melhor e criar uma errata. Mas não precisa referenciar a errata. 

---

## Capítulo 5 — A Check-in-Level Multitask Study of Next Category and Region (MobiWac 2026)

### B-23
**Página 68 · 5.1 Introduction (MobiWac) · 26/08 10:39**

**Trecho destacado**

> We propose two enhancements.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> **We propose two enhancements.** First, we build a check-in-level representation: instead of one fixed vector per place, each check-in gets its own vector that holds its context (the time, nearby places, and recent visits). This adds a fourth level, the check-in, beneath the place, region, and city levels of hierarchical graph infomax [32, 31] (Figure 4). Second, we train one model that predicts the next category and the next region in a single forward pass, with a shared trunk (a cross-attention stack where the two tasks exchange semantic context) and a private spatial path for the region task (Figure 5). We evaluate on two settings chosen to differ: five U.S. states of different sizes (Gowalla) and one non-U.S. city (Istanbul).1 […]

**Comentário do revisor**

> com relação ao primeiro né?

**Parecer** — *decisão tua · três palavras*

Alvo: `chapters/5_mobiwac/01_introduction.tex:24`.

Ele tem razão e o antecedente existe, mas é fraco: a frase imediatamente anterior (`:16-17`) diz
*"Our earlier work reported no consistent multitask advantage for the paired category tasks and
attributed it, in part, to this effect~\cite{silva2025mtlnet}"*. Logo "enhancements" é relativo ao
MTLnet — mas **o substantivo não o diz**, e num artigo lido isolado a distância é de uma frase.

Custo: três palavras (*"two enhancements over that design"*). É prosa reproduzida de artigo **aceite**,
portanto a rota é errata.

Nota: o **prefácio do Cap. 5** (`5_mobiwac.tex:33-45`, reescrito a 01/09) já faz este trabalho para o
leitor da dissertação — *"It closes the investigation that Chapters 3 and 4 open"*. Quem lê a
dissertação tem a resposta a duas páginas; quem lê o artigo isolado não tem.

Zero probes neste ficheiro.

> AUTHOR - Concordo podemos fazer


### B-24
**Página 72 · 5.4.1 The check-in-level representation · 26/08 10:46**

**Trecho destacado**

> the check-in, its place, the place’s region (a census tract), and the city.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> We build a graph with four levels: **the check-in, its place, the place’s region (a census tract), and the city.** Edges connect each level to the one above it and link a user’s consecutive check-ins with a weight that decays as the time gap between the visits grows; same-place visits connect through their shared place node one level up, and nearby places are linked at the place level. Each visit’s category, time of day, and day of week enter as input features of its node, not as edges. Four elapsed-time features join them: the time since the user’s previous visit and since the user’s first visit, both on a logarithmic scale, the gap to the previous visit within the same day, and an indicator for a user’s first visit. […]

**Comentário do revisor**

> regiao e lugar da regiao nao são dependentes?

**Parecer** — *oral · a resposta existe, e a dependência é declarada, não escondida*

Alvo: `chapters/5_mobiwac/04_method.tex:18`.

Pergunta boa, com duas leituras, e as duas têm resposta no texto:

**(a) Sobre o grafo** — se a região é determinada pelo lugar, o nível "região" acrescenta informação?
Acrescenta **agregação e vizinhança** (o infomax hierárquico contrasta cada vector contra a vizinhança
do seu nível), não identidade.

**(b) Sobre as tarefas** — se `r_p` é função de `p`, prever a próxima região não é uma projecção de
prever o próximo lugar? `5_mobiwac/03_problem.tex:13` responde: *"We do not predict the exact next
place; both properties are easier to learn and, for most uses, enough."* E a formalização em
`2_fundamentals.tex:80-82` diz explicitamente que cada POI *"lies in a region"* — **a dependência é
assumida e declarada**.

Custo zero se for resposta oral, e a defesa já passou.

Zero probes neste ficheiro.


### B-25
**Página 72 · 5.4.1 The check-in-level representation · 26/08 10:46**

**Trecho destacado**

> tempo,

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> […] Four elapsed-time features join them: the time since the user’s previous visit and since the user’s first visit, both on a logarithmic scale, the gap to the previous visit within the same day, and an indicator for a user’s first visit. Each is measured up to the visit itself, so a node describes the visit and the history preceding it, never anything that follows. These give the representation a sense of **tempo,** distinguishing a visit that follows minutes after the last one from a visit that opens a new outing, which a categorical hour-and-weekday encoding alone cannot express. The consecutive-visit edges run in one direction only, from an earlier visit to a later one, for the same reason: a target is predicted from a user’s past, so the representation is built from the past alone. This keeps a hierarchical graph’s place-to-region-to-city geography and adds the check-in as a bottom level. […]

**Comentário do revisor** — *nenhum: o revisor grifou o trecho sem escrever nada.*

**Parecer** — *dispensar · com uma hipótese sobre por que ele marcou uma palavra só*

Alvo: `chapters/5_mobiwac/04_method.tex:18`, a palavra "tempo".

É o único destaque de uma palavra isolada em 27, e a única leitura que explica o gesto: **"tempo" é um
falso amigo.** Em inglês significa *ritmo / cadência*; um leitor lusófono lê *time*, e nesse sentido a
frase fica circular — "dão à representação um sentido de tempo", logo depois de listar quatro
características de tempo.

É prosa aceite no MobiWac e a palavra está correcta em inglês. O projecto já corrigiu um falso amigo
desta família noutro sítio (`_history/_review_v1/CONSOLIDATED_REVIEW_REPORT.md:2188`, "expressivo"), portanto a
classe é reconhecida.

Não mexeria. Se mexeres, é uma palavra (`tempo` → `pacing` / `rhythm`), e é errata por ser artigo
aceite.


### B-26
**Página 74 · 5.5.2 Windows, splitting, and the integrity of the representation · 26/08 10:49**

**Trecho destacado**

> Windows.

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> **Windows.** For each user with at least ten visits, we order the visits by time. We then form overlapping sliding windows of nine visits and use the next visit as the target. A new window starts at each visit, which provides more examples for both tasks. Near the end of a user’s history, several start positions can produce shorter, padded windows with the same final visit as the target. We remove these duplicates and keep only the full-length window that ends at this target. The prediction horizon is usually short, but some time gaps are much longer. The median time from the last visit in a window to its target ranges from 0.4 hours in Florida to 5.5 […]

**Comentário do revisor**

> ??
>
> ficou estranho. só fez um pouco de sentido quando vi na proxima pagina que é um itemizador

**Parecer** — 🔴 *NÃO FIZ · ia fazer, e mudei de opinião a meio. Recomendo dispensar.*

Alvo: `chapters/5_mobiwac/05_setup.tex:28` e mais seis rótulos vivos no mesmo ficheiro.

Estava a caminho de converter os sete `\emph{X.}` em `\paragraph*{}`, alinhando com as **doze** ocorrências vivas
do Cap. 3 (3 em `basis.tex`, 8 em `method.tex`, 1 em `results.tex`; a primeira versão dizia dez), e classifiquei-o como o item mais barato dos 27. **Duas medições travaram-me:**

1. **`\paragraph*` nesta classe renderiza como título isolado numa linha própria** — verificado no
   `dissertacao.pdf`, onde "Architecture Overview" (Cap. 3) aparece sozinho na sua linha. E a secção
   imediatamente acima já se chama *"5.5.2 Windows, splitting, and the integrity of the
   representation"*. Converter criaria um título **"Windows."** debaixo de um título que já diz
   Windows. Piorava.
2. **Mais decisivo: o artigo original usa exactamente `\emph{Windows.}`** —
   `articles/[mobiwac]/src_fix/sections/05_setup.tex:26`, à letra. **Não é artefacto da
   re-tipografia.** É a convenção do próprio artigo, reproduzida com fidelidade. Converter seria
   **desviar-me** do publicado, não restaurá-lo.

A auditoria interna classificou este item como fechável por agente **na premissa de ser reformatação**
coberta pela cláusula "reformatted from the two-column original". A premissa é falsa, e por isso não
mexi.

Recomendação: **dispensar.** Rótulos corridos em itálico são convenção corrente em ACM/IEEE; este
leitor achou-a estranha, mas a fidelidade ao artigo aceite é o contrato da coletânea.

Se quiseres mesmo agir, a única rota sem custo de fidelidade é uma **frase de introdução antes de
`:28`** a anunciar a lista — e isso é prosa em capítulo aceite, portanto decisão tua e errata.

⚠ Se alguma vez mexeres neste ficheiro: ele tem 6 probes (nenhuma na janela, nenhuma a tocar em
`\emph`) e já foi alterado a 01/09 com as ERR-6/ERR-7 aplicadas.


### B-27
**Página 81 · 5.6.2 One model, two tasks (Tabela 10) · 26/08 10:58**

**Trecho destacado**

> Table 10 – One model, [legenda completa no contexto abaixo]

**Contexto** — o texto em volta; quando o destaque é parte de um parágrafo, ele vai em **negrito**

> **Table 10 – One model,** two tasks: the single joint model against the dedicated single-task models and the external baselines, ordered by check-in count (Table 8); the region counts in the second column do not follow that order. The upper block reports next-category (macro-F1) and the lower block next-region (Acc@10); the two share the dataset and region-count columns, and the same six datasets appear in the same order in both. Bold with ↑ marks an improvement over the dedicated model that survives Holm correction within its task family. In the region block, ≈ marks a difference that stays within the two-point margin registered before any result was read (statistical non-inferiority, TOST; Section 5.6.2). Category cells carry no equivalence mark because the margin was registered for the region axis only, so a category difference that fails superiority is reported by the bound its interval supports, half a point.

**Comentário do revisor**

> não entendi porque voce marcou 2 melhores embaixo e só o melhor na tabela de cima


**Parecer** — *✅ FEITO (2026-09-02) · e depois SUPERADO no mesmo dia, para melhor*

Alvo: `src/tables/mobiwac/results.tex`. Acrescentado à legenda da Tabela 10:
*"…; it does not mark the largest value in a column."*

**A leitura errada dele não é distração — é uma colisão de convenções dentro do teu próprio
documento.** A Tabela 2 (`tables/cbic/category.tex:4`) diz *"the better of the MTL and Single values
per row in bold, as in the published table"*: ali, negrito **é** o melhor valor. A Tabela 10 usa
negrito para "melhoria sobre o modelo dedicado que sobrevive a Holm". Ele aplicou a convenção da
primeira à segunda. Duas tabelas, dois sentidos, o mesmo documento.

Isto importa mais do que parece: **a Tabela 10 é a que vai ser citada.** Quem a lê com a convenção
errada vê uma célula a negrito no bloco de cima e duas no de baixo, conclui que o Alabama "não tem
melhor", e desvaloriza o resultado. A legenda já excluía essa leitura **por implicação**; agora
exclui-a por escrito.

Verificações feitas antes de editar:
- A legenda é **prosa da dissertação, não do artigo** — a do artigo
  (`[mobiwac]/src_fix/tables/tbl3_results.tex:22-29`) ordena por contagem de região e não tem nem a
  frase dos dois blocos nem o limite de meio ponto. Não é texto publicado a ser alterado.
- É uma **negativa**, não uma alegação nova: nenhum número, marca ou veredicto muda.
- Zero probes neste ficheiro; portão sem movimento depois da edição.
- `tab:mobiwac:results` está congelada no número **10** (`main_extra.tex:176`) — editar a legenda não
  mexe no número.

Proveniência registada em comentário datado acima da legenda.

> **ACTUALIZAÇÃO, ainda a 2026-09-02.** A cláusula que eu acrescentei foi **retirada horas depois**,
> porque o autor lembrou-se de uma correcção que fez para a apresentação da defesa e que nunca desceu
> ao texto. Ela resolve o B-27 melhor do que a minha legenda: **separa os dois canais.**
>
> Negrito e sublinhado passam a dizer só **magnitude** — o maior da linha e o segundo, ambos a negrito
> quando empatam à precisão impressa. O **veredicto estatístico** muda-se para marcas próprias, `↑` e
> `≈`, ao lado do valor do modelo conjunto.
>
> Era a sobreposição dos dois num só canal que perdia o revisor: no Alabama o modelo dedicado tem o
> número maior e nada estava a negrito, logo lia-se *"aqui não há melhor"*. A minha cláusula
> (*"não marca o maior valor da coluna"*) ficou **falsa** com a mudança e saiu.
>
> Aplicado a seis tabelas, com prova de que nenhum dígito se moveu, e registado como afastamento da
> ênfase publicada nas erratas B.1, B.3 e B.5. Commit `067341ff`.

---

## Como estes itens foram extraídos

```bash
python3 - <<'EOF'
import fitz
doc = fitz.open("~/Downloads/dissertacao - vitor hugo (1).pdf")
for pno, page in enumerate(doc, start=1):
    words, blocks = page.get_text("words"), page.get_text("blocks")
    for a in page.annots() or []:
        if a.type[1] != "Highlight":
            continue
        pts = a.vertices or []
        rects = [fitz.Quad(pts[i:i+4]).rect for i in range(0, len(pts), 4)]
        sel, seen = [], set()
        for w in words:                      # dedup: os quads se sobrepoem e repetem palavras
            wr = fitz.Rect(w[:4])
            if any((wr & r).get_area() > 0.5 * wr.get_area() for r in rects):
                key = (round(w[0], 1), round(w[1], 1), w[4])
                if key not in seen:
                    seen.add(key); sel.append(w)
        sel.sort(key=lambda w: (w[5], w[6], w[7]))
        quote = " ".join(w[4] for w in sel)                      # o trecho destacado
        ctx = " ".join(" ".join(b[4].split())                    # o paragrafo em volta
                       for b in blocks if (fitz.Rect(b[:4]) & a.rect).get_area() > 0)
        print(pno, "|", quote, "|", ctx, "|", a.info.get("content", ""))
EOF
```

A hifenização de fim de linha do PDF foi desfeita (`usu- ário` → `usuário`), preservando os hífens
reais (`single-task`, `check-in`, `cross-validation`): um `X- Y` só é juntado sem hífen quando
`X-Y` não ocorre em nenhum outro ponto do documento.

Quando o destaque cobre apenas um título de seção (B-06, B-07, B-08, B-10), uma legenda (B-19,
B-27) ou uma palavra isolada (B-25, B-26), o bloco de contexto foi completado com a abertura da
seção e a lista de subseções, porque é a isso que o comentário se refere. Nesses quatro casos o
contexto mistura texto da dissertação com uma nota de enquadramento escrita aqui — **o que está
entre «aspas angulares» é literal do PDF; o resto é a nota.** O verificador confere cada trecho
entre «» contra a página.

## Verificação

O arquivo é conferido por [`verify_revisao_banca.py`](verify_revisao_banca.py) (nesta mesma pasta), que lê o PDF por um caminho
independente do que gerou o texto — **pdftotext (poppler)** para o texto das páginas e **pypdf** para
as anotações, e não o PyMuPDF usado na extração. Ele checa, item a item:

1. o PDF tem 27 destaques, o documento tem 27 itens e o índice tem 27 linhas, com IDs `B-01`…`B-27` contíguos;
2. a página de cada item é a página onde a anotação está;
3. o comentário transcrito é idêntico ao `/Contents` da anotação;
4. a linha do índice (ID, página, seção) bate com o item, e o status começa em `☐`;
5. o trecho destacado ocorre literalmente na página que o item declara;
6. o contexto ocorre literalmente na mesma página (segmento a segmento, entre os cortes `[…]`); nos
   quatro itens com nota de enquadramento, cada trecho entre «» é conferido;
7. o trecho destacado está dentro do seu próprio contexto e aparece em negrito;
8. o rótulo de seção existe no sumário do PDF, com o título completo.

Resultado da última execução (2026-09-02): **27/27 itens, zero falhas.**

```
$ python3 articles/dissertacao/wrapup/verify_revisao_banca.py
itens: 27 | destaques no PDF: 27 | linhas de índice: 27
FALHAS: 0
```

O script assume o PDF em `~/Downloads/dissertacao - vitor hugo (1).pdf`; se ele mudar de lugar,
ajuste a constante `PDF` no topo.
