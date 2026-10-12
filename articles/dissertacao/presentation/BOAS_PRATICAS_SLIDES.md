# BOAS_PRATICAS_SLIDES.md — a referência de forma do deck de defesa

> **Escrito 2026-08-26 pela sessão `ppt`.** Defesa **sexta, 28/08/2026, 10:00, remota (Google Meet)**.
> Banca: Fabrício A. Silva (orientador/presidente), Clayson S. F. de Sousa Celes (ITA, externo),
> Alex Borges.
>
> **O que este documento é.** A referência de **forma**: hierarquia da informação, composição,
> densidade, legibilidade, uso do template, consistência. Ele consolida três coisas que antes
> estavam separadas ou não existiam: (1) o que a literatura de fato estabelece sobre slide de
> apresentação técnica, com a força da evidência declarada caso a caso; (2) a defesa do a defesa de referência
> **medida quadro a quadro** a partir da gravação, não lembrada; (3) o `nesped.sty` **medido** —
> escala de tipo, contraste, componentes e armadilhas, verificados compilando.
>
> **O que ele NÃO é.** Não é lei de conteúdo. O que entra em cada slide é decisão do autor,
> informada pelo agent `gate`. Não é lei de palavra: [`../WRITING_LAW.md`](../WRITING_LAW.md),
> [`../GLOSSARY.md`](../GLOSSARY.md) e [`../AGENT_GUARDRAILS.md`](../AGENT_GUARDRAILS.md) continuam
> valendo inteiros. Não é lei de estrutura: essa é o
> [`PLANO_FLUXO_DEFESA.md`](_preparacao/PLANO_FLUXO_DEFESA.md) §8. **Onde este documento divergir de qualquer
> um dos quatro, eles vencem.**
>
> **O método operacional está nos handoffs, e continua valendo:**
> [`HANDOFF.md (anexo, sec. `HANDOFF_SLIDES.md`)`](_preparacao/HANDOFF.md) (como trabalhar no deck) e [`HANDOFF.md`](_preparacao/HANDOFF.md)
> (estado, build, os sete casos de "o instrumento passou porque mediu outra coisa"). **Leia os dois.**

---

## 0 · O sumário executivo, em sete linhas

1. **O relógio é o problema, não a densidade de tela.** Fala medida: **8.837 palavras = 63 min a 140 ppm**, contra o teto de **50 min** do Art. 23. Cortar tela já foi tentado duas vezes e comprou **zero** minutos.
2. **A única alavanca que corta tela e relógio ao mesmo tempo é trocar prosa por figura.** O deck tem **6 `\includegraphics` e zero `tikzpicture` em 103 frames** — contra 83 `itemize`, 84 `minipage` e 23 `tabular`. O do a defesa de referência tem figura ou tabela na maioria dos slides de conteúdo. **O deck dele mostra; o nosso conta.** Um diagrama substitui fala; um marcador reescrito, não — e é por isso que as duas varreduras de densidade não compraram minuto nenhum.
3. **O corpo pequeno é causa, não sintoma.** **217** comandos de redução de corpo contra **um** `\normalsize`. Corpo pequeno é o que permitiu a densidade; subir o corpo força a brevidade sozinho.
4. **`\scriptsize` e `\small` não passam.** A régua correta não é pt, é altura-de-x sobre altura-da-imagem (§2). No Meet, num notebook, os dois falham.
5. **O negrito parou de sinalizar.** 706 `\textbf` em 103 frames ≈ 7 por tela. A curva dose-resposta da sinalização é medida: 10 marcações d=0,45 · 18 d=0,58 · **27 d≈0**.
6. **Falta respiro, e agora há um número para isso.** A tinta do corpo desce, na mediana, a **0,912 da altura** da tela. No PDF de demonstração **do mesmo template**, feito pelo autor do template, a mediana é **0,750**. Sessenta das cem páginas de conteúdo passam de 0,90; a do veredito chega a **0,996** — a última linha para praticamente na borda inferior, no mesmo nível do número do frame.
7. **A referência de ritmo é 48 s/slide** (medida, §3). A fala atual roda a **68 s/slide**.

---

## 1 · As réguas que não se negociam

| régua | valor | fonte |
|---|---|---|
| **Duração da apresentação** | **máximo 50 min** | Art. 23 do regimento PPGCC-UFV. É a **única** regra oficial sobre a apresentação: sem estrutura obrigatória, sem número de slides, sem exigência de idioma |
| **Aprovação** | **unânime** | Regimento PG UFV, Art. 67 §7. Projete para o examinador menos convencido |
| **Meio** | Google Meet, tela compartilhada | Sem norma. A régua de legibilidade é a janela do Meet, ~1230 px de largura |
| **Ordem da arguição** | provavelmente o externo primeiro | Não fixada pelo Art. 23. Prior forte, não garantia. Consequência: as definições da Seção 1 têm de ser autossuficientes |
| **Janela reservada** | 2h30 no total | Apresentação ≈ um terço da sessão. A arguição é mais longa que a fala |

⚠ **Um teto não é uma instrução para preenchê-lo.** A recomendação convergente das fontes
institucionais é aterrissar em **75–85% do permitido** — aqui, **38–42 min**. Estourar come o tempo
da banca e lê-se como preparação ruim. A defesa do a defesa de referência aterrissou em ~51 min, praticamente no
teto; funcionou, mas não é margem que se planeje.

**A régua que a banca aplica, e que não está em regimento nenhum:** o texto, já lido, decide o
resultado. A apresentação é o primeiro contato ao vivo, não a peça que muda o veredito. Isso baixa o
custo de uma imperfeição pontual e **eleva muito o custo de parecer não dominar o próprio trabalho**
— um número que não bate com a Tabela 9/10, uma notação que diverge do documento, um termo que muda
de nome entre slides. O levantamento completo está em
[`../reviewers/research/banca_evaluation_research_2026-07-20.md`](../reviewers/research/banca_evaluation_research_2026-07-20.md).

---

## 2 · A régua de tipo, medida

Esta é a seção mais útil do documento, porque **corrige uma régua errada que estava em uso**.

### 2.1 · A conversão, e de onde ela sai

O `nesped.sty` fixa `\geometry{paperwidth=16cm, paperheight=9cm}` — **160 mm de largura**, não os
128 mm padrão do beamer. Um slide 16:9 de PowerPoint tem 13,333 in = **338,7 mm**. Logo:

> **1 pt neste deck aparenta 2,117 pt na escala em que todo guia de apresentação foi escrito.**

Daí a escala completa (verificada medindo caixas de palavra no PDF construído, `pdftotext -bbox`):

| comando | pt no `.tex` | pt-equivalente | alturas de imagem que cobre |
|---|---:|---:|---:|
| `\tiny` | 6 | 12,7 | 2,08 |
| `\scriptsize` | 8 | **16,9** | **2,77** |
| `\footnotesize` | 9 | 19,1 | 3,12 |
| `\small` | 10 | 21,2 | 3,47 |
| `\normalsize` | 10,95 | 23,2 | 3,80 |
| `\large` | 12 | 25,4 | 4,16 |
| `\Large` | 14,4 | 30,5 | 4,99 |
| `\LARGE` | 17,3 | 36,6 | 5,99 |
| `\huge` | 20,7 | 43,9 | 7,19 |

### 2.2 · ⚠ Por que "`\scriptsize` ≈ 16,9 pt, logo passa no piso de 16 pt" está errado

O piso de 16 pt que o `PLANO §8 regra 10` carrega vem de um guia genérico e **não tem geometria
declarada** — é o defeito que a última coluna da tabela acima conserta. A norma de dimensionamento
de imagem (ANSI/AVIXA V202.01, "DISCAS") não mede tipo em pontos: mede **a altura da letra
minúscula contra a altura da imagem projetada**, e exige que ela cubra a distância do espectador
mais distante. A regra em uma linha:

> **distância máxima, em alturas de imagem = 2 × (altura-de-x ÷ altura-da-imagem, em %)**
>
> Nesta geometria, com a fonte padrão do beamer, isso reduz a: **D/H máximo = pt ÷ 2,884**.

Uma segunda norma, ergonômica e independente (ISO 9241-303), chega ao mesmo lugar por outro
caminho: altura de caractere ≥ 16 minutos de arco, com 20–22 como alvo. O DISCAS BDM equivale a
17,2 minutos de arco de altura-de-x. **Duas normas independentes convergem.**

**Agora aplique ao Meet.** A banca assiste numa tela de notebook ou monitor, não numa sala:

| cenário do examinador | largura do slide na tela | altura H | distância D | **D/H** |
|---|---:|---:|---:|---:|
| monitor 27", slide ocupando ~80% da altura | ~480 mm | 270 mm | 600 mm | **2,2** |
| notebook 15", Meet em tela cheia | ~300 mm | 169 mm | 550 mm | **3,3** |
| notebook 13", Meet numa janela de ~1230 px | ~244 mm | 137 mm | 500 mm | **3,7** |

Cruzando com a tabela de §2.1:

- **`\scriptsize` cobre 2,77.** Falha no notebook 15" e no 13". Passa só no monitor grande.
- **`\small` cobre 3,47.** Falha no 13". Marginal no 15".
- **`\normalsize` cobre 3,80.** Passa nos três, sem margem.
- **`\large` cobre 4,16.** Passa com margem.

> **A regra desta defesa: `\normalsize` é o piso do corpo; `\large` é o alvo. `\scriptsize` e
> `\small` só sobrevivem em nota de rodapé, legenda de tabela e proveniência — nunca em conteúdo
> que a banca precise ler para acompanhar o argumento.**

⚠ **E isso é mais duro do que parece**, porque hoje o deck tem **98 `\scriptsize` + 95 `\small` + 22 `\footnotesize`
+ 2 `\tiny` = 217 reduções contra 1 `\normalsize`**. Subir o corpo **não é um ajuste
cosmético: é o mecanismo que força a brevidade**, exatamente como o `HANDOFF.md (anexo, sec. `HANDOFF_SLIDES.md`) §1.1` regra 6
já dizia. A diferença é que agora há uma aritmética por trás.

### 2.3 · Os defaults do beamer que caem abaixo do piso sozinhos

Verificado em `beamerfontthemedefault.sty`, e o `nesped.sty` **não corrige nenhum deles**:

| elemento | default | cobre | veredito |
|---|---|---:|---|
| `caption` | `\scriptsize` (nesped) | 2,77 | **reprova** |
| `framesubtitle` | `\small` (nesped) | 3,47 | marginal |
| segundo nível de `itemize` | `\small` | 3,47 | marginal |
| `frametitle` | `\Large` bold | 4,99 | passa |
| título de bloco | `\large` | 4,16 | passa |

**A falha é invisível para quem escreve**: basta indentar um marcador um nível, ou pôr uma legenda
de figura com os números, e o tipo cai sozinho — justamente onde a banca procura evidência.
**Corrija explicitamente** ou elimine a necessidade (um só nível de marcador; o conteúdo da legenda
vai para o `\framesubtitle`).

### 2.4 · Figuras obedecem a uma régua mais dura

Para uma figura da qual a plateia precisa ler detalhe fino (rótulo de eixo, barra de erro, curva
fina), o limite não é acuidade de letra (5 min de arco) e sim **acuidade de linha: 1 minuto de
arco**. Consequência prática, e é o defeito mais comum de deck de ML:

> Uma figura do matplotlib com linhas de 1,5 pt e eixos de 0,8 pt, inserida com
> `\includegraphics[width=0.5\textwidth]`, vira **0,75 pt e 0,40 pt na tela**. O limite de acuidade
> a 6 alturas de imagem é **0,45 pt**. Os eixos literalmente desaparecem.

**A regra: nunca reduza uma figura.** Regenere-a no tamanho final, com o corpo da fonte da figura
ajustado para cair em `\normalsize`–`\large` **na tela**, e todo traço ≥ 1,5 pt depois da escala.
No deck atual isso vale para as seis figuras que existem, e vale antes de qualquer diagrama novo.

### 2.4b · ⚠ A altura útil depende do TÍTULO, e isso acopla duas decisões que pareciam separadas

Medido no deck: a faixa colorida do `\frametitle` **não tem altura fixa** — ela cresce com o
título. Entre um título de uma linha e um de duas (ou um com `\framesubtitle`), a base da faixa vai
de **0,186** a **~0,227** da altura da página.

| se o `\frametitle` … | base da faixa | altura útil até o limite de 0,935 |
|---|---:|---:|
| couber em **uma** linha | 0,186 | **67,4 mm** |
| quebrar em **duas**, ou levar subtítulo | ~0,227 | **63,7 mm** |

São **3,7 mm**, quase uma linha de texto inteira.

> **A consequência, e ela é contra-intuitiva: num slide de diagrama, um título de duas linhas custa
> a linha de conclusão.** Quem escolhe o título e quem dimensiona a figura estão decidindo a mesma
> coisa por dois lados. Nesses slides a escolha de §4.5 (título curto × título com afirmação no
> subtítulo) deixa de ser só hierarquia e vira orçamento de caixa.

**Ordem prática:** feche o título primeiro, meça a faixa naquele slide, e só então dimensione a
figura. Um diagrama de 58,6 mm num slide de 67,4 deixa **8,8 mm** — duas linhas de `\small`, ou um
bloco e nada mais. Não cabe figura + legenda + conclusão.

### 2.4c · A régua para escolher QUEM fica maior quando dois elementos são obrigatórios

Vem de um caso real: o slide do veredito carrega uma tabela **e** três linhas de texto que a lei
obriga, e os dois não cabem juntos no mesmo corpo. Qual sobe?

> **O que a tela precisa carregar sozinha tem prioridade de corpo sobre o que a fala carrega junto.**

No caso: **os números da tabela não são ditos em voz alta; as ressalvas são.** Quem não consegue ler
o intervalo de confiança **não consegue avaliar a afirmação**; quem não consegue ler a ressalva
**vai ouvi-la**. Tabela em corpo maior, texto de lei em corpo menor — **e nenhuma palavra cortada**,
porque a regra de presença (`PLANO §8` regra 6) fala de acompanhar, não de tamanho.

#### ⚠ E a exceção, que descobri quebrando-a (27/08)

O contrato irmão dessa regra é: **cortar da tela não perde conteúdo se a fala o carrega**, e a
verificação é ler a fala antes de cortar. **Isso vale para a maioria e é FALSO para uma classe.**

> **Uma cláusula auto-incriminatória não se preserva mandando-a para a fala — ela muda de
> significado.** Dita mas não projetada, lê-se como concessão feita a contragosto; projetada,
> lê-se como honestidade oferecida antes de ser cobrada.

**O caso:** o slide 42 tinha *"absolute scores are optimistic"* na tela, e o `SLIDES.md`
registrava desde 24/08 **por que ela ficava**: mandá-la para a fala *"pareceria escondê-la"*.
Numa reescrita ela foi para a fala — **e a verificação de cobertura passou**, porque a fala de
facto a dizia. **A regra genérica aprovou o que a decisão específica proibia.**

**Como reconhecer** — e a linha é fina, mas é decidível:

| a cláusula qualifica… | onde vive |
|---|---|
| **um NÚMERO que está na tela** | **fica na tela.** Ela desce junto com o número — é o que a `R6` quer dizer com *a ressalva acompanha o resultado* |
| **uma ESCOLHA DE MÉTODO sem número associado** | pode viver na fala e na reserva |

*"absolute scores are optimistic"* qualifica os escores que a banca está olhando → **fica**.
*"a convenção alternativa nos favoreceria e nós a recusamos"* qualifica uma decisão de protocolo,
e o slide dela é só a fórmula → **pode sair**.

⚠ **E separe erro de escolha.** A primeira saiu **contra uma decisão registrada que ninguém leu**;
a segunda **o autor decidiu sabendo o que saía**. O critério acima decide onde a cláusula *deve*
viver; **só o autor decide abrir mão dela.**

**Estado do deck (27/08):** a trilha principal mantém **quatro** cláusulas desta classe na tela —
`absolute scores are optimistic` (42) · `Not width-matched` (26) · `this chapter does not isolate
each encoder` (26) · `the evidence does not separate the contributions of the shared trunk and the
private spatial path` (33).

**A defesa:** antes de mover qualquer coisa para a fala, **leia o bloco do `SLIDES.md` daquele
slide**, não só a fala. As decisões sobre **onde** uma cláusula tem de viver moram lá, e **não
aparecem em varredura nenhuma** — nem no `diff_fala`, nem num `grep` de termos.

⚠ **A régua não autoriza encolher o que a fala cobre até o ilegível.** Ela ordena a prioridade
quando há disputa; o piso de §2.2 continua valendo para tudo que a banca precise ler para
acompanhar.

### 2.5 · Comprimento de linha

Medido nesta geometria, a `\textwidth` cheia comporta: `\footnotesize` 103 caracteres ·
`\small` 95 · `\normalsize` 87 · `\large` 81 · `\Large` 68. A banda que a literatura tipográfica
sustenta é **≤ 70**, com ~66 ideal.

O que torna isso útil é a convergência: **a mesma subida de corpo que conserta a legibilidade
conserta a medida**. E se nenhum bloco de texto passar de duas linhas — que é a regra de composição
de §4.3 — a medida deixa de importar.

---

## 3 · A referência medida: a defesa do a defesa de referência

🛑 **A GRAVAÇÃO FOI APAGADA EM 28/08/2026**, por decisão do autor (conteúdo pessoal de
terceiro, cópia única). Era
`presentation/exemples/Screen Recording 2026-07-08 at 10.02.56.mov` — 7,04 GB, 3.679 s,
4096×2304, 60 fps. **O método e os valores desta seção ficam; a evidência primária não é
reverificável.**

⚠ **E o aviso que estava escrito aqui estava certo, e não foi executado:** *"ela não está no git —
`articles/dissertacao/.gitignore` ignora `exemples/`, e o backup em
`~/Backups/dissertacao_exemples_2026-08-20.tgz` é de 20/08, anterior ao vídeo. Se o arquivo sumir
do disco, some de vez."* **Sumiu.** Confirmado em 28/08: nem o tarball nem
`/Volumes/linux/VIDEO/` a tinham. **Um aviso registado não é uma salvaguarda** — é a mesma classe
do `slide_final.pdf`, que ficou a um `git clean` de distância com o acidente já documentado no
próprio `.gitignore`.

**O que exatamente deixou de ser verificável**, porque a distinção importa para quem citar o §3.1:

| leitura | instrumento | sobrevive? |
|---|---|---|
| 45 s/slide (bloco A) · 37 s/slide (bloco B) | quadros amostrados da gravação | 🛑 **não** — só o número, sem a fonte |
| ~11 min do slide final na tela | idem | 🛑 **não** |
| §3.2 inteiro (títulos, ausência de bloco colorido) | observação direta da gravação | 🛑 **não** |
| 48 s/slide (64 slides em ~51 min) | `APRESENTACAO_DEFESA_GUIDE.md` §4.0 | ✅ **sim** — é documento |

> ⚠ **A convergência de §3.1 perde duas das três pernas.** Ela valia por as três leituras **não
> partilharem instrumento**; hoje duas delas não têm mais como ser refeitas. **O alvo de ~48 s por
> slide continua defensável** — vem da perna que sobreviveu — **mas não o chame mais de
> triangulação.**

⚠ **Não é PDF.** Um agente anterior procurou PDF, não achou, e concluiu que a referência não
existia — estando o caminho num documento que ele mesmo escrevera. **Isso continua a valer como
lição**, mesmo agora que o ficheiro não existe.

**Método desta seção:** extraí 41 quadros a cada 90 s com `ffmpeg -ss` antes do `-i` (busca por
keyframe, barata num arquivo de 7 GB), montei folhas de contato e **olhei**. Depois li os números
impressos de slide nos quadros amostrados. Não é a mesma medida da contagem de palavras que já
existia no `HANDOFF.md §4b` — aquela é OCR sobre a gravação, esta é estrutura e ritmo.

### 3.1 · Ritmo

| medida | valor |
|---|---|
| páginas impressas lidas em quadros amostrados, bloco A | p1 → p17 em 12 min = **45 s/slide** |
| idem, bloco B | p41 → p63 em 13,5 min = **37 s/slide** |
| do guia, medido de outra forma (`APRESENTACAO_DEFESA_GUIDE.md` §4.0) | 64 slides em ~51 min = **48 s/slide** |
| slide final (`Agradecimentos`) na tela | **~11 min**, a arguição inteira |

As três leituras convergem em **~40–48 s por slide**, e elas **não compartilham o instrumento**: uma
lê número impresso em quadro amostrado, outra lê os extremos da fala na gravação, a terceira lê
título por banda de cor. (Essa checagem existe porque o §3 do `HANDOFF.md` registra um caso em que
"três medições independentes" partilhavam o mesmo contador.)

**Contra o nosso deck:** 8.837 palavras de fala / 54 slides = **164 palavras por slide = ~70 s a
140 ppm**. Ou seja, **cada slide nosso fala ~45% mais do que a referência**.

> **O alvo derivado, e é a única forma quantitativa de fechar o relógio:**
> 54 slides × 48 s = **43 min** ≈ **6.050 palavras de fala** a 140 ppm.
> Hoje: 8.837. **Cortar ~2.800 palavras (32%), ou ~52 por slide.**

⚠ **O estouro não está espalhado por igual.** Os 12 slides mais falados somam **3.159 palavras =
36% do total em 22% dos slides**: `Result 2` (457), `Result 1` (310), `The measured trade` (284),
`The verdict` (283), `Protocol 4/4` (277), `HGI` (243), `Protocol 2/4` (236), `Protocol 3/4` (231).
**Só o bloco de protocolo (S41–S44) come 744 palavras = 5,3 min.**

### 3.2 · O que o vídeo mostra e a contagem de palavras não capta

**Título.** Substantivo curto e literal, **sempre**: *Introdução Geral · Objetivo · Trabalhos
Relacionados · Fontes de dados & string de busca · Resultados · Considerações finais · Arquitetura
de FL · Arquitetura de ML · Estudo de caso · Métricas em classificação do lixo · Trabalhos futuros ·
Agradecimentos*. **Zero analogia, zero frase, zero trocadilho.** A única exceção é a família de
slides de pergunta de pesquisa, cujo título **é** a pergunta: *"RQ1: Qual a distribuição anual dos
estudos?"*.

**Bloco colorido.** Ele **não usa nenhum**. Nem `block`, nem `alertblock`, nem `exampleblock`. O
único elemento colorido da tela é a faixa do frametitle e a barra de navegação. O corpo é `itemize`
puro mais figura ou tabela.

**Slide de resultado.** Título + tabela (ou figura) + legenda numerada + número da página. **Sem
interpretação ao lado.** Quando há uma conclusão, ela é **um** marcador curto abaixo da figura:
*"Medianas próximas e diferença no erro inferior a 1 na maioria dos casos."*

**Respiro.** Em vários slides o conteúdo ocupa ~60% da altura e o resto é branco. **O vazio dele não
é sobra: é composição.** No nosso deck praticamente todo slide vai até a borda inferior.

**Layout.** Duas colunas é o dominante — marcadores de um lado, figura ou tabela do outro.

**Marcador.** Três a cinco por slide, fragmento terminado em `;`, o último em `.`, citação `[7, 36]`
inline. Corpo grande: ele **não usa `\scriptsize`**.

**Fecho.** *"Obrigado pela atenção!"* + nome + e-mail. Três linhas, e fica na tela a arguição
inteira.

### 3.3 · Onde nós somos melhores, e vale preservar

- **Convenção de ranking.** Ele **não** marca melhor e segundo colocado. Nossa convenção
  negrito = melhor, sublinhado = segundo é um acréscimo nosso e é uma melhoria — o
  `considerations.md` manda estendê-la a todas as tabelas, e isso está certo.
- **Barra de navegação com seis seções.** Os dois usam; no nosso ela narra a linhagem de modelos, o
  que é mais informativo que rótulos genéricos.
- **`\specialframe` para transição.** Ele não usa. Os nossos slides 23 e 31 são, na varredura visual,
  os que melhor funcionam do deck inteiro.

---

## 4 · O que a literatura estabelece, e o que é folclore

⚠ **Aviso de qualidade de fonte.** A web aberta sobre este assunto está dominada por texto gerado
por máquina que afirma números precisos ("15–20 slides", "24 pt de corpo", "um slide por 1,5 min")
sem fonte nenhuma, e se contradiz entre páginas do mesmo domínio. **Nada disso entrou aqui.** Cada
item abaixo traz a força da evidência declarada.

### 4.1 · O que tem estudo controlado

| achado | efeito medido | o que isso obriga |
|---|---|---|
| **Estrutura afirmação-evidência** (título é uma frase que declara o achado; corpo é evidência visual, não lista) | Garner & Alley 2013, N=110, narração idêntica de 1.000 palavras, só a estrutura do slide varia: compreensão d=0,81; retenção a 10 dias d=0,89; **menos concepções erradas** d=0,47; **menor esforço mental percebido** d=−0,50 | é a **única** intervenção de design de slide com ensaio randomizado a favor |
| **Redundância** — nunca projetar a frase que você vai dizer | 16 de 16 testes, d mediana 0,86. Yue, Bjork & Bjork 2013, N=105: texto **abreviado e reescrito** bate texto idêntico em recordação, d=0,95 | a ressalva vai para a fala; o que fica na tela é paráfrase mais curta, **não transcrição** |
| **Coerência** — apagar tudo que não sustenta a afirmação do slide | 23 de 23 testes, d mediana 0,86 | decoração, logo repetido, coluna extra de tabela, legenda não usada: fora |
| **Contiguidade espacial** — o rótulo em cima da coisa, nunca numa legenda | 22 de 22 testes, d mediana > 1,0 | anote direto no gráfico; legenda separada é carga extra pura |
| **Contiguidade temporal** — diga enquanto está na tela | 9 de 9 testes, d mediana 1,22 | proíbe "isso vocês vão ver daqui a dois slides" e "voltando à figura de antes" |
| **Sinalização** — marcar onde olhar | 103 estudos, N=12.201: retenção g=0,52; transferência g=0,31. Dose-resposta: 27 marcações → d≈0; 18 → 0,58; 10 → 0,45 | **marcar demais é o mesmo que não marcar.** Os 706 `\textbf` do deck estão do lado errado dessa curva |
| **Segmentação** — uma afirmação por frame | 10 de 10, d mediana 0,79 | um `and` unindo duas afirmações no título significa dois slides |
| **Jargão** — definir não conserta | Bullock et al. 2019, N=650: jargão piora a fluência de processamento (p<0,001); **definir não repara** (p=0,543) | não basta expandir a sigla na primeira aparição |
| **Polaridade** — texto escuro sobre fundo claro | Buchner & Baumgartner 2007: vantagem a 5 lux **e** a 550 lux; Piepenbrock et al. 2014: a vantagem **cresce quando o tipo é pequeno** | o fundo claro do `nesped` está certo |

**A armadilha metacognitiva, e ela importa aqui:** a plateia **prefere** a versão que aprende pior.
No estudo de Yue et al., a maioria julgou o texto idêntico "melhor para aprender" (χ²=20,15,
p<0,001) enquanto tinha desempenho pior; no de Garner & Alley, o grupo afirmação-evidência avaliou a
quantidade de texto como **menos adequada** (d=−0,60) enquanto aprendia significativamente **mais**.
**Conforto da banca não é evidência.**

### 4.2 · ⚠ A ressalva que muda o peso disto tudo: a banca é especialista

Mayer & Fiorella declaram três condições de contorno para o efeito de redundância, **e as três estão
vivas numa defesa**: o efeito "pode ser eliminado ou até revertido quando os aprendizes são
experientes, quando o texto na tela é curto, ou quando o material não tem gráficos". Kalyuga,
Chandler & Sweller encontraram o efeito em aprendizes de baixa experiência e **não** nos de alta —
a reversão por expertise. E a meta-análise de Adesope & Nesbit (57 estudos) achou que falado +
escrito **bate** falado sozinho quando não há gráfico (d=0,24).

**Consequência prática, e é o oposto de "tire todo o texto":**

- Num slide **com** figura ou diagrama, prosa duplicada é dano. Ali vale a régua estrita.
- Num slide **sem** gráfico — uma definição, uma equação, a pergunta de pesquisa, uma tabela — texto
  na tela **não** é redundância nociva para esta plateia. É por isso que o slide 3 do a defesa de referência tem
  ~70 palavras numa pergunta emoldurada e funciona.
- **Número que a banca precisa reter fica na tela.** Alley et al. mediram isto: estatística
  **impressa** foi recordada por 87% contra ~50% quando apenas falada. Apagar um número
  carregador em nome de minimalismo é perder a informação, não enxugá-la.

> **A síntese que este deck deve seguir: corte pela FUNÇÃO, não pela contagem.** A ressalva, a
> justificativa e a explicação saem da tela e vão para a fala. A afirmação, o número que sustenta o
> veredito e a definição ficam.

### 4.3 · O que é consenso de especialista, com mecanismo

- **Bloco de texto ≤ 2 linhas**, incluindo o título. Lista, quando existir, com **2 a 4 itens**.
- **Título à esquerda, no alto**, no máximo duas linhas.
- **Respiro interno vale mais que margem.** Projetado, o branco da borda quase não é percebido; o
  branco **entre** blocos é o que agrupa. Não resolva slide cheio encolhendo o conteúdo para o
  meio: apague conteúdo e abra os intervalos.
- **Uma mensagem por slide.** Teste do relance: a plateia pega o ponto olhando, sem você.
- **Slide de estrutura tem de parecer diferente de slide de conteúdo.** O `\specialframe` e o
  `\autotocframe` já resolvem isso aqui.
- **Orçamento de leitura ~20 palavras por minuto de fala.** É heurística de projeto, não limiar
  medido — mas serve de auditoria: dá para contar no `.tex`.
- **Ao menos um minuto por slide.** Contando um `frame` com overlays como **um**.
- **Termine na conclusão, não no "Obrigado".** Duas fontes independentes convergem: o último slide
  projetado durante a arguição deve ser a contribuição ou a conclusão, porque é o que a banca fica
  olhando por vinte minutos ou mais.

⚠ **Este último colide com duas coisas daqui**: o `considerations.md` pede um slide final de
agradecimentos, e a referência do a defesa de referência deixa o "Obrigado" na tela a arguição inteira. **A
reconciliação que eu recomendo, e que não custa nada: diga o agradecimento sobre o slide de
agradecimentos, e então volte um slide para a conclusão e deixe ELA projetada.** Decisão do autor.

### 4.4 · O que é folclore, e não deve ser citado como regra

| regra | veredito |
|---|---|
| **6×6 / 7×7 / 5×5** | Sem base empírica nenhuma. Tufte a cita justamente para atacá-la. E ela otimiza a coisa errada: manda **abreviar**, não **esclarecer**, e pressupõe a lista de marcadores — a estrutura que a única intervenção testada manda abandonar |
| **10/20/30 (Kawasaki)** | Escrito para pitch de investidor, explicitamente não para palestra de pesquisa |
| **4/6/8** | A própria AVIXA a lista num slide intitulado *"The Old Way of Doing Things"* e a substituiu formalmente em 2016. Não tem termo de tamanho de conteúdo: diz onde sentar, não como dimensionar o tipo |
| **"a atenção colapsa aos 10–15 min"** | Sem suporte. O que se mede é entra-e-sai contínuo desde ~30 s. Não reestruture a fala por causa disso; **crie pontos de reentrada a cada ~5 min** (um divisor, uma pergunta repetida, uma recapitulação de uma linha) |
| **"nunca ponha texto no slide"** | Leitura exagerada do princípio de redundância — ver §4.2 |
| **entrelinha de 1,3–1,5** | Craft tipográfico, sem estudo para slide projetado. E custa altura, que é o recurso mais escasso numa tela de 90 mm |

### 4.5 · Duas tensões reais, que este deck tem de resolver escolhendo

**Tensão 1 — título-afirmação contra título curto.** A literatura empurra para "título é uma frase
que declara o achado". O **autor pediu o contrário** no `considerations.md`: títulos diretos,
descritivos, sérios, sem analogia. E a referência do a defesa de referência dá razão ao autor: os títulos dele são
substantivos literais.

> **Resolução recomendada, e ela satisfaz os dois:** `\frametitle` curto e literal
> (*"Resultado: representação"*), `\framesubtitle` carregando a afirmação do slide. O template já
> desenha os dois na mesma faixa, com hierarquia. **Custa zero linha de corpo** e mantém a lei do
> autor.
> ⚠ Se adotar, suba o `framesubtitle` de `\small` para `\normalsize` (§2.3).
>
> ⚠ **A redação da afirmação NÃO é decisão de forma.** Ela cai sob a lei dos verbos
> ([`../WRITING_LAW.md`](../WRITING_LAW.md) §3 e o `HANDOFF.md` §6): *supera* só nas três células
> com teste pareado, *empata* / *matches* / *ties* / *em todos os conjuntos* banidos como veredito.
> **Este documento não escreve nenhuma afirmação de exemplo, de propósito** — um exemplo inventado
> aqui vira, por cópia, uma afirmação no deck. Peça a redação ao `gate`.

**Tensão 2 — legibilidade contra afirmação.** Subir o corpo reduz o que cabe; a afirmação no título
gasta linha. São conciliáveis só por redução de conteúdo. **O teste conjunto:** *o título é
específico E cabe em duas linhas no corpo em que está?* Um slide que precisa de três linhas de
título é um slide com duas ideias.

---

## 5 · O template NESPeD, medido

Verificado compilando um specimen isolado que exercita cada componente, e medindo o PDF resultante.
O specimen não toca em nada do deck.

### 5.1 · O que existe, e para que serve

| recurso | uso certo | ⚠ |
|---|---|---|
| `\titleframe{\titlelogo{…}}` | capa com logos | os cartões de logo **devem** ficar colados ao topo — é o desenho, não defeito. Decisão do autor, `\vskip-2mm` restaurado |
| `\autotocframe{sectionstyle=…, subsectionstyle=hide}` | divisor automático em toda `\section` | com `subsectionstyle=show/…` o recap **estoura** com a profundidade deste plano |
| `\tocframe[…]` | recapitulação sob demanda | fundo em degradê, barra esmaecida |
| `\specialframe` (envolver o frame em chaves) | **uma frase, tela inteira** | o melhor recurso do template para transição e veredito |
| `block` / `exampleblock` / `alertblock` | verde / azul-marinho / magenta | ver §5.3 sobre semântica |
| `\miniframesoff` / `\miniframeson` | tirar a série B da contagem | o número do frame **congela** ali |
| `\insertframenumber` no rodapé | slides numerados | conta **frame**, não slide: overlays não inflam |
| `\alert{}` | destaque inline em magenta | 6,04:1 sobre branco, aprovado |
| `lstlisting` com `mystyle`, `algorithm2e` em português | código e pseudocódigo | não usados no deck; disponíveis |
| `adjustbox` com `export` | `\includegraphics[max height=…]` | útil para caber figura sem distorcer |
| `animate` | animação | carregado; não use |

**Opções do pacote:** decoração `net` \| `accel` \| `data`; cor `green` \| `blue` \| `red`.
⚠ **`red` está declarada vazia no `.sty`** — não define cor nenhuma. Não usar. O deck usa
`[net,green]`.

### 5.2 · Contraste da paleta, calculado

| par, como é de fato desenhado | razão | WCAG |
|---|---:|---|
| branco sobre `alertshade` (título do alertblock) | 8,60:1 | AAA |
| branco sobre `secondaryshade` (título do exampleblock) | 9,83:1 | AAA |
| preto sobre `alerttint` / `secondarytint` (corpos) | 18,6 / 17,4 | AAA |
| `secondary` sobre branco | 9,83:1 | AAA |
| `alert` sobre branco (`\alert{}`) | 6,04:1 | AA |
| **branco sobre `primaryshade` (a faixa do frametitle)** | **3,33:1** | só como texto grande |
| **`primaryshade` como texto sobre branco** | **3,33:1** | **reprova para corpo** |
| **branco sobre `primary` (a ponta CLARA do degradê)** | **2,67:1** | **reprova** |
| branco sobre `secondary` (a ponta escura do degradê) | 9,83:1 | AAA |
| `primarysuper` sobre branco | 1,31:1 | invisível |

**As três consequências:**

1. **Nunca ponha texto pequeno na faixa do frametitle.** O título passa por ser grande e negrito; um
   `\framesubtitle` em `\small` está no limite. Se o subtítulo virar carregador de afirmação (§4.5),
   suba-o para `\normalsize` — aí ele passa com folga como texto grande.
2. **`primaryshade` não serve de cor de prosa.** Serve de marcador, de filete e de número grande em
   negrito. Prosa em verde sobre branco reprova.
3. ⚠ **Na capa e em todo `\specialframe`, o texto tem de morar na metade escura do degradê.** O
   degradê corre de `primary` (claro, 2,67:1) a `secondary` (escuro, 9,83:1) a 45°. Texto branco no
   canto superior esquerdo está no pior lugar possível. Hoje a capa põe o título exatamente ali —
   ele sobrevive por ser grande e negrito, mas é a única coisa que o segura.

⚠ **E o número acima é otimista**, porque contraste de projeção e de vídeo comprimido é pior que
contraste calculado em sRGB. Para um deck que vai por compartilhamento de tela num Meet, **trate
AA como reprovação e mire AAA (7:1)**.

### 5.3 · Semântica de bloco: a regra que falta

Hoje os três blocos aparecem sem semântica fixa. O `alertblock` magenta é usado para ressalva, para
pergunta herdada, para mudança de par de tarefas e para armadilha de nome. Quando a cor mais forte
da paleta significa quatro coisas, ela para de significar qualquer uma — é literalmente a curva
dose-resposta de sinalização de §4.1.

> **A convenção proposta, uma cor por função, e nada mais:**
>
> | bloco | cor | e só |
> |---|---|---|
> | `block` (verde) | neutro | a afirmação do slide, ou uma definição |
> | `exampleblock` (azul) | apoio | o que o capítulo estabelece, proveniência, convenção |
> | `alertblock` (magenta) | **ressalva** | **no máximo um por slide, e só quando limita um resultado** |
>
> Bloco de título vazio (`\begin{block}{}`) é o recipiente certo para **uma frase que precisa
> dominar a tela** — a pergunta de pesquisa, o veredito.

### 5.4 · Armadilhas do template, todas verificadas

1. ⚠ **O motor é `xelatex`.** Sob `pdflatex` o build "passa" e a capa e todos os divisores saem **em
   branco** — texto branco sobre um degradê que não desenhou. Um teste de texto aprovaria.
2. ⚠ **Duas passagens são obrigatórias.** Medi: com um passe só, a **capa e todos os `\tocframe`
   saem em branco**, porque `\tikz[remember picture, overlay]` precisa do segundo passe.
   **`make check` é passe único** — o PDF dele sempre parece quebrado. Não julgue por ele; use
   `make all`.
3. ⚠ **`\begin{frame}{título}{subtítulo}` é sintaxe válida.** Abrir o corpo com uma chave —
   `{\footnotesize …}` — manda o conteúdo para **dentro da faixa colorida do título**. Zero erros no
   log, e o texto **está** no PDF, então a canária dá 100%. Abra o corpo com `\vspace`, `\par`,
   `\noindent` ou um `\begin{block}`.
4. ⚠ **`tikz` vem com `calc` e `shadows` só.** `positioning` **não** vem: `right=of` produz seis
   erros de PGF Math. Adicione `\usetikzlibrary{positioning}` antes de desenhar.
5. ⚠ **Em slide de duas colunas, largura não é alavanca — ela muda de vítima.** Alargar uma coluna
   estreita a outra, e num slide no limite isso só transfere o estouro. As alavancas que removem
   altura, nesta ordem: **cortar conteúdo → reduzir o corpo → só então largura.**
6. ⚠ **Nunca `\vspace` negativo.** O deck acumulou 31 deles; eles não criavam espaço, puxavam o
   conteúdo para cima do elemento anterior. O log ficava limpo e a tela ficava sobreposta.
7. ⚠ **`Overfull` deixou de ser zero de propósito.** Zerar o log empurrando conteúdo de volta recria
   exatamente o defeito que a varredura de 24/08 corrigiu.
8. **Quatro bugs do template estão corrigidos só na nossa cópia**, cada um com errata datada no
   `.sty`: `\pagewidth`→`\paperwidth`; o `\autotocframe` que vazava o argumento; o `\decorationnet`
   que nunca desenhava a malha; e `width=\textwidth`→`\linewidth` em `\beamerboxesframed` (que fazia
   todo bloco em coluna vazar por baixo do vizinho). **Não os reverta.** E ⚠ **nem toda diferença
   em relação ao original é bug**: um quinto "conserto" foi revertido pelo autor.

### 5.5 · Padrões de composição que este template desenha bem

Testados no specimen, com render conferido:

- **Número grande.** `\Huge` em `primaryshade` negrito, três colunas, rótulo em `\small` embaixo. É
  a forma mais legível que existe para um delta. Substitui uma tabela inteira quando a mensagem é
  "estes três números".
- **Tabela com respiro.** `booktabs` + `\renewcommand{\arraystretch}{1.35}` + corpo `\small` ou
  maior, centrada, com o delta colorido. Lê bem à distância. ⚠ O `nesped.sty` aplica
  `\vspace{-5mm}` no fim de todo ambiente `table` — conte com isso.
- **Uma frase na tela inteira.** `\specialframe` com `\vfill … \Large … \vfill`. É o melhor recurso
  do template e está subutilizado: quatro usos em 103 frames.
- **Diagrama em TikZ com a paleta.** Nós `rounded corners=1mm`, `fill=primarytint`,
  `draw=primaryshade`, setas em `secondary`; o ramo de categoria em `alerttint`, o de região em
  `secondarytint`. Fecha o loop com a identidade visual sem parecer colado.
- **Dois blocos empilhados** em vez de lado a lado, quando o conteúdo é sequencial e não paralelo —
  é o que o `considerations.md` pede no slide 17, e é a composição certa: colunas afirmam paralelismo.

### 5.6 · Três coisas de mecânica do beamer que valem para este deck

**Já estão certas, e não devem ser mexidas:** as 15 chamadas de `columns` usam
`[T,onlytextwidth]` / `[t,onlytextwidth]` — sem `onlytextwidth` o bloco de colunas sai 3,4 mm à
esquerda de todo o resto do slide, **sem aviso nenhum**. E os 49 frames da série B usam
`[noframenumbering]`, então não inflam o contador que a banca vê.

### 5.6b · ⚠ As duas opções de classe estão FECHADAS, e uma delas foi medida

**Decisão do autor, 2026-08-26. Não reabrir.**

| opção | veredito |
|---|---|
| `\documentclass[t]{beamer}` (ancorar no topo) | **RECUSADA.** Testei num frame e mostrei o render. O autor prefere o corpo **centrado na vertical**, que é o default do beamer e é o que o a defesa de referência faz. `main.tex` voltou byte-idêntico |
| `\documentclass[12pt]{beamer}` (subir o corpo) | **RECUSADA**, e o experimento diz por quê |

**O experimento do corpo, rodado numa cópia isolada:** um **único degrau** em todo o deck
(`\tiny→\scriptsize`, `\scriptsize→\footnotesize`, `\footnotesize→\small`, `\small→\normalsize`;
217 substituições, `\smallskip` preservado), recompilado.

> **De 25 para 50 páginas com `Overfull \vbox`.** 25 estouros novos, 45 páginas agravadas em mais
> de 5 pt. Os piores novos: `The evidence base` **38,5 pt** · `The null result` **28,5** ·
> `Result 2` **19,3**. E o slide do veredito vai de 17,9 para **48,5 pt** fora da caixa.

**A leitura, e ela é mais dura que "alguns slides são de risco": o deck inteiro está dimensionado
para o corpo atual.** Os 217 comandos de redução não são desleixo — foram postos **para caber**.

> **Consequência de método: a régua de §2 continua verdadeira como DIAGNÓSTICO e não é executável
> como POLÍTICA enquanto o conteúdo não encolher.** A ordem é obrigatória e não tem atalho:
>
> **`gate` decide os cortes → o conteúdo encolhe → o corpo sobe → render página a página.**
>
> As duas últimas sem as duas primeiras produzem estouro em massa, e o estouro deste deck é
> silencioso (§5.4).

### 5.6c · A alavanca que ficou no lugar: respiro INTERNO

Recusadas as duas opções globais, o que o autor pediu foi **espaço entre os elementos**, com os
blocos mais para o rodapé. Isso não é um consolo: é a mesma coisa que a literatura recomenda por
outro caminho (§4.3 — projetado, o branco da borda quase não é percebido; o branco **entre** blocos
é o que agrupa).

Cinco tratamentos do mesmo frame, todos compilando com **0 erros e 0 overfull**:

| | tratamento | resultado |
|---|---|---|
| A | como está hoje | a caixa cola na lista; o grupo flutua no meio |
| **B** | **`itemsep 2ex` + 10 mm antes da caixa** | **os itens respiram, a caixa separa, o grupo continua centrado.** É o alvo |
| C | `[s]` com `\vfill` antes da caixa | lista no topo, caixa no rodapé. Funciona, mas deixa de ser centrado |
| D | 18 mm antes da caixa | o intervalo passa a ler como buraco, não como separação |
| E | o respiro de B com o corpo em `\large` | respiro **e** legibilidade — **só onde couber, slide a slide** |

> **A regra: B é o tratamento padrão. E onde sobrar altura, verificado por render. Nunca D.**
>
> ⚠ **Espaço vertical passa a ser alavanca declarada de projeto, não sobra.** Um slide com três
> blocos, sob o tratamento B, vira um slide com dois — porque os intervalos crescem. Quem
> especifica conteúdo precisa saber disso antes de escrever.
>
> ⚠ E `\vspace` **positivo** entre elementos é a ferramenta certa. `\vspace` **negativo** continua
> proibido (§5.4): ele não cria espaço, puxa o conteúdo por cima do vizinho.

**⚠ B também não se aplica em massa, e a razão é medida.** O deck está compresso **de propósito**:
**47 `\setlength{\itemsep}{0pt}`** e **53 `\parskip{0pt}`**. Trocar todos por `2ex` acrescenta
altura a slides que já não têm folga.

**O instrumento que decide: quanto cada página ABSORVE.** Como o conteúdo é centrado, ele cresce
para os dois lados — então a capacidade é `2 × min(folga acima da 1ª linha, folga abaixo da última)`,
com o topo medido a partir da **base real da faixa do título** em cada página (ela varia: 0,171 a
0,348), não de um limiar fixo. Medido sobre as 100 páginas de conteúdo:

| capacidade | páginas | o que cabe |
|---|---:|---|
| ≥ 35 pt | **21** | o B completo |
| ≥ 20 pt | 24 | um B reduzido |
| ≥ 10 pt | 43 | só o `itemsep` |
| ≥ 0 pt | 70 | nada |
| **< 0** | **30** | já estão no limite |

Mediana da capacidade: **7,1 pt**. Ou seja: **o B é tratamento por slide, com portão medido — nunca
uma varredura.**

### 5.6d · Fase A — a cirurgia estrutural, executada e verificada (2026-08-26)

Decisão de conteúdo do autor, via `gate`. Saíram os impressos **6**, **18** e **28**; o **37** foi
movido para abrir `\subsection{O veredito}`.

| | antes | depois |
|---|---:|---:|
| linhas do `main.tex` | 3.365 | 3.264 |
| frames | 103 | 100 |
| páginas do PDF | 111 | **107** |
| slides impressos | 54 | **51** |
| `Overfull \vbox` | 25 | **25** |
| hyperlinks órfãos | 0 | **0** |
| páginas acima de 0,93 | 18 | **18** |

*(−4 páginas para −3 frames: o impresso 28 tinha overlay. E 51, não 50, porque a fusão 4⊕15 é
fase B.)*

**A verificação que importou, e ela é o modelo:**

1. ⚠ **As duas `\subsection` que ficariam vazias saíram junto com os frames.** Uma `\subsection`
   sem frame vira rótulo sem pontinho na barra de navegação — o LaTeX não avisa.
2. **Grafo de hyperlinks conferido antes e depois:** 49 alvos, 49 destinos, **zero órfãos, zero
   alvos sem link** — uma bijeção perfeita, e todos os 49 vivem na série B. Nenhum frame removido
   carregava alvo. **Confira isso ANTES de remover qualquer frame**; é o defeito que compila limpo.
3. **Depois da cirurgia, o número impresso de tudo que vem depois muda.** Não tente prever: leia o
   PDF construído e devolva o mapa medido a quem mantém as referências.

> ⚠ **A armadilha que a Fase A criou, e ela é silenciosa.** Remover frames desloca o número
> impresso de tudo que vem depois. Se o plano de conteúdo já contava com uma remoção que ainda
> **não** foi executada, os dois números existem, os dois apontam para slides reais, e **nada no
> build reclama**. Aconteceu aqui: o mapa do `gate` mirava 50 slides (já com a fusão), o deck estava
> em 51, e tudo a partir do impresso 14 ficou deslocado em um — *"slide 41"* significava
> *Result 2* no plano e *Result 1* no deck.
>
> **As duas regras que decorrem:**
> 1. **Execute primeiro o item que muda a numeração**, e só depois o que é ancorado por ela.
> 2. **Identifique slide por TÍTULO, com o número só como conferência.** Se os dois discordarem,
>    pare e pergunte. ⚠ Duas exceções neste deck: os `\specialframe` de transição **não têm
>    `\frametitle`** (só o número os ancora), e quatro pares compartilham título (os dois
>    *Architecture or representation?* e os quatro *The protocol, in four steps*) — nesses, título
>    **+ subtítulo**.

### 5.6e · O primeiro lote de respiro, aplicado e verificado (2026-08-26)

Dos 21 que cabem, **11 são da série B** — que fica densa de propósito, por decisão do autor
(`HANDOFF.md (anexo, sec. `HANDOFF_SLIDES.md`)` §6). Sobram 10 na trilha principal; exigindo margem de segurança de 8 pt entre
folga e custo, ficam **6**. Aplicados:

| pág. PDF | slide impresso | frame | desceu |
|---:|---:|---|---:|
| 10 | 7 | Related work: POI prediction and multitask learning | 10,1 pt |
| 12 | 9 | How two tasks share a model, and how that fails | 21,6 pt |
| 16 | 13 | The metric all three studies share | 13,9 pt |
| 40 | 33 | Next region: the task, and why it is worth predicting | 12,0 pt |
| 47 | 40 | The protocol, in four steps (1 · the unit of data) | 16,3 pt |
| 48 | 41 | The protocol, in four steps (2 · what is measured) | 10,1 pt |

**Verificação, e ela é o modelo para os próximos lotes:**

- `Overfull \vbox` **25 → 25**, páginas **111 → 111**;
- **exatamente 6 páginas mudaram de altura**, medido por varredura de tinta contra o PDF anterior;
- **nenhuma passou do limite de 0,935** (a maior ficou em 0,910);
- as outras **94 páginas não se moveram**.

⚠ **O log sozinho não teria dito nada disso** — ele daria 25 antes e 25 depois. Quem respondeu foi a
comparação de tinta página a página contra o build anterior. **Guarde o PDF antes de qualquer lote.**

⚠ **Três armadilhas que não mordem hoje mas mordem no primeiro diagrama novo:**

1. **`[shrink]` e `[allowframebreaks]` fazem o `Overfull` sumir do log sem consertar nada.** O
   `allowframebreaks` ainda parte o frame em dois em silêncio. **Não use nenhum dos dois.**
2. **Staging só em TikZ não cria slide.** Se a encenação vier de `visible on=<2->`, o beamer
   renderiza **uma** página com tudo visível e **não avisa**. É preciso declarar o intervalo no
   frame: `\begin{frame}<1-3>{…}`.
3. **Conteúdo escondido por transparência do TikZ continua extraível.** Ele infla contagem por
   `pdftotext` e pode ser selecionado do PDF. Se algo precisa mesmo ficar oculto, use `\only`.

> ⚠ **A armadilha do subtítulo reincidiu em 2026-08-26, comigo, quatro horas depois de eu a
> documentar aqui e avisar duas outras sessões sobre ela.** Vale registrar *como* ela voltou, porque
> a lição não é "lembre-se dela" — é onde ela entra.
>
> Um frame novo foi prototipado num sandbox, onde o corpo começava com uma **chamada de macro**
> (`\tabela{1.35}`), que começa com `\`. Ao migrar para o deck eu **inlinei** o grupo, e o corpo
> passou a começar com `{\small\renewcommand…`. O beamer leu o grupo como subtítulo e **as três
> primeiras linhas da tabela foram desenhadas dentro da faixa colorida do título**, em branco sobre
> verde. Zero erros, zero overfull, e o `pdftotext` extraía tudo — o texto **estava** no PDF.
>
> **A armadilha não mora no frame: mora na TRANSIÇÃO** — sandbox → deck, macro → inline, refatoração
> que troca o primeiro token do corpo. Um frame que estava certo passa a estar errado sem que o
> conteúdo mude. **Depois de qualquer edição que mexa no início do corpo de um frame, renderize
> aquele frame.** Nenhum outro instrumento vê.
>
> ⚠⚠ **E ela voltou uma TERCEIRA vez, no mesmo dia, causada pelo próprio conserto da segunda.** O
> frame do slide de resultado abria com `\vspace{0.5mm}` — que era o guarda. Numa varredura de
> espaçamento para fazer o slide caber, eu removi o `\vspace` **por parecer folga**, e a tabela
> inteira voltou para dentro da faixa do título.
>
> **A lição não é "lembre-se": é que um guarda que parece folga vai ser removido por alguém
> otimizando folga — inclusive por quem o pôs.** O guarda tem de se declarar:
>
> ```latex
> \begin{frame}{Título}
>     \vspace{0pt}% ⚠ GUARDA -- NAO REMOVER. Sem algo que nao seja "{" abrindo o corpo, o beamer
>     % le o grupo seguinte como SUBTITULO. Custa zero altura.
>     {\small ...
> ```
>
> **Duas formas de guarda, e a segunda é gratuita:**
> 1. `\vspace{0pt}` com o comentário `⚠ GUARDA` na mesma linha;
> 2. ⚠ **uma LINHA EM BRANCO depois do `\begin{frame}{título}`** — medido: ela encerra a varredura
>    de argumento opcional do beamer, e o grupo seguinte já não vira subtítulo. É o que protege o
>    slide *The null result*, que abre com `{\centering…` e **está correto**.
>
> **A varredura que encontra os dois casos:**
> ```python
> re.finditer(r'\\begin\{frame\}(\[[^\]]*\])?\{([^}]*)\}\s*\n((?:\s*%[^\n]*\n)*)\s*([^\s])', s)
> # sinaliza quando o grupo 4 e' "{" -- mas confira o render, porque linha em branco e' falso positivo
> ```

**Escolha do comando de overlay pelo que a tela precisa fazer:** `\onslide`/`\uncover` reservam o
espaço (nada se mexe) — é o certo para revelar em lugar. `\only` **não reserva espaço** e faz o
resto do slide pular; use só dentro de algo já dimensionado. Para trocar um bloco por outro,
`overlayarea` ou `overprint`, que têm tamanho fixo.

---

## 5.7 · `\specialframe` significa "fora do fio do argumento"

Estabelecido 26/08, quando o slide da pergunta saiu dele.

**`\specialframe` (fundo em degradê, sem faixa de título) marca a página que NÃO faz parte do fio
do argumento.** Duas famílias, e só essas:

| | páginas | |
|---|---|---|
| **transição** | *"Three possible causes do not close the investigation"* · *"With the architecture fixed, the input moved the result"* | fecham um capítulo e abrem o seguinte |
| **fecho** | `Closing` · `Obrigado` | as duas capas do fim |

⚠ **O slide da pergunta estava vestido de transição sendo a âncora da defesa inteira.** O contraste
que o degradê dava não compensava a mentira de gramática: quem conhece o deck lê `\specialframe`
como *"aqui não há o que anotar, é passagem"* — exatamente o oposto do que aquele slide pede.

**A pergunta a fazer diante de qualquer `\specialframe`:** *a banca precisa reter algo desta tela?*
Se sim, é conteúdo, e vai de frame comum com faixa de título.

## 5.8 · O fecho tem outro gênero: ali a plateia não lê, escuta

Formulação do autor, 26/08, e ela vale mais que qualquer limiar que a gente mediu:

> *"É gênero até, pq são os últimos slides e neles a plateia já não lê mais, só escuta — então é
> importante ser o mais didático e simples possível."*

**Nos últimos oito slides a tela deixa de informar e passa a marcar lugar.** Minuto 42 a 50, atenção
no mínimo, o autor falando de cabeça. **O mesmo slide que passa no minuto 12 não passa no 45.**

⚠ **NENHUMA métrica isolada separa os slides que o autor contestou dos que ele não contestou.**
Duas tentativas falharam, e o registro das duas importa mais que o princípio:

| régua tentada | por que falhou |
|---|---|
| **palavras na tela** | os 4 mais textuais do deck (40, 17, 24, 41) **não** foram citados; o 43, citado, tem exatamente a mediana |
| **palavras por unidade** | mediana do deck **14,7**; três dos quatro citados estão **na mediana ou abaixo** (45 = 14,7 · 42 = 13,7 · 43 = 5,7), e os seis mais pesados não foram citados |
| **objetos de leitura** | o 43 tem 21 contra mediana 4 — mas o **41 tem 37** e ninguém reclamou |

**O que sobrevive é qualitativo e é uma lente, não um alvo:**

> **Uma tela pode carregar 188 palavras se nenhuma unidade for uma frase.** O 41 tem 167 palavras
> em células de 3 e nunca incomodou. **O que cansa é a unidade que exige leitura de frase** — e no
> fecho, qualquer objeto que exija leitura é caro, enquanto um número que se varre não é.

⚠ **A lição de método por trás disso é maior que o assunto.** A primeira régua nasceu de uma amostra
de controle de **quatro slides escolhidos por quem queria a conclusão** — todos tabela de números.
Contra 3 palavras por célula, qualquer prosa parece fora da curva. **Cada medição estava certa; o
controle é que não era controle.** Antes de traçar uma linha, meça a população inteira.

## 6 · Slide de resultado — a lei própria

Merece seção porque é onde este deck concentra os dois defeitos. Dos doze slides mais falados, oito
são de resultado; dos dez mais densos de tela, sete são tabela; e a página que mais desce na tela é
a do veredito.

### 6.1 · O formato

> **Título curto · afirmação no subtítulo · UMA tabela ou UM gráfico ocupando 60–80% da tela ·
> nenhuma prosa ao lado · a ressalva na fala.**

É literalmente o que a referência faz (§3.2) e é o que a evidência sustenta.

### 6.2 · Tabela ou gráfico

| use tabela | use gráfico |
|---|---|
| a banca precisa **ler o valor exato** | a mensagem é **ordenação, distância, tendência** |
| as unidades diferem entre colunas | a comparação é "nós contra baselines" |
| menos de ~15–20 números | mais de ~20 células |

**O teste em uma linha:** se a sua frase de conclusão contém *"maior / menor / cresce / satura"*, é
gráfico. Se contém *"o valor é"*, é tabela.

⚠ **Isto é genuinamente contestado.** Meyer, Shinar & Leiser (1997) acharam **tabela mais rápida que
gráfico** em toda tarefa testada — mas com uma tabela de 3×5 cujos valores terminavam em 0 ou 5. O
que sobrevive da controvérsia é o critério acima, não uma preferência.

### 6.3 · Os limites, e eles são duros

| limite | valor | por quê |
|---|---|---|
| tamanho da tabela | **~5 linhas × 4 colunas (~20 células)** | acima disso ninguém lê em 30 s |
| corpo da tabela | **`\normalsize` ou `\small`**, nunca menos | §2. E é o piso de corpo que **força** o limite de 20 células |
| dígitos | **dois efetivos** — os dois que variam | `0,70`, não `0,7024` |
| destaque | **UMA célula, UM canal** | cor **ou** negrito **ou** caixa, não os três |
| altura do gráfico | **60–80% da altura útil** | abaixo de ~1/4 a codificação deixa de ser decodificável |
| legenda | **nenhuma** | rotule cada série na própria série. Zero consultas |
| ordem das linhas | **pela métrica**, nunca alfabética | dá âncora ao olho |

⚠ **"Negrito no melhor de cada coluna" numa tabela de doze linhas NÃO é sinalização** — é decoração
uniforme, e cai na parte plana da curva dose-resposta. A convenção negrito/sublinhado que o
`considerations.md` manda padronizar **funciona numa tabela de cinco linhas e falha numa de doze**.
Em tabela grande, o certo é acinzentar tudo menos a nossa linha e a do concorrente que importa, e
mandar a grade completa para a reserva.

⚠ **E o arredondamento tem um limite que vem de fora desta seção.** Um número na tela que não bate,
dígito a dígito, com a célula da tabela entregue é exatamente o descuido que faz um membro da banca
virar hipercrítico. **Arredondar é permitido; divergir não é.** Se o arredondamento fizer a
diferença sumir, isso é informação — diga, e reformule a afirmação — mas **não invente uma
precisão que a tabela entregue não imprime, nem apague uma que ela imprime.** A regra de
proveniência do `PLANO §8` regra 3 continua acima desta.

### 6.4 · Honestidade gráfica, e a banca vai olhar

- **Barra de F1 ou acurácia começa em zero.** Se com o zero a diferença some, **não trunque a
  barra**: troque a marca — ponto com intervalo, ou plote o **delta** com o zero marcado. Pôr um
  símbolo de eixo quebrado **não conserta** (medido: as pistas de quebra e o degradê não reduzem o
  viés de leitura).
- **Nunca um número de semente única.** Toda métrica de manchete carrega o **n** e a dispersão.
- **Diga o que a barra de erro significa**, na mesma redação em todo slide: *"média ± 1 dp sobre
  4 sementes × 5 partições (n=20)"*.
- ⚠ **Dispersão entre partições NÃO é intervalo de confiança.** As partições compartilham dados de
  treino, então a variância ingênua da validação cruzada **subestima** a real. Rotule como
  *"dispersão entre partições"*, e para afirmação inferencial use o teste pareado que o Cap. 5 já
  tem.
- ⚠ **E não deixe a banca ler sobreposição de intervalos como "sem diferença".** Dois IC de 95%
  sobre médias independentes que **apenas se tocam** correspondem a p ≈ 0,01. Se um arguidor começar
  a comparar sobreposição no olho, **corrija explicitamente**.
- **Codificação da comparação de manchete: posição numa escala comum.** Nunca ângulo, área,
  saturação ou 3D.
- **Muitas condições: múltiplos pequenos**, com eixos compartilhados e o mesmo layout em cada
  painel. **Não anime entre elas** — a animação ganha em atenção e **perde em acurácia**, e numa
  defesa a moeda é acurácia.

### 6.5 · Paralelismo entre slides de resultado

Quando o resultado ocupa vários slides, **reuse exatamente o mesmo layout, os mesmos limites de
eixo, a mesma atribuição de cor, a mesma ordem de linhas e a mesma gramática de título.** Mude
**só** a coisa em discussão. É barato — fixa-se uma vez numa macro — e é o que permite comparar de
um slide para o outro sem reaprender a tela.

### 6.6 · Revelação progressiva, quando vale

Três condições, e as três juntas: **no máximo 2–3 passos**; **todo passo acrescenta informação**
(uma linha nova, uma anotação), nunca só desacinzenta o que você vai ler; e **nada que já está na
tela se move um pixel** entre os passos. Mais que três passos: são slides separados.

Revelar a tabela de resultados em dois passos — primeiro a baseline, depois o nosso número — é
defensável e ajuda. Revelar cinco marcadores um a um é o uso que o próprio guia do beamer
desaconselha.

---

## 7 · As regras operacionais deste deck

Escritas para serem verificáveis. Cada uma passa ou reprova.

### 7.1 · Tela

| # | regra |
|---|---|
| T1 | **Piso de corpo `\normalsize`, alvo `\large` — mas SÓ depois do corte de conteúdo (§5.6b).** Hoje o deck não comporta: um degrau dobra o estouro. Até lá, `\small` e `\scriptsize` sobrevivem por necessidade, e cada slide tocado sobe o corpo **até onde couber**, verificado por render. `\tiny` em lugar nenhum |
| T2 | **Nenhum bloco de texto com mais de duas linhas**, título incluído |
| T3 | **Lista com 2 a 4 itens.** Cinco ou mais é sinal de que o slide tem duas ideias |
| T4 | **Um só nível de `itemize`.** O segundo nível cai para `\small` sozinho |
| T5 | **No máximo um `alertblock` por slide**, e só para ressalva que limita um resultado |
| T6 | **No máximo dois `\textbf` por bloco de texto.** Hoje são 706 em 103 frames, ~7 por tela |
| T7 | **Slide de resultado é tabela ou figura mais legenda.** Nunca prosa ao lado |
| T8 | **Todo rótulo em cima da coisa.** Sem legenda separada, sem "ver a nota" |
| T9 | **Nenhuma figura reduzida.** Regenere no tamanho final; todo traço ≥ 1,5 pt na tela |
| T10 | **Nada nos 5% externos da tela.** É seguro contra corte e contra colisão com o número da página |
| T11 | **Convenção de tabela idêntica em todo o deck:** negrito = melhor, sublinhado = segundo. ⚠ **Só funciona em tabela de até ~5 linhas** (§6.3) |
| T12 | **Nenhuma cor sozinha carrega significado.** Cor mais forma, ou cor mais rótulo direto |
| T13 | **A tinta do corpo para em ~0,85 da altura; acima de 0,93 é defeito.** Medido pela varredura de §8.1 |
| T15 | **Respiro entre elementos, tratamento B (§5.6c):** `itemsep 2ex` na lista, ~10 mm antes do bloco seguinte. `\vspace` positivo é a ferramenta; negativo continua proibido |
| T14 | **Layout idêntico entre slides de resultado consecutivos.** Muda só a coisa em discussão |

### 7.2 · Palavra

| # | regra |
|---|---|
| P1 | **Nenhuma frase da tela é uma frase da fala.** Se coincidirem palavra a palavra, uma das duas sai — normalmente a da tela |
| P2 | **O que fica na tela é paráfrase mais curta**, ~metade das palavras da fala, redação diferente. Nem idêntica, nem ausente |
| P3 | **Ressalva, justificativa e explicação vão para a fala.** Protocolo obrigatório: localize a cláusula no destino com `grep`; se não existir lá, **ela não sai** — escreva-a na fala primeiro; registre no bloco do `SLIDES.md` onde ficou |
| P4 | **Afirmação, número de veredito e definição ficam na tela.** Número impresso é lembrado; número só falado, não |
| P5 | **Título curto e literal.** Sem analogia, sem trocadilho, sem frase. A afirmação vai no `\framesubtitle` |
| P6 | **Um nome por conceito, idêntico ao da dissertação.** [`../GLOSSARY.md`](../GLOSSARY.md) é fail-closed |
| P7 | **Travessão por função:** fica como separador de rótulo, título de bloco e subtítulo de frame; sai de dentro de frase completa. ⚠ Classifique por função **antes** de substituir |
| P8 | **Todo número copiado de célula de tabela entregue.** Nunca re-derivado |

### 7.3 · Relógio

| # | regra |
|---|---|
| R1 | **Alvo 38–42 min**, não os 50 do teto |
| R2 | **~48 s por slide** é a referência medida. 54 slides ≈ 43 min |
| R3 | **~6.050 palavras de fala** é o orçamento a 140 ppm. Hoje: 8.837 |
| R4 | **Nenhum slide passa de ~110 palavras de fala** sem justificativa registrada. Hoje a mediana é 158 |
| R5 | **Ensaio cronometrado com marca no fim de CADA seção.** Com o total sozinho descobre-se que estourou e não de onde cortar |
| R6 | **Duas saídas de emergência marcadas** — blocos de 3 a 5 slides que podem cair ao vivo — e o ensaio feito também na versão sem eles |
| R7 | **Um ponto de reentrada a cada ~5 min:** um divisor, uma pergunta repetida, uma recapitulação de uma linha |

---

## 8 · O protocolo de verificação

Nesta ordem, e nenhum passo substitui o seguinte.

```bash
cd articles/dissertacao/presentation

# 1 · edite o SLIDES.md PRIMEIRO, depois propague para slides/main.tex
# 2 · build -- xelatex, tres passes; NUNCA pdflatex
cd slides && source ../../src_utils/texenv.sh && make all

# 3 · canaria: o ultimo elemento visivel de cada frame tocado aparece no PDF?
pdftotext main.pdf -            # SEM -layout

# 4 · varredura de tinta: ate onde o conteudo desce, pagina a pagina (§8.1)
python3 ink_sweep.py slides/main.pdf 72

# 5 · OLHE, no tamanho real do Meet
pdftoppm -f <p> -l <p> -png -scale-to-x 1230 -scale-to-y -1 main.pdf /tmp/s

# 6 · se a fala mudou, regenere o SPEECH -- e so DEPOIS de reconstruir o deck
python3 build_speech_1_extract.py && python3 build_speech_2_emit.py
make -f Makefile.speech

# 7 · sincronize SLIDES.md <-> main.tex antes de commitar
```

**O que cada passo responde, e o que ele NÃO responde:**

| passo | responde | **não** responde |
|---|---|---|
| `make all` | compila? | se o conteúdo saiu da página; se dois blocos se sobrepõem |
| canária | o texto está no PDF? | se está **onde eu mandei**; se o bloco **fecha** |
| varredura de tinta | o conteúdo desce até onde não devia? | se o que está lá faz sentido |
| render a 1230 px | o slide funciona? | se o número bate com a tabela entregue |
| leitura contra a fonte | o número está certo? | — |

### 8.1 · A varredura de tinta — o instrumento que faltava

O log não vê colisão, e a canária não vê posição. **A varredura de tinta vê as duas.** Renderize
cada página em cinza a 72 dpi, apague a caixa do número do frame e a faixa do título, e meça **até
que fração da altura a tinta do corpo desce**. Página de fundo cheio (capa, `\tocframe`,
`\specialframe`) é detectada pela luminância do miolo e sai da conta — sem isso a taxa de falso
positivo é 100%.

**A calibragem, feita contra o próprio template:**

| | mediana | p90 | acima de 0,90 |
|---|---:|---:|---:|
| **deck da defesa** (100 páginas de conteúdo) | **0,912** | 0,945 | **60 de 100** |
| **demo do `nesped_slides_template/`**, do autor do template (13 páginas de conteúdo) | **0,750** | 0,907 | **2 de 13** |

> **O alvo: a tinta do corpo para em ~0,85. Acima de 0,93 é defeito.**

**As páginas que mais descem hoje** (72 dpi): p53 **0,996** — o veredito, e é o slide mais
importante do deck · p65 0,977 · p75 0,965 · p108 0,953 · p26 / p76 / p83 / p105 0,949.
**Dezoito páginas passam de 0,93 e quarenta e cinco põem conteúdo dentro da faixa do rodapé**, que
o template deixa vazia por desenho.

⚠ **Uma correção de medida, e ela importa como método.** Um relatório anterior descreveu a página 53
como *"colide com o número da página"*. **Medi, e a colisão literal não se confirma:** a 150 dpi, a
tinta do corpo naquela faixa vai até x=0,883 e o número do frame começa em x=0,978 — não há
sobreposição de glifo. O que **é** verdade, e continua sendo defeito, é que a última linha desce a
0,996 e fica no mesmo nível do número, sem margem inferior nenhuma. **Nenhuma página do deck colide
de fato.** A distinção é do próprio script (`invade` × `COLIDE`), e existe porque as duas pedem
correções diferentes.

O script está em `ink_sweep.py`, ao lado deste documento. Ele leva alguns segundos para as 111
páginas e não depende de nada além de poppler, Pillow e numpy.

⚠ **Uma página de fundo cheio legitimamente pinta até 1,0.** Se a detecção por luminância errar num
caso novo, ponha o número da página numa lista de exceção **explícita** — não afrouxe o limiar.

**As quatro sub-armadilhas da canária, todas já pagas:**

1. `pdftotext` **sem** `-layout`. Com ele as colunas se intercalam e a busca falha em conteúdo que
   **está** na tela.
2. A sonda tem de ser **conjunto de palavras** (≥5 letras, exigir ≥66% presentes), nunca frase
   contígua — uma quebra de linha derruba qualquer busca por frase, e não é ponto cego só de tabela.
3. Apague `\begin{…}` / `\end{…}` **com nome e argumentos** antes de extrair as sondas, senão nomes
   de ambiente viram "texto" (215 falsos positivos numa tentativa, 62 de 101 noutra).
4. **Rederive as sondas do `.tex` a cada corrida.** Sonda guardada caduca com a edição.

⚠⚠ **O caso 9, e é o mais barato de repetir: verificar a PÁGINA ERRADA.**

Em 2026-08-26 eu reescrevi o slide impresso 44 e reportei **✔ 0,906** pela varredura de tinta. **O
número era da página 52; o slide 44 é a página 51.** O que estava fora da página era a terceira das
três condições da conclusão — a que o próprio `gate` tinha avisado para não perder. `Overfull` de
**24,4 pt**, log lido, canária não rodada naquele frame, e **eu declarei o slide verificado**.

**A causa não foi o instrumento: foi a âncora.** O número impresso e o índice de página do PDF
**divergem e o deslocamento muda** (capa, `\tocframe`, `\specialframe` e overlays não numerados).
Eu tinha o mapa medido e mesmo assim usei índices lembrados de uma medição anterior.

> **A regra: verifique SEMPRE ancorado no número impresso lido do PDF na mesma corrida, nunca num
> índice de página guardado.** O mapa envelhece a cada frame removido, e um índice de ontem aponta
> para outro slide hoje — silenciosamente, porque o slide errado também existe e também tem um
> número plausível.

⚠⚠ **O caso 10: um `grep` de duas palavras não atravessa a quebra de linha da FONTE.**

Reportei que o termo fora de registro `fine class` tinha **zero ocorrências**. Tinha uma, e ela
aparecia na tela. O `.tex` quebra a linha **entre as duas palavras** (`fine\n class}`), e
`grep 'fine class'` não casa. **É a sub-armadilha 2 da canária — sonda por frase não sobrevive a
quebra de linha — aplicada a uma varredura de estilo, onde ninguém espera por ela.**

> **A regra: auditoria de termo roda sobre o PDF EXTRAÍDO e com os espaços normalizados**, não
> sobre a fonte. É onde o termo de facto aparece para a banca, e não tem quebras de linha do `.tex`:
>
> ```bash
> pdftotext main.pdf - | tr '\n' ' ' | grep -o '.\{45\}<termo>.\{45\}'
> ```
>
> O contexto de 45 caracteres de cada lado é o que permite julgar **função** em vez de presença — que
> é a regra do travessão aplicada a qualquer termo restrito.

**E a mesma varredura, rodada de novo com contexto, achou o que a busca por presença tinha perdido.**
Procurando `venue` (banido pelo `GLOSSARY.md:84` como sinónimo de *place*), o PDF devolveu **três**
ocorrências, não a única que eu tinha consertado:

| ocorrência | veredito |
|---|---|
| `the **venue-type feature** maps one-to-one…` (×2) | ✅ **licenciada** — é verbatim de `4_courb.tex:42` e `venue` ali nomeia **uma coluna de dados**, não um lugar |
| `the literature also calls it next-POI, next-location or **next-venue**` | ⚠ `venue` **como sinónimo de lugar**, que é o sentido banido |

> **A lição: um termo banido não é banido em todo contexto, e a varredura tem de mostrar o
> contexto para que alguém julgue.** Uma contagem devolve "3" e não diz que duas são legítimas; o
> `grep -o` com janela devolve as três frases e a decisão fica possível.

**E a regra de decisão, quando o contexto não resolve sozinho:**

> **Quando um termo está numa lista fail-closed e a defesa dele depende de uma distinção sutil, o
> termo sai** — não porque a distinção esteja errada, mas porque explicá-la ao vivo custa mais do
> que ela vale. Numa arguição, quem gasta fôlego defendendo uma palavra decorativa perde o fio do
> argumento.
>
> **O inverso também vale:** um termo restrito **fica** quando é verbatim do texto entregue, nomeia
> uma coisa específica, e **carrega peso** no argumento. Foi o critério que separou `next-venue`
> (saiu) de `venue-type feature` (ficou) na mesma varredura.

⚠⚠ **E a fronteira entre os dois instrumentos, que é o que impede o padrão novo de ganhar falsa
confiança:**

> **Extrair o PDF pega termo ERRADO; só renderizar pega conteúdo AUSENTE.**
> **Os dois são necessários e nenhum substitui o outro.**

A extração encontrou os dois termos fora de registro — os dois estavam **corretos na tela**, só eram
a palavra errada. **Ela não teria encontrado a condição `Scale` do caso 9**, porque o que não é
desenhado também não é extraído. E o render sozinho não teria encontrado os termos.

**Duas medições que precisam do contador certo:**

- **Fala:** conte **tokens separados por espaço**, sem filtro de tamanho. Um `{2,}` derruba `é`,
  `e`, `o`, `a`, `há` — em português isso é viés de 15–20%, não higiene.
- **Tela:** remova as linhas de comentário **do arquivo** antes de contar, não da saída. O
  `main.tex` carrega blocos `% FALA:` inteiros em português.

⚠ **E um terceiro caso, pago em 2026-08-26, contra o meu próprio instrumento.** Medi a deriva entre
o `SLIDES.md` e o `main.tex` varrendo o bloco de comentário **inteiro** a partir de `% FALA:` até a
próxima linha não-comentada, e reportei **seis blocos com deriva**, um deles de 444 palavras. Estava
errado: o `% FALA:` do `.tex` **não é espelho da fala** — é cópia de conveniência, e vários frames
carregam **notas de projeto anexadas ao mesmo bloco**. A deriva real, medida por par, é **menor que
15 palavras onde há par**. Mesma assinatura dos outros seis casos do `HANDOFF.md` §3: o instrumento
reportou defeito porque mediu outra coisa. **Para medir sincronia, compare texto de TELA
(`Na tela` × corpo do frame), não fala.**

⚠ **E a lição que vale mais que os dois números:** um relatório errado deste projeto vinha com
*"três medições independentes concordam em 1%"* — **as três partilhavam o mesmo contador**.
Concordância só é evidência quando os métodos **não partilham o passo suspeito**.

---

## 9 · Decisões do autor, e o que continua aberto

### 9.1 · Fechadas em 2026-08-26 — não reabrir

| decisão | onde ela morde |
|---|---|
| **A implementação é da sessão `ppt`**; o conteúdo é do `gate`; a `presentation` para de escrever e vira consulta | uma mão só no `main.tex` |
| **Conteúdo centrado na vertical.** `[t]` recusado depois de ver o render | §5.6b |
| **`12pt` recusado.** O corpo só sobe depois do corte de conteúdo | §5.6b — e o experimento diz por quê |
| **Respiro INTERNO é a alavanca**, com os blocos mais para o rodapé | §5.6c, tratamento B |
| **Título curto e literal; a afirmação vai no `\framesubtitle`** | §4.5, Tensão 1 — resolvida |
| **O S6 sai; a regra 13 do `PLANO §8` fica REVOGADA.** A contribuição aparece uma vez, no S50 | arrasta o `[BLOCO-CONTRIBUIÇÃO]` (três cópias com teste de sincronia) e a ressalva *operational, not computational* |
| **O S3 perde a tabela de resultados.** Fica a pergunta + a restrição de modelo único | arrasta a fala que promete a resposta no minuto três, o `INTRODUZ` do veredito (1.3 → S46) e a restrição, que migra do S4 para o S3 |
| **Travessão: a regra por função continua valendo.** Sai o de texto corrido, fica o de glosa | verificação caso a caso, **nunca varredura** |
| **O relógio fica para depois desta rodada** | a medição fica registrada; nenhum item bloqueado por tempo |

### 9.2 · O que este documento continua não decidindo

- **O que entra em cada slide.** É do autor, informado pelo `gate`.
- **Se o deck fecha na conclusão ou nos agradecimentos.** §4.3 recomenda dizer o agradecimento e
  voltar para a conclusão, deixando **ela** projetada na arguição. Do autor.
- **Se o slide 28 e o 18 saem.** Do autor, e o 28 ainda passa pelo orientador.
- **Se os 48 slides da série B devem entrar no `SPEECH.pdf`.** Eles são descartados em silêncio
  hoje: os blocos usam prefixo `SB<n>` e o regex do extrator é `\n### (S\d+) · `, e o `B` não é
  dígito. Pode ser deliberado — a série B é lida, não falada — mas se a intenção é pular para um
  slide B na arguição com a fala impressa na mão, hoje não dá. **É uma linha de regex.** Do autor.
- **Qualquer número, qualquer afirmação científica.** Do `gate`, contra o texto entregue.

---

## Fontes

**Regulamentares.** Regimento interno PPGCC-UFV, Art. 22 e 23 (`https://ppgcc.ufv.br/regimento-interno/`);
Regimento de Pós-Graduação UFV, Art. 67 e 70; consolidado em [`../UFV_COMPLIANCE.md`](../UFV_COMPLIANCE.md) §3.

**Estudos controlados.** Garner & Alley 2013, *Int. J. Engineering Education* 29(6):1564–1579
(afirmação-evidência, N=110) · Alley, Schreiber, Ramsdell & Muffo 2006, *Technical Communication*
53(2):225–234 · Yue, Bjork & Bjork 2013, *J. Educational Psychology* 105(2):266–277 (redundância,
N=105) · Mayer & Fiorella, *Cambridge Handbook of Multimedia Learning* 2ª ed., caps. 12–13 ·
Adesope & Nesbit 2012 (meta-análise, 57 estudos) · Schneider, Beege, Nebel & Rey 2018,
*Educational Research Review* 23:1–24 (sinalização, 103 estudos, N=12.201) · Ginns 2006
(contiguidade, meta-análise) · Rey 2012 (detalhes sedutores, meta-análise) · Bullock, Colón Amill,
Shulman & Dixon 2019, *Public Understanding of Science* 28(7):845–853 (jargão, N=650) ·
Buchner & Baumgartner 2007, *Ergonomics* · Piepenbrock, Mayr & Buchner 2014, *Human Factors* ·
Arditi & Cho 2005, *Vision Research* (serifa) · Harrower & Brewer 2003, *Cartographic Journal*
(ColorBrewer, testado em projetor).

**Normas.** ANSI/AVIXA V202.01 "DISCAS" (dimensionamento de imagem; reconstruída do material de
treinamento CTS da própria AVIXA, que traz as fórmulas e a crítica ao 4/6/8) · ANSI/INFOCOMM 3M-2011
"PISCR" (contraste de sistema: 7:1 passivo, 15:1 decisão básica, 50:1 analítico) ·
ISO 9241-303 (altura de caractere ≥16 min de arco; largura de traço 1/12 a 1/6 da altura) ·
WCAG 2.2 §1.4.3, §1.4.6, §1.4.11 · Okabe & Ito, *Color Universal Design*.

**Cânone de prática.** Alley & Neeley 2005 (Tabela 1) · Doumont, *Trees, Maps and Theorems* ·
Peyton Jones, *How to give a great research talk* · Duarte, *slide:ology* · Reynolds,
*Presentation Zen* · Naegle, *Ten Simple Rules for Effective Presentation Slides* ·
Paradi 2013 (pesquisa de irritação, N=682).

**Apresentação de dados.** Cleveland & McGill 1984 (ranking de codificação gráfica) · Heer &
Bostock 2010 (replicação em multidão; ⚠ **não** reproduziu a previsão de que ângulo é pior que
comprimento) · Correll, Bertini & Franconeri 2020 (eixo truncado: a quebra de eixo e o degradê
**não** corrigem o viés) · Correll & Gleicher 2014 (o viés "dentro da barra") · Robertson et al.
2008 (múltiplos pequenos batem animação em acurácia, p<0,001) · Meyer, Shinar & Leiser 1997
(tabela × gráfico; ⚠ contestado) · Bateman et al. 2010 (enfeite e memória; n=20, confundido com
novidade) · Cumming (leitura de sobreposição de IC) · Reimers & Gurevych 2017 e Bouthillier et al.
2021 (variância por semente) · Ehrenberg (dois dígitos significativos) · Kosslyn et al. 2012
(violações medidas em decks reais).

**Mecânica do beamer.** Guia oficial do beamer (`beameruserguide`): 20–40 palavras por frame com
teto de 80; no máximo um frame por minuto; semântica de `\only` / `\uncover` / `\visible` /
`overlayarea` / `overprint`; *"não descubra listas em pedaços"*.

**Medições feitas para este documento.** Gravação duma defesa anterior do mesmo programa
(`presentation/exemples/…mov`, 41 quadros amostrados, folhas de contato, leitura dos números
impressos) · specimen do `nesped.sty` compilado e renderizado, exercitando cada componente ·
contraste WCAG calculado sobre as onze cores do `.sty` · varredura de tinta sobre as 111 páginas do
deck **e** sobre as 23 do demo do template, para calibrar o alvo (`ink_sweep.py`, ao lado deste
arquivo) · contagem de macros, de palavras de tela e de palavras de fala sobre o `main.tex` e o
`SLIDES.md`, com os comentários filtrados **no arquivo** · deriva `SLIDES.md` ↔ `main.tex` por
casamento de título e diff de sequência.

⚠ **Duas normas ANSI são pagas e não pude ler o texto original** (V202.01 e 3M-2011); os valores
vêm do material de treinamento da própria AVIXA e de imprensa técnica, e cruzam numericamente entre
si. Os valores da ISO 9241-303 vêm de resumos secundários concordantes. **Se algum deles for citado
normativamente na arguição, marque como secundário.**
