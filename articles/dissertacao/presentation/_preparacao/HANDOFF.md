# HANDOFF.md — o que um agente novo precisa saber para continuar

> **Escrito 2026-08-24**, manhã do dia do primeiro ensaio. **Defesa: sexta, 28/08, 10:00, remota
> (Google Meet).** Banca: Fabrício A. Silva (orientador/presidente), Clayson S. F. de Sousa Celes
> (ITA, externo), Alex Borges.
>
> **Quem aprova é o autor.** Não existe portão com o orientador para a apresentação — foi decisão
> dele, registrada. Não reintroduza.
>
> **Este documento é orientação, não lei.** A lei da estrutura é o `PLANO_FLUXO_DEFESA.md`; a lei
> da palavra são os três arquivos em `../` (`WRITING_LAW.md`, `GLOSSARY.md`, `AGENT_GUARDRAILS.md`).
> Onde este arquivo divergir deles, eles vencem.

---

## 1 · Leia nesta ordem

| # | Arquivo | O que é |
|---|---|---|
| 1 | `../CLAUDE.md` **§0** | **De onde vem cada número.** Se você escrever um número sem ler isto, vai errar — foi o erro mais repetido do projeto |
| 2 | `PLANO_FLUXO_DEFESA.md` | A lei da estrutura: arco, seis seções, minutos, ledger de de-duplicação, e **16 regras em §8** que o deck obedece |
| 3 | `SLIDES.md` | O slide-a-slide: tela (inglês), fala (português), proveniência por número, proibições |
| 4 | `APRESENTACAO_DEFESA_GUIDE.md` | Logística, Art. 23, e a análise quadro a quadro de uma defesa real do mesmo programa |
| 5 | `../wrapup/open_points/ARGUICAO.md` | 23 perguntas de banca + 8 "não foi medido", com resposta preparada |

---

## 2 · Estado, em 24/08

| Artefato | Estado |
|---|---|
| `PLANO_FLUXO_DEFESA.md` | **Fechado e aprovado.** 48 min, seis seções, somas conferidas nos dois níveis |
| `SLIDES.md` | **Completo.** 54 slides de deck + 46 de reserva. Passou por 5 personas revisoras |
| `slides/main.tex` + `main.pdf` | **Compila: 111 páginas, 0 erros.** É o deck vivo — **e é o único**; o `slides_ux/` foi descartado pelo autor. ⚠ **Overfull não é mais zero, e isso é intencional** — ver §4 |
| `../src/banca.pdf` | **Congelado** — o que a banca recebeu. md5 `5be69d1b`, 119 pp. **Nunca reconstruir** |
| `../src/dissertacao.pdf` | O build corrente, **com a errata do Resumo aplicada**. md5 `d7e85bb7` |
| Ensaio nº 1 | **Hoje**, com amigos |

### O que NÃO está feito

- ~~Varredura visual das 110 páginas~~ — **FEITA 2026-08-24.** 80 achados, e a causa era em boa
  parte **uma só**: um bug do template. Ver §4.
- ~~A grafia de "Pedro Maia"~~ — **RESOLVIDO 2026-08-24 pelo autor: Pedro Augusto Maia Silva.**
  Está no slide de agradecimentos (S55). Era a única fonte possível: o nome não aparece em nenhum
  artigo, no texto entregue, nem em lugar nenhum do repositório.

---

## 3 · A armadilha central deste projeto

> **Um instrumento dizer "limpo" não é evidência de que está limpo.** Isto aconteceu **cinco vezes**
> nesta sequência, sempre com o mesmo formato: uma checagem passou porque media outra coisa.

| # | O instrumento disse | A verdade era |
|---|---|---|
| 1 | `make check` saía **0** e os commits diziam "gates verdes" | Saía **2**. O 0 era do shell; o `make` retornava erro. **Leia o código de saída, não a saída** |
| 2 | Busca pela frase do Resumo no build `academico`: **0 ocorrências** | Aquele build **começa na página 10** e não contém o Resumo. Zero do instrumento, não do texto |
| 3 | Avisos "No current point" do poppler apareciam **também no PDF oficial** → "ruído benigno" | Eram o sintoma de um bug real. **Uma referência que compartilha o defeito não é controle** |
| 4 | `pdflatex` compilou o deck: **42 páginas, 0 erros**, texto extraível completo | Capa e todos os divisores saíam **em branco** — texto branco sobre gradiente que não desenhou. **Um teste de texto teria aprovado** |
| 5 | `make all` no deck: **0 erros, 0 overfull** | A legenda **sobrepunha** a tabela do veredito. Colisão não gera aviso |
| 6 | `make all`: **0 erros, 0 overfull**, e o `pdftotext` extraía tudo | Conteúdo empurrado para **fora da caixa do frame** não é desenhado — e o que não é desenhado **também não é extraído**. A ressalva que a R13 obriga sumiu da página em **dois builds seguidos**, sem uma linha de aviso. Diferente do caso 5: lá o conteúdo é desenhado **por cima** e renderizar revela; aqui ele **não existe**, e só uma busca pela string revela |

> **O detector do caso 6, e é barato — uma canária por frame.** Pegue o **último elemento visível**
> de cada frame (é o que cai quando estoura) e exija que ele apareça no texto extraído do PDF.
> ⚠ **Duas sub-armadilhas, ambas já pagas, uma por cada agente:**
> 1. Use `pdftotext` **SEM `-layout`**. Com ele as duas colunas de um slide se intercalam linha a
>    linha e o número da página entra no meio da frase do rodapé — então a busca falha em conteúdo
>    que **está** na tela. (Dois falsos positivos aqui.)
> 2. **A sonda tem de ser CONJUNTO DE PALAVRAS, não frase contígua.** `pdftotext` quebra
>    **célula de tabela** em várias linhas, então nenhuma frase de uma célula sobrevive inteira —
>    uma canária por frase **reprova toda tabela do deck**. Compare o conjunto de palavras
>    distintivas (≥6 letras) do último elemento e exija ≥66% presentes: imune a quebra de linha e
>    a ordem. Custo de não fazer: um alarme falso no ladder, cuja frase *"replaces two dedicated
>    single-task models on both tasks"* está no PDF, quebrada em três linhas.
>    ⚠ **E não é um ponto cego só de tabela.** A mesma sonda por frase reprovou
>    *"suggested, not isolated"* num **bullet de prosa comum**, porque o PDF quebrou a linha
>    no meio — em conteúdo que estava correto e visível no render. Sonda por frase não
>    funciona em lugar nenhum deste deck.
> 3. Apague `\begin{...}` / `\end{...}` **com o nome e os argumentos** antes de extrair as sondas.
>    Senão os nomes de ambiente viram "texto" e a canária dispara em tudo — **215 falsos positivos**
>    numa tentativa, **62 de 101** noutra, independentes, pela mesma causa.
>
> 4. **A sonda envelhece com a edição.** Uma canária guardada numa lista caduca: se o slide for
>    reescrito, a sonda passa a procurar palavras que já não estão lá e reprova conteúdo
>    correto. **Rederive as sondas do `.tex` a cada corrida; nunca as leia de uma lista
>    guardada.** Custo já pago: uma sonda procurando `computed` e `datasets`, duas palavras
>    que a reescrita da véspera tinha removido do próprio slide que ela vigiava.
>
> **Um checador ruidoso é pior que nenhum: treina a ignorá-lo.** As duas tentativas genéricas foram
> descartadas; a canária é o que sobreviveu. Rodada sobre os 101 frames por dois agentes em separado:
> **zero conteúdo caído.**

> ### Caso 7 — o contador de palavras, e por que três medições concordaram estando erradas
>
> **O orçamento de tempo do deck depende de contar palavras da trilha `% FALA:`.** Dois contadores
> diferentes, escritos por dois agentes, subestimaram-no em 16-19% — e por causas **diferentes**:
>
> | contador | 1 bloco | deck | viés |
> |---|---:|---:|---:|
> | `split()` por espaço — **o correto para taxa de fala** | 127 | **8.840** | — |
> | `[A-Za-zÀ-ÿ0-9]{2,}` | 106 | 7.416 | 16,1% |
> | `\b[A-Za-z]+\b` (ASCII) | 103 | 7.196 | 18,6% |
>
> **A causa medida do primeiro é o `{2,}`, não o acento.** A classe `À-ÿ` cobre os acentuados;
> `análise` casa sem problema. O que cai são as palavras de **uma letra** — e em português `é`,
> `e`, `o`, `a`, `à`, `há` estão entre as mais frequentes da língua, **e todas são ditas em voz
> alta**. Num idioma latino, um mínimo de comprimento num contador de palavras não é higiene: é um
> viés de 15-20%.
>
> ⚠ **A segunda causa é diferente e dá quase o mesmo total** (o regex ASCII mata acentuado em vez
> de palavra curta). Foi essa coincidência que fez uma atribuição de causa errada parecer
> confirmada. **Registre a causa MEDIDA, não a suposta** — dois defeitos distintos podem produzir
> o mesmo número.
>
> **E a lição que vale mais que o número:** o relatório errado vinha com *"três medições
> independentes concordam em 1%"*. **As três partilhavam o mesmo contador.** Três instrumentos que
> herdam o mesmo defeito não são três medições — são uma, repetida. Concordância entre métodos só
> é evidência quando os métodos **não partilham o passo suspeito**.
>
> **Para taxa de fala, conte tokens separados por espaço.** Qualquer filtro subestima, e subestima
> *uniformemente*, que é o que torna o erro difícil de ver: o total parece plausível e a razão
> entre seções fica intacta.

**A regra que decorre:** para qualquer coisa visual, **valide por renderização**. Para qualquer
coisa contada, valide **sobre o artefato final**, não sobre o relatório de quem o produziu (foi
assim que um slide duplicado passou pela minha conferência de ledger — eu contei os arrays que os
redatores devolveram, não o arquivo montado).

---

## 4 · A varredura visual — feita, e o que ela ensinou

**Rodada em 2026-08-24 sobre as 110 páginas renderizadas: 80 achados** (4 bloqueantes, 46 maiores,
30 menores). O tipo dominante era *sem espaço de respiro* (32), seguido de inconsistência (22),
ilegível (13) e sobreposição (10).

**A maior parte da sobreposição tinha uma causa única, no template:** `\beamerboxesframed` fixava
`width=\textwidth`. Dentro de uma `column`, `\textwidth` continua sendo a largura do **frame
inteiro** — então todo bloco em duas colunas era desenhado mais largo que a sua coluna e passava por
baixo do bloco vizinho, que o cobria. Uma linha (`\linewidth`) matou a classe inteira.

**São QUATRO os bugs corrigidos só na nossa cópia do template** (eram cinco; o quinto foi
**revertido pelo autor** — ver o aviso abaixo), todos com errata no próprio
`.sty`: `\pagewidth`→`\paperwidth`; o `\autotocframe` que vazava o argumento; o `\decorationnet`
que nunca desenhava; e o `width=\textwidth` acima.

> ⚠ **O quinto foi REVERTIDO em 2026-08-24, por decisão do autor.** Um agente trocou o
> `\vskip-2mm` do `\titleframe` por `\vskip3mm`, por julgar que o valor original cortava o topo
> dos cartões de logo da capa. **O autor conferiu contra o template do NESPeD e decidiu que os
> cartões DEVEM ficar colados ao topo da página** — é o desenho do template, não um defeito, e o
> PDF de referência do próprio autor do template sai assim. Valor original restaurado; a errata no
> `.sty` registra a reversão e o motivo. **Lição: nem toda diferença em relação ao original é bug.
> Antes de "corrigir" o template, compare com o PDF de referência dele** (`nesped_slides_template/`)
> e, se a diferença for de desenho e não de renderização quebrada, é decisão do autor, não do agente.

> ⚠ **`Overfull` deixou de ser zero de propósito — não "conserte" isso empurrando de volta.**
> O deck tinha 0 overfull porque os redatores usavam **31 `\vspace` negativos**. Eles não criavam
> espaço: puxavam o conteúdo para cima do elemento anterior. O log ficava limpo e a tela ficava
> sobreposta. Removidos, o LaTeX passou a declarar a verdade. Os estouros que restam foram
> **verificados por renderização** e ficam dentro da folga do beamer. **Se você reintroduzir
> `\vspace` negativo para zerar o log, você recria exatamente o defeito que esta varredura corrigiu.**

**A regra que decorre, e que vale para a próxima:** o log de compilação **não vê** colisão de blocos,
e um log limpo pode ser sintoma de cramming, não de saúde. Valide por renderização:

```bash
cd slides && pdftoppm -r 95 -png main.pdf /tmp/deck   # e olhar página a página
```

## 4b · A referência de densidade: a defesa do a defesa de referência

**É uma GRAVAÇÃO, não um PDF** — e o caminho já estava no `APRESENTACAO_DEFESA_GUIDE.md:131,:317`.
Eu procurei um PDF, não achei, e escrevi "não está no repositório" **sem reler o meu próprio guia**.
Falha nº 2 do §3, outra vez. O arquivo:

```
/Volumes/linux/VIDEO/Screen Recording 2026-07-08 at 10.02.56.mov     # 7 GB, 1h01, 4096×2304
```

É a **sua tela** durante a defesa, então o Meet só está em foco parte do tempo (≈0–15 min e
≈35–60 min). Extraia com `ffmpeg -ss <seg> -i <arq> -frames:v 1` (o `-ss` ANTES do `-i` = seek por
keyframe, barato num arquivo de 7 GB).

> ⚠ A gravação que sustenta esta medição foi apagada em 28/08/2026, por decisão do autor
> (conteúdo pessoal de terceiro, cópia única). O método e os valores ficam; a evidência
> primária não é reverificável.

**Ele usa o MESMO template NESPeD**, também é coletânea, também seis seções na barra. **64 slides em
≈48 min** — praticamente o nosso ritmo (54 em 48). O que difere não é a quantidade de slides:

| | a defesa de referência | nosso deck |
|---|---|---|
| palavras na tela, mediana | **~25–30** | **119** |
| máximo | ~70 | **237** |
| slides com frase completa | poucos | **54 de 54** |

⚠ **As duas medidas não são diretamente comparáveis, e o erro faz cortar demais.** A contagem do
nosso deck lê o corpo do LaTeX e **não vê texto dentro de figura**; OCR sobre o vídeo **vê**. O slide
"só uma figura" dele dá 82 no OCR e ~9 de corpo. Compare corpo com corpo.

**E a contagem sozinha engana.** O slide mais denso dele tem ~70 palavras — é *uma pergunta de
pesquisa num bloco*, que a plateia lê de uma vez. O nosso de 237 são *quatro marcadores de ressalva*,
que a plateia lê quatro vezes e perde a fala. Mesma contagem, funções opostas. **Corte pela função,
não pelo número.**

> 🔴 **O deck viola a regra 10 do PLANO em 54 dos 54 slides.** A regra diz *"Marcadores por
> palavra-chave, **nunca parágrafos**"*. Medido: todo slide do deck tem ao menos uma frase completa
> longa na tela. Quem for enxugar **não está sobrepondo o plano — está aplicando uma regra que ele já
> continha**. Não é preciso licença para cortar; o mandato existe. Mas ver §4c antes.

## 4c · O que NÃO pode sair da tela, e o protocolo para o que pode

Do `PLANO_FLUXO_DEFESA.md` §8, classificado. **Mandato de tela** (cortar é regressão): **R1**
navegação/seis `\section` · **R5** carimbo `Next-POI Prediction = next category (Def. 2.7)` em arte
dos Caps. 3/4 · **R8** rodapé `pós-submissão` em todo slide da série B · **R10** numeração dos slides
· **R12** slides de transição, que o plano proíbe explicitamente que um corte de tempo remova ·
**R13** a contribuição duas vezes, **com redação idêntica** · **R14** "Apêndice B" sempre com o nome
do volume.

**Governam a palavra, não o volume** (comprimir é seguro): R2, R3, R7, R9, R11, R15. **R16 e R10
mandam cortar** — são aliados. **R4** (ledger) vive no `SLIDES.md`, **não na tela**.

**A armadilha é a R6**, *"ressalva antes da manchete, sempre"*. Foi ela que produziu os 119: os
redatores puseram a ressalva **na tela** porque a R6 exige que ela acompanhe o resultado. A leitura
que o S47 testou: a R6 exige que a ressalva **acompanhe**, não que esteja **projetada** — se a
manchete está na tela e a ressalva é dita no mesmo fôlego, está satisfeita. **Mas só com este
protocolo, e ele não é opcional:**

> Para cada cláusula que sai da tela: **(1)** localize-a no destino (a fala do MESMO slide, ou um
> slide de reserva) com grep; **(2)** se não existir no destino, **ela não sai** — escreva-a na fala
> primeiro; **(3)** registre no bloco do `SLIDES.md` onde ela ficou.
>
> Sem o passo 2 isso vira perda de honestidade com aparência de design. O **S47** é o molde: três
> itens saíram, cada um conferido no destino (B1-1, S3, S50) antes de sair, e a nota está no bloco.

## 4d · A fala: quem é canônico

**`SLIDES.md` é a fonte; o `% FALA:` do `main.tex` é o espelho.** Estabelecido por medida:
o `SLIDES.md` nasceu primeiro (`f9b8f82e`), o portão de revisão operou nele (`d1491956`), o deck veio
depois (`5c2ee121`), e a correção dos revisores **flui SLIDES.md → main.tex** (o texto corrigido está
no `.tex`, o antigo tem zero ocorrências lá). Só o `SLIDES.md` carrega `LEDGER`, `Proveniência` e
`Nunca dizer`.

Deriva atual entre as duas cópias: **120 palavras em 11.259 (1%)**. Pequena, mas real.

**Corte sempre no `SLIDES.md` primeiro, depois propague.** Nunca o contrário: o `% FALA:` não
renderiza, então um erro lá fica invisível até alguém abrir o `.tex`. **E não apague o `% FALA:` do
`main.tex` para "resolver" a duplicação** — ele existe para que quem edita o slide veja a fala na
mesma tela, e é o que mantém tela e voz sincronizadas.

⚠ **O deck não cabe em 50 min, e isso é independente da densidade de tela.** A trilha de fala do deck
principal tem **8.935 palavras** = ~64 min a 140 ppm; caberia em 48 min só a **186 ppm**, dizendo IC
e correção de Holm. O desencontro é **concentrado**, não espalhado: S43–S46 e S48 somam ~1.400
palavras de fala contra ~7 min orçados. Os `Tempo:` por slide foram estimados por peso de assunto e
**nunca reconciliados** com o texto que os preenche. **Decisão de corte de fala é do autor.**

## 4e · A regra de edição — nós dois a pagamos, por caminhos diferentes

> **Edite por CONTEÚDO, nunca por índice de linha.** Um `.tex` ou `.md` reflui a cada edição, e um
> índice capturado antes do refluxo aponta para outra coisa depois.
>
> **Valide TODOS os anchors antes de escrever QUALQUER um.** Um script que aplica 3 de 4 e morre no
> quarto deixa o ficheiro meio editado, e ninguém sabe onde. Um que valida tudo primeiro e aborta
> sem escrever é recuperável de graça.
>
> **E valide contra o estado ATUAL do ficheiro, não contra uma leitura em cache.** Um script que leu
> o ficheiro no início, aplicou duas edições e depois valida o terceiro anchor contra o texto que
> leu no início está validando contra um ficheiro que já não existe.
>
> **Custo já pago, nas duas direções:** uma linha de RESULTADO apagada e outras duplicadas no
> `PLANO_FLUXO_DEFESA.md`, em três ocasiões da mesma sessão, por edição por índice depois do
> refluxo e por anchor validado contra cópia em memória. E, do outro lado, um script da varredura
> de densidade que abortou com *"anchor ambíguo"* e **não escreveu nada** — a falha segura
> funcionou, mas só porque existia; a maior parte dos scripts de edição escritos naquele dia não
> validava nada antes de escrever.

---

## 4f · O travessão nos slides — decisão do autor, com a base textual

> ⚠ **NÃO "conserte" isto numa varredura de estilo.** A `WRITING_LAW.md:131` diz *"No em-dash
> anywhere"* e o checklist em `:410` exige contagem zero. Um agente que rode essa regra sobre o deck
> vai querer eliminar todos. **O autor decidiu que não, em 2026-08-24, e a decisão tem base no
> próprio plano.**

**A regra, por FUNÇÃO e não por presença:**

| onde | decisão |
|---|---|
| **separador de rótulo** num fragmento — `\textbf{Semantic} --- the category of the visited place` | **fica** |
| **título de bloco** — `\begin{block}{Practical --- what it delivers}` | **fica** |
| **subtítulo de frame** — `\framesubtitle{Table 7, Florida --- the sequential target...}` | **fica** |
| **dentro de frase completa** — `...in place of two --- operational, not computational` | **sai**: vírgula, ponto e vírgula, dois-pontos ou duas frases |

**A base, e é o que torna a decisão defensável se um arguidor perguntar:**

1. A proibição vive sob **`§1 · Register: dissertation ≠ paper`**, num trecho sobre legibilidade de
   **prosa** (o teste do "um leitor não-nativo absorve isto numa leitura?"). A justificativa declarada
   é *"(Also an AI tell; also the MobiWac rule.)"*
2. A **regra 15 do `PLANO_FLUXO_DEFESA.md` §8**, que estende as três leis aos slides, contém a
   ressalva exata: *"**Um deck não é prosa**, mas as três leis governam **palavra e número** igual."*
   **Pontuação não é palavra nem número.** A regra 15 estende a autoridade sobre vocabulário
   (glossário fail-closed) e sobre afirmação/número — e antecipa a objeção declarando que um deck
   não é prosa.
3. A metade **"AI tell"** continua valendo, e é por isso que o corte foi por função e não zero:
   travessão dentro de frase é onde a densidade vira tell, e onde o teste de uma-leitura morde.

**Estado medido em 2026-08-24, depois da decisão:** deck principal com **93** travessões, todos
separador de rótulo, título de bloco ou subtítulo de frame; os **11 de dentro de frase foram
removidos**. A série B **não foi varrida** — decisão de escopo: ela só aparece sob demanda, e cada
slide tocado a quatro dias da defesa é risco novo de estouro de caixa.

⚠ **Se for varrer a série B depois, classifique por função primeiro.** Uma varredura por presença
sobre o deck teria tocado 105 lugares; apenas 11 precisavam mudar. Os outros 94 são estrutura
tipográfica, e trocá-los por vírgula produz fragmento ilegível.

---

## 5 · Decisões já tomadas — não reabra sem o autor

| Decisão | Ruling |
|---|---|
| **O vazamento do v18 sai da narrativa** | A dissertação **não o cita** (medido: `forward-only` tem zero ocorrências no PDF entregue). Narrá-lo poria na fala algo que a banca não acha no texto que julgou. **O que fica** é a direcionalidade, dita como **princípio de projeto**, nas palavras do próprio Cap. 5 |
| **Ordenação por LINHAGEM** | §2 só recebe o que é transversal **e não faz parte da herança que o arco narra**. MTLnet fica no Cap. 3 porque *"a mesma arquitetura, sem alterar uma linha"* é o argumento de controle do Cap. 4 |
| **Protocolo estatístico em 5.4**, não na §2 | Só o Cap. 5 o usa. Idem Acc@10 e joint-best |
| **Seções 3–5 levam o título do artigo**, não o veículo | Barra de navegação = a linhagem: MTLnet · ST-MTLNet · Check2HGI |
| **Seção 1 é genérica** | Sem "sete categorias", sem *mahalle*, sem nomes de estado — **exceto** a frase do veredito, que nomeia Flórida, Texas e Califórnia |
| **Karpathy não vai na conclusão** | Vai para a série B, como contexto ao oferecer o P1. *"Tasks fight for capacity"* é exagero na direção **oposta** à que a posição do tronco protege |
| **Q13/Q14/Q15** | Slides prontos para resposta **oral** |
| **NSO-46 fechado pela premissa inválida** | O parágrafo **não chega ao leitor** (zero aparições nos três builds). ⚠ **Não** por "não há vazamento no Cap. 3" — a auditoria mediu canal indireto e o confirmou por intervenção causal |

---

## 6 · Frases que não podem ser ditas

Estão espalhadas nas linhas `Nunca dizer:` do `SLIDES.md`. As que mais custam:

1. **`empata` / `matches` / `ties` / `em todos os conjuntos`** — nos dois eixos. O veredito é
   supera em **três células** e nada mais.
2. **A frase retratada:** *"o ganho vem da representação hierárquica e não da injeção de features"*.
   O controle refeito conclui que **a frase depositada está errada na direção**. Um revisor a
   encontrou no deck, entregue como fala, com os números da mesma tela a refutando.
3. **`meio ponto` no eixo de região.** É o limite da **categoria**. A margem derivada de região é
   **1,287 pp** — citar um no outro é exagero de três vezes.
4. **`o DGI não vaza`.** A auditoria mediu que vaza, de forma indireta. O que se diz é a diferença
   de mecanismo: **consulta exata no Cap. 4, média diluída a um salto no Cap. 3**.
5. **Qualquer macro-F1 de próxima categoria entre 54 e 80** — é número vazado pré-v18. A faixa
   entregue é **30–38**. ⚠ Escopado de propósito: Acc@10 de região vive em 59–77 e é legítimo.
6. **Misturar um número do `mtlcheck` com um da dissertação** na mesma frase. Protocolos diferentes.

---

## 7 · Como construir

```bash
cd slides
make check   # passe único: valida se compila. A CONTAGEM DE PÁGINAS DELE NÃO É A FINAL
make all     # 3 passes + bibtex. Use este para qualquer número que vá ser citado
```

- **O motor é `xelatex`.** `nesped.sty` carrega `fontspec`. Sob `pdflatex` o build "passa" e as
  telas com fundo saem **em branco** (caso 4 do §3).
- **O template tem quatro bugs corrigidos** só na nossa cópia (um quinto foi revertido pelo autor — ver §4) — os três antigos
  (`\pagewidth`→`\paperwidth`, o `\autotocframe` que vazava o argumento, o `\decorationnet` que
  nunca desenhava) e o de 24/08 (`width=\textwidth`→`\linewidth` em `\beamerboxesframed`).
  Cada um tem errata datada no `.sty`. O original de terceiros não
  foi tocado.
- **A série B usa `\miniframesoff`.** O número do frame **congela** ali — por isso cada slide B
  carrega o rótulo no conteúdo, não no rodapé.
- **Não rode `make` na pasta `../src/`** sem pensar: cinco alvos sobrescrevem o `dissertacao.pdf`,
  incluindo o `make` pelado. O `banca.pdf` está a salvo deles.

---

## 8 · Ambiguidades encontradas hoje, que precisam da palavra do autor

Trabalho não commitado apareceu depois do meu último commit. **Não sei quem o fez e não presumi.**

1. ~~**`slides_ux/`**~~ — **RESOLVIDO 2026-08-24: o autor decidiu ficar no `slides/`.** O
   `slides_ux/` é uma variante com fontes customizadas (Petrona + IBM Plex), 35 frames, incompleta.
   **Não é a direção.** Fica em disco como referência; **não construa a partir dele**.
2. ~~**`SLIDES_serieB.md`**~~ — **RESOLVIDO 2026-08-24: apagado, com a decisão do autor.** Era o
   rascunho do agente que escreveu a série B, **pré-revisão**. Estabelecido por medida, não por
   memória: dos 46 blocos, 43 têm corpo idêntico ao do `SLIDES.md`, **nenhum código existe só nele**,
   e os 3 que diferem são casos em que o `SLIDES.md` é a versão **posterior e mais cuidadosa** —
   inclusive `B3-7`, onde o rascunho ainda diz *"which **sits inside** the seed spread"*, a
   afirmação que `d1491956` ("os dois bloqueantes que os revisores acharam") trocou por *"of the
   order of"*. Manter era manter em circulação um texto que a revisão derrubou. **Recuperável:**
   `git show c7f0fd1f:articles/dissertacao/presentation/SLIDES_serieB.md`.
   **`SLIDES.md` é o canônico da série B — não recrie um segundo arquivo para ela.**

3. **`slides/_font_test.tex`** — teste de fonte, provavelmente descartável.

---

## 9 · Onde o conhecimento mora

| Assunto | Arquivo |
|---|---|
| De onde vem cada número entregue | `../CLAUDE.md` §0 |
| O que está aberto na dissertação | `../wrapup/open_points/LACUNAS.md` — 42 itens, 17 abertos |
| Perguntas de banca com resposta pronta | `../wrapup/open_points/ARGUICAO.md` |
| O que veio depois do envio | `../wrapup/` — a fronteira é declarada no README |
| O que ficou para trás | `../archive/` — **nada ali é fonte de nada** |
| A reescrita do sistema experimental | `../wrapup/NEW_VERSION.md` (`mtlcheck`) |
| Correções de nomenclatura estatística | `/Users/vitor/Desktop/mestrado/mtlcheck/mtlcheck/docs/NOMENCLATURE.md` |

---

## 10 · Como este autor trabalha

- **Ele aprova antes de qualquer mudança crítica.** Apresente opções com recomendação e espere.
- **Ele quer notificação** quando você precisar de decisão — não deixe pergunta parada em terminal.
- **Ele corrige o rumo com boas razões.** Duas das melhores mudanças do plano vieram de objeções
  dele: tirar o vazamento da narrativa, e recusar mostrar a Tabela 9 duas vezes.
- **Verifique a premissa dele antes de agir.** Uma vez a lembrança dele contradizia o registro (o
  vazamento do Cap. 3), e o registro existia porque ele mesmo pedira auditoria independente. Dizer
  isso claramente foi mais útil do que concordar.


---

# Anexo · Os outros tres handoffs da defesa

> **Consolidado em 2026-08-28**, depois de a defesa ter sido aprovada. Eram quatro ficheiros
> `HANDOFF*` sobre o mesmo evento, escritos por sessoes diferentes, com as mesmas seccoes
> repetidas (a armadilha central, as decisoes travadas, o estado do dia). O conteudo esta
> VERBATIM e cada seccao mantem o nome do ficheiro original.
>
> **O que aqui dura e o que nao dura:** as seccoes de *estado* (`Estado, em 24/08`, `O que eu
> estava fazendo quando parei`, `O que esta aberto`) morreram com a defesa. O que sobrevive sao
> os CATALOGOS DE ERRO -- `HANDOFF_GATE §3` (12 classes) e `HANDOFF_PPT §2` e `§7.1..7.7` --
> porque nao sao sobre slides, sao sobre como um instrumento devolve verde e mede outra coisa.


---

## `HANDOFF_SLIDES.md` — a sessao dos slides

# HANDOFF_SLIDES.md — para o próximo agente que mexer no deck

> **Escrito 2026-08-24.** Defesa **sexta, 28/08/2026, 10:00, remota (Google Meet)**. Banca: Fabrício
> A. Silva (orientador/presidente), Clayson S. F. de Sousa Celes (ITA, externo), Alex Borges.
>
> **Este documento é sobre COMO trabalhar no deck.** O estado e as armadilhas de build estão no
> [`HANDOFF.md`](HANDOFF.md) ao lado, que continua valendo inteiro — **leia os dois**. Onde eles
> divergirem, o `HANDOFF.md` vence nos fatos e este vence no método.
>
> **Quem aprova é o autor.** Ele decide sobre conteúdo, ênfase e forma. Você mede, propõe com
> opções, e espera.

---

## 1 · As cinco coisas que você precisa saber antes de tocar em qualquer arquivo

### 1.1 · A brevidade é o alvo, e ele tem uma referência medida

O deck foi reescrito em 2026-08-24 contra um alvo **empírico**, não uma opinião: a defesa de
**uma defesa anterior do mesmo programa**, mesmo programa, mesmo template NESPeD, gravada em
`/Volumes/linux/VIDEO/Screen Recording 2026-07-08 at 10.02.56.mov` (61 min, 4K).
⚠ **Não é um PDF.** Um agente anterior procurou por PDF, não achou, e concluiu que a referência não
existia — estando o caminho num doc que ele mesmo escrevera.

> ⚠ A gravação que sustenta esta medição foi apagada em 28/08/2026, por decisão do autor
> (conteúdo pessoal de terceiro, cópia única). O método e os valores ficam; a evidência
> primária não é reverificável.

**Medido em 10 slides amostrados da gravação: mediana 21 palavras de tela, média 28, máximo ~71.**

⚠ **Duas ressalvas de método, e as duas puxam para cortar MENOS:**
1. A contagem do a defesa de referência é **OCR sobre a gravação** e enxerga texto dentro de figura; a nossa é
   **corpo LaTeX** e não enxerga. Não são a mesma régua.
2. **A regra dele não é "sem frases".** Ele escreve frase completa exatamente onde a frase **É** o
   conteúdo (a pergunta de pesquisa, o que o estudo faz), e nunca para explicar ou ressalvar. O
   slide 3 dele tem 71 palavras, quase todas numa pergunta de pesquisa emoldurada.

**A regra aprovada pelo autor, seis pontos:**

| # | |
|---|---|
| 1 | No máximo **uma frase completa por slide**, e só quando a frase é o conteúdo. Bloco próprio, corpo grande |
| 2 | Todo o resto vira **fragmento** sem verbo conjugado, terminado em `;` |
| 3 | **Ressalva, justificativa e explicação saem da tela** e vão para a fala, ditas no mesmo fôlego |
| 4 | **Slide de resultado é tabela ou figura + legenda.** Nunca prosa ao lado |
| 5 | Guarda-corpo: mediana **25–30**, teto **~70** — e o teto só vale quando é *um* bloco lido de uma vez |
| 6 | Sair do `\scriptsize` como padrão. Não por legibilidade, mas porque **corpo maior força brevidade** |

**Estado atual, medido:** 53 slides de deck, **mediana 89**, máximo 143, total 4.6k palavras
(era 119/233/6.5k na manhã de 24/08). ⚠ **A mediana de 89 é o piso desta abordagem.** O que resta
acima de 70 **não é verbosidade**: são tabelas, figuras com legenda, carimbos de convenção e blocos
de redação mandatada. Chegar a 25–30 exigiria **tirar conteúdo da tela**, que é decisão do autor
sobre o que a banca vê, não reescrita.

### 1.2 · Onde consumir cada informação

| o que você precisa | onde está | ⚠ |
|---|---|---|
| **de onde vem cada número** | [`../CLAUDE.md` §0](../../CLAUDE.md) | **leia ANTES de escrever qualquer número.** É o erro mais repetido do projeto |
| a lei da estrutura do deck | [`PLANO_FLUXO_DEFESA.md`](PLANO_FLUXO_DEFESA.md), **§8 tem as 16 regras** | |
| o slide-a-slide | [`SLIDES.md`](../SLIDES.md) | **é a FONTE da fala**; o `main.tex` é o espelho |
| estado, build, armadilhas | [`HANDOFF.md`](HANDOFF.md) | **o §3 tem 7 casos de "o instrumento passou porque mediu outra coisa"** |
| a lei da palavra | [`../WRITING_LAW.md`](../../WRITING_LAW.md) | registro, lei dos verbos, construções banidas |
| o registro de termos | [`../GLOSSARY.md`](../../GLOSSARY.md) | **fail-closed**: termo fora do registro não pode ser usado |
| protocolo de número e afirmação | [`../AGENT_GUARDRAILS.md`](../../AGENT_GUARDRAILS.md) | |
| perguntas de banca com resposta pronta | [`../wrapup/open_points/ARGUICAO.md`](../../wrapup/open_points/ARGUICAO.md) | |
| a comparação com a literatura | [`../wrapup/open_points/BASELINES_EXTERNOS.md`](../../wrapup/open_points/BASELINES_EXTERNOS.md) | o que se pode afirmar, em qual eixo, e o que não |
| o roteiro de fala | [`SPEECH.md`](../SPEECH.md) / `SPEECH.pdf` | **gerado**, não editado à mão — ver §4 |

### 1.3 · As regras de escrita, e a exceção registrada

O `PLANO §8 regra 15` estende as três leis aos slides, **mas com uma ressalva que importa**:

> *"**Um deck não é prosa**, mas as três leis governam **palavra e número** igual."*

Consequência prática, decidida pelo autor em 2026-08-24 e registrada em [`HANDOFF.md` §4f](HANDOFF.md):
**o travessão fica quando é separador de rótulo, título de bloco ou subtítulo de frame; sai quando
faz trabalho de prosa dentro de uma frase completa.** ⚠ **Não "conserte" isso** — a
`WRITING_LAW.md:131` diz *"No em-dash anywhere"* e uma varredura ingênua vai querer eliminar os 93
que ficam.

⚠ **Lição de método, e vale para toda varredura de estilo:** a primeira contagem dizia 28 para
remover; a verificação caso a caso deu **11**. Uma varredura por *presença* teria tocado 105 lugares
onde 11 precisavam mudar. **Classifique por função antes de substituir.**

O que **está limpo** e você não precisa reverificar (medido 24/08): as listas banidas
(`delve`, `showcase`, `leverage`, `moreover`, `comprehensive`/`robust` decorativos) dão **zero** na
tela do deck principal.

### 1.4 · Use um agente Fable como revisor para o que é importante

**Decisão do autor.** Para qualquer coisa que envolva **conteúdo, ênfase, estrutura ou uma
afirmação que a banca possa atacar**, rode uma revisão crítica por um agente Fable **antes de
aplicar**. Isso não é cerimônia: numa sessão ele achou três defeitos que ninguém tinha visto.

| o que o Fable achou | o que teria acontecido sem ele |
|---|---|
| o slide de contribuições era, **inteiro**, tela de outros três slides — e um deles era o **imediatamente anterior** no fechamento | a banca veria dois terços de um slide repetidos um clique depois |
| o risco de reivindicar "superamos a literatura" no eixo de região, porque **um piso de Markov também supera dois dos três externos** | a manchete desmontaria numa única pergunta |
| uma referência para a frente: `graph-infomax` na tela do S7, mas a ideia é INTRODUZ no **S8** | defeito de ledger invisível a qualquer verificação mecânica |

**Como usar bem:** dê a ele o material verbatim (as passagens do texto entregue, as restrições, os
números medidos) em vez de um resumo seu — ele avalia a situação real, não a sua leitura dela. E
**peça explicitamente que discorde de você.**

⚠ **E verifique o que ele devolver.** Numa das rodadas ele atribuiu uma causa errada a um defeito
real, e a atribuição errada quase entrou num documento de lei. **Segunda opinião não é veredito.**

### 1.5 · A disciplina de fonte: `SLIDES.md` primeiro

O `SLIDES.md` é a fonte; o `main.tex` é o espelho. **Corte primeiro no `SLIDES.md`, propague, e
verifique com diff mecânico.** ⚠ Se você inverter (como já se fez, por pressa), **sincronize de
volta antes de commitar** — as duas cópias divergentes é o defeito que aquele arquivo existe para
impedir.

⚠ **Nunca apague o `% FALA:` do `main.tex`** para "resolver" a duplicação. Ele está lá para que quem
edita o slide veja a fala na mesma tela.

#### ⚠ Os números `S<n>` do `SLIDES.md` NÃO são a numeração da tela

Medido 2026-08-25. O `SLIDES.md` conta a capa como `S1`; o deck não numera a capa. Resultado: o bloco
`S8` era o **slide 7 impresso**, o `S12` era o **11**, o `S13` era o **12** — e mais adiante o
deslocamento muda outra vez (o `S28` é o **28** impresso). **Não existe uma fórmula.** O autor fala
por número impresso ("olha o slide 28"), o arquivo fala por outro.

E os números pioraram de propósito na reordenação da Seção 2 (2026-08-25): os blocos foram movidos
**sem renumerar**, porque **doze referências cruzadas dentro do próprio `SLIDES.md` apontam para eles
pelo número** (`"a Def. 2.12 é de S9"`, `"isso é de S10"`, `"ela é de S14"`, …) e renumerar quebraria
todas em silêncio. A ordem física do arquivo é a ordem do deck; os números são identidades
históricas.

> **Regra:** identifique slide por **título**, nunca por número — no `SLIDES.md`, no `main.tex`, nas
> âncoras de script e ao conversar com o autor. Quando ele disser um número, **confirme pelo título**
> antes de editar. É a mesma regra do §4e, e é por isso que ela existe.

---

## 2 · ⚠ A armadilha que mais custou: conteúdo que sai da página em silêncio

**Oito slides estouraram a caixa do frame numa única sessão, TODOS com `0 erros` e `0 overfull` no
log.** O LaTeX não avisa nenhuma vez, e o que não é desenhado **também não é extraído** pelo
`pdftotext` — então uma verificação de texto aprova.

Casos reais: a ressalva que a **regra 13 obriga** sumiu da página em **três builds seguidos**; o
botão de retorno ao índice sumiu de um slide de reserva; a linha de proveniência de outro; e o
slide 28 vazou pela borda de baixo em **duas** versões seguidas, trocando de coluna no meio (§2.1).

### O detector, e é barato: uma canária por frame

Pegue o **último elemento visível** de cada frame (é o que cai quando estoura) e exija que ele
apareça no texto extraído. **Quatro sub-armadilhas, todas já pagas:**

1. **Use `pdftotext` SEM `-layout`.** Com ele as colunas se intercalam linha a linha e o número da
   página entra no meio da frase do rodapé — a busca falha em conteúdo que **está** na tela.
2. **A sonda tem de ser CONJUNTO DE PALAVRAS, não frase contígua.** Uma quebra de linha derruba
   qualquer busca por frase — e não é ponto cego só de tabela: aconteceu num marcador de prosa
   comum. Compare palavras distintivas (≥5 letras) e exija ≥66% presentes.
3. **Apague `\begin{...}` / `\end{...}` com nome e argumentos** antes de extrair as sondas, senão os
   nomes de ambiente viram "texto" e a canária dispara em tudo (215 falsos positivos numa tentativa,
   62 de 101 noutra, independentes, pela mesma causa).
4. **A sonda envelhece com a edição.** Rederive-as do `.tex` a cada corrida; nunca leia de uma lista
   guardada. (Custo já pago: uma sonda procurando palavras que a reescrita da véspera removera.)

**E depois da canária, OLHE.** Renderize a ~1230 px, que é o tamanho real de uma janela do Meet:

```bash
pdftoppm -f <pagina> -l <pagina> -png -scale-to-x 1230 -scale-to-y -1 main.pdf /tmp/slide
```

A canária responde *"foi desenhado?"*. Ela **não** responde *"o bloco fecha?"* — um bloco pode ser
desenhado até a borda e parar, sem borda inferior, e só a renderização mostra.

**Quando o espaçamento não bastar, corte CONTEÚDO.** ⚠ **Nunca reintroduza `\vspace` negativo** —
foi assim que o deck acumulou 31 deles e as sobreposições que a varredura de 24/08 corrigiu.

### 2.1 · Em slide de duas colunas, largura não é alavanca — ela só muda de vítima

O slide 28 (`Why these encoders`, página 33 do PDF) é o caso didático, e vale ler antes de tentar
consertar qualquer slide de duas colunas.

| versão | o que se fez | o que aconteceu |
|---|---|---|
| v1 | — | o bloco **Spatial** (coluna estreita, 0.426, com mais conteúdo) vazava pela borda de baixo |
| v2 | reequilibrei as colunas para `0.478`/`0.452` + três cortes lexicais | Spatial fechou; **o vazamento migrou para o `Categorical`**, na coluna que ficou mais estreita |
| v3 | os três blocos de `\small` para **`\footnotesize`** | os três fecham |

A lição: alargar uma coluna estreita **estreita a outra**, e num slide que já está no limite isso
apenas transfere o estouro. Num slide de duas colunas as alavancas que de fato removem altura são,
nesta ordem: **cortar conteúdo**, **reduzir o corpo** (`\small` → `\footnotesize` ≈ 19 pt
projetados, ainda acima do piso de 16 pt da regra 10 — a régua é a geometria `16cm × 9cm` do
`nesped.sty`, **não** os 128 mm padrão do beamer), e só então mexer em largura.

⚠ **Reequilibrar largura obriga a renderizar as DUAS colunas.** Na v2 a canária deu 100% nas duas —
o texto do `Categorical` **estava** desenhado, só que metade dele fora da página.

### 2.2 · Nunca abra o corpo de um frame com uma chave

`\begin{frame}{título}{subtítulo}` é sintaxe válida do Beamer: **o segundo grupo de chaves vira o
subtítulo**. Então isto —

```latex
\begin{frame}{The line this work stands on, and the one idea on it}
    {\footnotesize \textbf{one-hot identifier} $\rightarrow$ ...}
```

— não põe a tira no corpo: põe **dentro da faixa colorida do título**, em fonte de subtítulo. Custou
um build em 25/08, e **a canária deu 100%**, porque o texto estava mesmo no PDF, só que no lugar
errado. Nenhum erro no log, nenhum overfull.

**O conserto é uma linha:** abra o corpo com algo que não seja `{` — `\vspace{0.5mm}`, `\par`,
`\noindent`, um `\begin{block}`. O frame fundido da Seção 2 carrega um comentário `⚠` explicando
isso logo acima do `\begin{frame}`; não o apague.

**A lição geral:** a canária responde *"o texto está no PDF?"*. Ela não responde *"está onde eu
mandei?"* nem *"o bloco fecha?"*. Só a renderização responde essas duas.

---

## 3 · A regra de edição, que dois agentes pagaram

> **Edite por CONTEÚDO, nunca por índice de linha.** Um `.tex` ou `.md` reflui a cada edição.
>
> **Valide TODOS os anchors antes de escrever QUALQUER um.** Um script que aplica 3 de 4 e morre no
> quarto deixa o ficheiro meio editado, e ninguém sabe onde.
>
> **E valide contra o estado ATUAL do ficheiro**, não contra uma leitura em cache.

Custo já pago: uma linha de RESULTADO apagada e outras duplicadas no `PLANO_FLUXO_DEFESA.md`, em
três ocasiões da mesma sessão.

---

## 4 · O `SPEECH` é gerado, não editado

`SPEECH.md` e `SPEECH.pdf` são o roteiro de fala em cartões, para uso **ao vivo**. **Se a fala mudar
no `SLIDES.md`, regenere** em vez de editar à mão:

```bash
cd articles/dissertacao/presentation
python3 build_speech_1_extract.py && python3 build_speech_2_emit.py
make -f Makefile.speech
```

Cada cartão tem quatro camadas em ordem de urgência: **ABRE** (a primeira oração), **DIZER** (os
trechos em negrito da fala, que são as superfícies de lei) ou **COBRE** (o LEDGER, onde não há
negrito), **NÚMEROS** (só os que são resultado) e **NUNCA**. Carrega o número impresso do slide **e**
a página do PDF, que são coisas diferentes.

---

## 5 · ⚠ O que está aberto, e é o mais importante deste documento

**A fala não cabe no tempo.** Medido: **~8.976 palavras** na trilha `% FALA:` do deck principal.

| ritmo | duração |
|---|---:|
| 130 ppm | 69,0 min |
| **140 ppm** | **64,1 min** |
| 150 ppm | 59,8 min |
| **teto do Art. 23** | **50 min** |

⚠ **Cortar tela NÃO compra tempo.** O conteúdo já estava na fala; ele só deixou de estar duplicado.
As duas varreduras de densidade tiraram 29% da tela e **zero** do relógio.

⚠ **E o estouro está ESPALHADO pelas seis seções**, não concentrado numa. Não há uma culpada para
sacrificar; distribuir ~2,5 min por seção dói muito menos que cortar 15 de uma.

**O instrumento que falta é o ensaio cronometrado, com marca no fim de CADA seção.** Com o total
sozinho o autor descobre que estourou e não de onde cortar. A tabela por seção, para levar ao
ensaio, está na primeira página do `SPEECH.pdf` com uma linha em branco por seção.

⚠ **Uma armadilha de medição, que já produziu um relatório errado:** para contar palavras de fala,
conte **tokens separados por espaço**. Dois contadores diferentes, de dois agentes, subestimaram em
16–19% — um por `{2,}` (que em português derruba `é`, `e`, `o`, `a`, `há`, entre as palavras mais
frequentes da língua), outro por regex ASCII (que derruba acentuadas). **E o relatório errado vinha
com "três medições independentes concordam em 1%": as três partilhavam o mesmo contador.**

---

## 6 · Decisões travadas — não reabra sem o autor

Estas foram decididas nesta sequência e têm o motivo registrado. **As de conteúdo estão no
[`HANDOFF.md` §5](HANDOFF.md); estas são as de deck:**

| decisão | onde está o motivo |
|---|---|
| **travessão por função**, não contagem zero | [`HANDOFF.md` §4f](HANDOFF.md) |
| **`match` verbatim** no slide do protocolo, com guarda | `SLIDES.md`, `Nunca dizer` do S44 |
| **`technical tie` verbatim**, vocabulário do Cap. 4 apenas | `SLIDES.md`, `Nunca dizer` do S30 + `GLOSSARY` §4 |
| **os cartões de logo colados ao topo da capa** — é o desenho do template, não defeito | [`HANDOFF.md` §4](HANDOFF.md); o `\vskip-2mm` foi restaurado |
| **a comparação com a literatura NÃO entra nas contribuições nem no Resumo** | [`../wrapup/open_points/BASELINES_EXTERNOS.md`](../../wrapup/open_points/BASELINES_EXTERNOS.md) §7 |
| ~~**a série B fica como está** (47 slides de reserva, densos de propósito: são lidos, não apresentados)~~ | ~~decisão do autor~~ — 🔄 **REVERTIDA PELO AUTOR EM 2026-08-27. Ver a nota abaixo.** |
| **a contribuição usa o recorte do grupo *Theoretical***, não a taxonomia do §6.2 | `SLIDES.md`, nota v2 do S7/S51 |

### 🔄 Reversão registrada — a série B, 2026-08-27

**A trava riscada acima foi levantada pelo autor em 2026-08-27**, em consulta direta, e substituída
pelas decisões `D-1`…`D-10` de [`SPEC_EXTRAS.md`](SPEC_EXTRAS.md) §0. Registrado aqui **como
reversão**, e não apagado, porque a entrada original carregava uma **razão** — e é a razão que mudou.

**O que a trava dizia:** *"densos de propósito: **são lidos, não apresentados**"*.

**O que o autor escreveu depois** (`archive/extra_RAW_2026-08-26.md`, e repetido na consulta de
27/08): os extras devem funcionar como *"apoio rápido durante perguntas **da banca**, e não como
páginas de apêndice que exigem leitura detalhada"*, permitindo que algo seja *"localizado e
compreendido rapidamente, **sem exigir que a banca pare para ler grandes blocos de texto**"*.

> **A leitora deixou de ser o apresentador e passou a ser a banca.** É essa mudança que autoriza a
> reforma inteira — faixa de título com a conclusão, corpo `\normalsize`, uma exibição apontável por
> tela, prioridade em quatro níveis. Sob a premissa antiga (telas para ler), metade dessas medidas
> estaria otimizando para um uso que não existe.

**Decisões que substituem a trava** (`SPEC_EXTRAS.md` §0): alvo ~50 páginas, **nada é cortado** além
de 6 fusões · o título inverte e a pergunta em português sai da tela · prioridade em 4 níveis com os
códigos mantidos · 3 cartões de conceito + δ-crítico + partição × k-fold · divisor `Extras`.

⚠ **Registrado por decisão explícita do autor** (*"levantada — registra"*, 27/08), justamente para
que ninguém implemente achando que está desfazendo uma decisão travada dele.

---

⚠ **Três copias, não duas:** o `[BLOCO-CONTRIBUIÇÃO]` do cabeçalho do `SLIDES.md`, o **S7** e o
**S51** carregam o mesmo texto. A **§8 regra 13** exige redação idêntica. Qualquer edição move as
três, e há um teste de sincronia no fim desta seção do `SLIDES.md`.

---

## 7 · O ciclo de trabalho, do começo ao fim

```bash
# 0 · leia  ../CLAUDE.md §0  e  HANDOFF.md §3  antes de tocar em número ou build
cd articles/dissertacao/presentation

# 1 · edite o SLIDES.md primeiro, depois propague para slides/main.tex
# 2 · build (o motor e' xelatex; sob pdflatex a capa e os divisores saem EM BRANCO)
cd slides && source ../../src_utils/texenv.sh && make all

# 3 · canaria: o ultimo elemento de cada frame tocado aparece no PDF?
pdftotext main.pdf -            # SEM -layout

# 4 · OLHE, no tamanho real do Meet
pdftoppm -f <p> -l <p> -png -scale-to-x 1230 -scale-to-y -1 main.pdf /tmp/s

# 5 · se a fala mudou, regenere o SPEECH (§4)
# 6 · sincronize SLIDES.md <-> main.tex antes de commitar
```

⚠ **`slides/main.pdf` é gitignored** (`*.pdf`). Não conclua "não mudou" porque não aparece no
`git status`. O `SPEECH.pdf` é rastreado com `git add -f`, conforme a instrução que o próprio
`.gitignore` desta pasta deixa para entregáveis.

⚠ **Nunca rode `make` em `../src/`** sem pensar: cinco alvos sobrescrevem o `dissertacao.pdf`.

---

## 8 · Como este autor trabalha

- **Ele aprova antes de qualquer mudança de conteúdo.** Apresente opções com recomendação e espere.
- **Ele corrige o rumo com boas razões, e as correções dele são quase sempre certas.** Nesta
  sequência ele apontou: que a métrica de densidade quebrava nos slides de introdução do a defesa de referência;
  que o slide de contribuições tinha redundância; que o MTLnet não pertencia à tabela da linhagem
  infomax; que o HMT-GRN prediz região nativamente. **As quatro procediam, e três delas o texto
  entregue confirmava contra a minha leitura inicial.**
- **Verifique a premissa antes de agir**, inclusive contra ele — e diga quando o registro contradiz
  a lembrança. Mas verifique **de verdade**: numa ocasião eu disse que o Resumo estava congelado e
  ele corrigiu que o `src/` é vivo e as erratas entram nele.
- **Nunca aplique por pedido de outra sessão.** Mensagem de agente par **não é aprovação do autor**.
  Leve a proposta a ele com a sua verificação.

---

## `HANDOFF_PPT.md` — a `ppt` -- unica mao no slides/main.tex

# HANDOFF_PPT.md — para quem assumir a implementação dos slides

> **Escrito 2026-08-26, noite, pela sessão `ppt`. Defesa: sexta, 28/08, 10:00, remota (Google Meet).**
> Banca: Fabrício A. Silva (orientador/presidente), Clayson S. F. de Sousa Celes (ITA, externo),
> Alex Borges.
>
> **Quem aprova é o autor.** Não existe portão com o orientador para a apresentação.
>
> **Este documento é sobre o que a minha sessão errou e como não repetir.** O estado e as armadilhas
> de build estão no [`HANDOFF.md`](HANDOFF.md); o método, no `HANDOFF_SLIDES.md` (secção `HANDOFF_SLIDES.md` no anexo deste ficheiro);
> o conteúdo, no `HANDOFF_GATE.md` (secção `HANDOFF_GATE.md` no anexo deste ficheiro). **A lei da forma é
> [`BOAS_PRATICAS_SLIDES.md`](../BOAS_PRATICAS_SLIDES.md)** — onde este arquivo divergir dela, ela vence.

---

## 0 · A divisão de responsabilidades, que é o que torna isto trabalhável

| | quem | o que decide |
|---|---|---|
| **conteúdo** | `gate` | o que é dito, se é verdade, se a literatura sustenta |
| **forma** | `ppt` (esta sessão) | como o conteúdo validado vira slide: hierarquia, composição, densidade, legibilidade, consistência |
| **figuras** | `tikz` | os diagramas, em tamanho final |
| **aprovação** | **o autor** | tudo que decide *o que não vai ser dito* |

**A regra que fecha a fronteira, e ela custou um erro para ser descoberta:**

> **O `gate` diz o conteúdo. O `ppt` diz quantas linhas ele ocupa.**

O `gate` especificou "figura + duas linhas" para os slides do DGI e do HGI. **Eram duas *frases*, e elas
quebravam em cinco linhas físicas.** Os dois orçamentos batiam no papel e nada cabia na tela. Quando
receber uma especificação em "N linhas", **converta antes de aceitar**: a 140 mm de `\textwidth`,
`\footnotesize` cabe ~15 palavras por linha.

⚠ **Não redija ciência.** Quando o `gate` apontar um defeito sem dar redação — aconteceu com o
`:1400`, que apontava uma coluna de desvio inexistente —, **aplique o que ele redigiu e devolva o
resto**. Inventar a frase certa ali é assumir o papel dele.

---

## 1 · O build. Esta é a regra que eu violei o dia inteiro

```bash
cd articles/dissertacao/presentation/slides
make all          # xelatex · bibtex · xelatex · xelatex -- TRÊS passes, em build/
```

**NUNCA** `xelatex main.tex` na mão, e **nunca** dois passes.

⚠ **`make all` leva 2–4 min. O tempo padrão do Bash é 120 s.** Rodar sem `timeout` maior faz o
build ser interrompido no meio e **deixa `build/main.log` pela metade** — e um log parcial não tem
`Overfull` para achar, então **a contagem dá zero e parece um deck limpo.** Isso me pegou três
vezes numa noite.

**Antes de ler o log, confirme as duas coisas:**
```bash
grep -c 'Output written' build/main.log     # 1 = completo, 0 = parcial
[ main.pdf -nt main.tex ] && echo ok        # PDF mais novo que a fonte
```
**Log com mtime MAIOR que o do PDF significa build em curso.** Qualquer número dali é lixo.

**O que dois passes produzem:** o divisor da Seção 5 renderizou **sem o fundo em degradê** — texto
branco sobre branco, os seis títulos do sumário invisíveis. O `remember picture, overlay` do
`nesped.sty` precisa das posições do `.aux` **convergidas**, e enquanto o conteúdo ainda se move dois
passes não convergem.

**NUNCA `pdflatex`**: compila sem erro e a capa, o sumário e todo `\specialframe` saem sem fundo.

---

## 2 · O catálogo de erros desta sessão, e o padrão que os une

**Todos têm a mesma forma: o instrumento funcionou e respondeu outra pergunta.**

| # | o que eu fiz | o que o instrumento disse | o que era |
|---|---|---|---|
| 1 | reportei ✔ 0,906 para o slide 44 | verdade — **da página 52** | o slide era a **51**, com `Overfull` de 24,4 pt e uma condição inteira cortada fora da página |
| 2 | `grep 'fine class'` | 0 ocorrências | a fonte quebra a linha **entre as duas palavras** |
| 3 | "zero `Overfull` novo" na nota do 27 | verde no `\hbox` | o defeito era `\vbox` — **10,5 pt**, e a tinta subiu para 0,973 |
| 4 | "o total declarado está superestimado" | verdade **para o S45** | no agregado **subestimava em 9:22** |
| 5 | "os overlays são +4:00 do excesso" | — | **minha própria tabela somava +2:36** |
| 6 | medi 444 palavras de deriva na fala | verdade | varri o bloco `% FALA` inteiro, que **também guarda notas datadas de projeto** |
| 7 | contei a fala do S34 em 8 s | verdade sob a minha regra | a regra de parada listava `Próxima` como marcador de nota, e **a fala começa com "Próxima região é…"** |
| 8 | atribuí falas a frames por ordem | verdade | as falas de **divisor de seção** não têm frame próprio e contaminavam o frame seguinte |

**Três checagens que teriam pego todos:**

1. **ancore a verificação no número impresso lido do PDF na mesma execução**, nunca num índice de
   página lembrado;
2. **quando afirmar um agregado, some-o**. Não infira a direção de um caso;
3. **pergunte o que o instrumento NÃO responde** antes de reportar o verde dele.

### 2.1 · A quarta classe, que nenhum instrumento pegava

O divisor sem fundo **passou pelos três**: o `pdftotext` extraía os seis títulos, nenhum `Overfull`
disparou, e a varredura de tinta **classificava a página como fundo cheio e a excluía** — a regra que
existe porque `\specialframe` e `\tocframe` são legitimamente escuros era a que escondia o defeito.

**Quem achou foi o autor, olhando.**

**Corrigido no instrumento** (`ink_sweep.py`, 26/08): numa página que deveria ter fundo, a regra
inverte e **exige tinta em vez de ignorá-la**. Validado contra o render da página quebrada:

| | tinta na área útil | |
|---|---:|---|
| divisor quebrado | **0,02 %** | dispara |
| divisor saudável | 99,0 % | excluído como fundo cheio |

### 2.4 · Contra reescrita, o `diff` é estruturalmente cego

**A pergunta certa não é "os dois textos batem?", é "o que entrou no original DEPOIS que a
reescrita nasceu?"**

O `diff_fala.py` compara fala↔fala. **Entre uma fala e a reescrita dela a similaridade é 0,20–0,37
por desenho** — a reescrita é 50% menor. A ferramenta reportaria divergência máxima, estando certa
e sendo inútil. ⚠ **É a única classe para a qual ela é cega por construção.**

**Caso real (27/08):** cinco falas curtas escritas em 26/08. Comparar não achou nada. **Procurar o
que entrou depois achou:** o `gate` acrescentara um "asterisco honesto" à fala do protocolo 4 no
dia seguinte, e a reescrita não o tinha. **A tela carrega um `*` cujo referente estaria só na
versão antiga** — rodapé órfão, que é a divergência tela↔fala ao contrário e a pior das duas.

### 2.5 · Imitar o vizinho propaga o defeito do vizinho

**Eu medi que `\textcolor{gray}` (= `black!50`) dá 3,95:1 e reprova a WCAG AA. Escrevi no
`BOAS_PRATICAS`. E no dia seguinte usei `\textcolor{gray}` num rodapé que escrevi.**

**Não foi esquecimento — foi imitação.** Copiei o rodapé de um frame vizinho para acertar o idioma
da seção, e vieram junto a cor errada e o formato. **Levei o meu próprio achado para dentro do erro
que ele descrevia.** Os 49 casos iguais na Série B vinham todos da mesma imitação.

⚠ **E o conserto criou uma superfície de erro que não existia.** O rodapé velho dizia *"migrado em
27/08"* — **não tinha número nenhum para estar errado**. Ao escrever proveniência de verdade,
escrevi `Figura 4` onde é `Figura 6, p. 80`. **Fazer certo custa uma verificação que fazer
parecido não custava.**

### 2.3 · Um número derivado escrito à mão não sabe que ficou velho

Formulação do `gate`, 26/08, depois de encontrar **37 dos 49 campos `Slide impresso:` do
`SLIDES.md` deslocados em +1** — um bloco removido tinha ficado na lista ativa e empurrou toda a
numeração a partir dele.

⚠ **O perigo é o silêncio.** Se a instrução *"inverta os impressos 13 e 14"* viesse dessa tabela,
os slides invertidos seriam os errados — **e nada reclamaria**: os dois números existem, os dois
frames existem, compila, o `Overfull` não muda, a tinta não muda, o `pdftotext` extrai tudo.
**Nenhum instrumento de página vê.**

**A defesa, nas duas superfícies:**

| onde | como |
|---|---|
| **na tela** (LaTeX resolve) | `\label` no frame alvo, `\ref` no que cita. Testado sob o tema nesped: devolve o número impresso correto |
| **em documento** (não resolve) | **re-derivar do artefato e verificar por título**, nunca ajustar à mão |

**Nunca ajuste à mão** — ajustar à mão é como os 37 sobreviveram.

⚠ **E marque o tempo quando um comentário citar número.** Um comentário que diz *"o **antigo**
impresso 37"* é seguro; um que diz *"o impresso 37"* é indistinguível de um que envelheceu.

### 2.2 · A quinta classe: a fala e a tela divergem

Quando o corpo de um slide muda, **não envelhece só o título — envelhecem o título, a fala e a
proveniência.** Nenhum dos três dispara `Overfull`, e nenhum instrumento de página os alcança,
**porque o defeito não está na tela: está na diferença entre a tela e a boca.**

Casos reais: o slide 3 perdeu *"point-of-interest prediction"* da tela e a fala continuou dizendo-o;
o `M29` tirou *"acima do HMRM em todas as categorias"* da tela e a fala manteve; o `M23` tirou
*"o Capítulo 5 não se apoia nisso"* e a fala manteve.

**A varredura** — cinco linhas de regex sobre os blocos `% FALA` da trilha principal, com o frame
dono resolvido por posição — procura **os termos que se sabe terem saído da tela**:

```python
ALVOS = {'pontos de interesse': 'saiu da ancora', '95 por cento': 'o CI virou 90%', ...}
# para cada linha de comentario que casar, resolve o \begin{frame} seguinte e reporta os dois
```

⚠ **Confira cada achado lendo o contexto antes de reportar.** Na primeira rodada, **2 das 4
ocorrências eram falsas** — uma era a ressalva do MobiWac, que diz "submetido" de propósito, e a
outra dizia "computação" no sentido certo do par `operational / computational`.

⚠ **O limite, que precisa ser declarado junto:** ela só acha termo que alguém **sabe** ter tirado.
**Uma fala que envelheceu por mudança de sentido sem mudança de palavra passa direto** — essa é a
triagem semântica do `gate`, e esta varredura não a substitui.

---

## 3 · Padrões de forma que valeram altura, sem cortar palavra

- **`\begin{center}` é uma `trivlist` e cobra `\topsep` dos DOIS lados.** Trocar por
  `\noindent\makebox[\textwidth]{…}` devolve **~8 pt por figura**, de graça;
- **a moldura de um `block` custa ~28 pt de cromo sem texto.** Primeira coisa a examinar quando um
  slide estoura por poucos pontos;
- **fórmula em `\[ \]` custa duas linhas a mais que a mesma fórmula inline**;
- **rebalancear colunas** (42/55 em vez de 48/48) tira duas linhas sem cortar uma palavra;
- **conteúdo centrado cresce para os dois lados**: a altura absorvível é `2 × min(folga acima, folga
  abaixo)`, medida a partir da base real da faixa de título **daquela** página.

### 3.0 · Quem recusa fica devendo a revisita

A `tikz` recusou separar a discriminação do fluxo na chapa do HGI, **por uma razão medida e
verdadeira na hora**: as entradas do `POI–Region` teriam de atravessar uma faixa inteira e o
resultado era um novelo. Depois ela introduziu os conectores A/B **para outro problema** — e eles
derrubavam a recusa anterior como consequência direta. **Ninguém voltou a testar.** Só reabriu
porque o autor insistiu, e a chapa nova é melhor **e mais baixa**.

> **Quem recusa fica devendo a revisita quando a própria caixa de ferramentas muda — e o dono da
> recusa é quem tem menos chance de notar, porque já resolveu aquilo na cabeça.**

*(Formulação da `tikz`, corrigindo a minha, que era mais leniente: eu tinha escrito "sem ninguém
perceber", como se fosse acidente sem dono.)*

### 3.1 · A regra que decide corpo quando dois elementos competem

> **O que a tela precisa carregar sozinha tem prioridade de corpo sobre o que a fala carrega junto.**

Os números de uma tabela nunca são lidos em voz alta; as ressalvas obrigadas pela §8.6, sim. Por isso
a ressalva metodológica do HGI ficou na tela em `\footnotesize` e a explicação causal foi para a fala.

### 3.2 · ⚠ A armadilha do subtítulo — três reincidências

`\begin{frame}{título}{grupo}` é sintaxe válida. **Se o corpo abrir com `{`, o beamer lê o grupo como
subtítulo** e o conteúdo renderiza dentro da faixa colorida — com log limpo e `pdftotext` extraindo
tudo. **Uma linha em branco depois do título também encerra a varredura do argumento opcional.**

O guarda é uma linha que se declara:

```latex
\begin{frame}{Título}
    \vspace{0pt}% ⚠ GUARDA -- NAO REMOVER. Sem algo que nao seja "{" abrindo o corpo, o
    % beamer le o grupo seguinte como SUBTITULO. Custa zero altura.
    {\small ...
```

> **Um guarda que parece folga vai ser removido por quem estiver otimizando folga — inclusive por
> quem o pôs.** Eu removi o meu numa varredura de espaçamento e reintroduzi o defeito.

---

## 4 · O pipeline do SPEECH

```
SLIDES.md  →  build_speech_1_extract.py  →  build_speech_2_emit.py  →  make -f Makefile.speech
```

**O extrator lê só quatro campos:** `Tempo:`, `Fala (PT):`, `Nunca dizer:`, `LEDGER:`.
⚠ **`Na tela:` e `Proveniência:` NUNCA chegam ao SPEECH.** Regenerá-los não muda o roteiro — o valor
deles é servir de referência a quem escreve a fala.

**Ordem obrigatória:** `SLIDES.md` → reconstruir o deck → regerar o SPEECH. Gerar antes produz um
roteiro de um deck morto, **que é pior que um roteiro velho porque parece novo**.

**Dois defeitos corrigidos em 26/08:**
- o regex era `### (S\d+) · ` e **não casava com sufixo de letra**. `S5b` (o slide das tarefas) e
  `S26b` eram **invisíveis** — duas telas iriam para a defesa sem fala nenhuma, sem nenhum aviso.
  Agora `### (S\d+[a-z]?) · `;
- consertar só o regex **quebrava o emissor**, que fazia `int(code[1:])` em cinco pontos. Chave
  numérica `_n()` que ordena `S5b` logo depois de `S5`.

⚠ **Valide o emissor num sandbox, nunca no lugar.** A minha primeira correção deixou escapar uma
quinta ocorrência e o emissor explodiu — se eu tivesse rodado na pasta real, teria destruído o SPEECH.

### 4.2 · ⚠ A fala é o que está ENTRE ASPAS

Descoberto 26/08. **Doze dos 56 blocos carregavam anotação editorial dentro do campo
`Fala (PT)`** — um parentético de versão antes da aspa de abertura, uma nota de revisão depois da
de fechamento. O extrator lia o campo inteiro, então o roteiro impresso traria
`*(v3, 26/08 — a primeira frase foi refeita…)*` **no meio do que o autor lê em voz alta.**

**Não era visível de lado nenhum:** no `SLIDES.md` a anotação está formatada e é o `gate`
escrevendo para si mesmo; no `.tex` ela não existe. **Só aparece no que o extrator produz.**

**A regra, medida antes de ser adotada:** 55 dos 56 blocos põem a fala entre aspas e a anotação
sempre fora delas. `so_a_fala()` faz, **nesta ordem**:

1. remove `*(v… )*` e tudo a partir do primeiro `⚠`;
2. toma o que está entre a primeira e a última aspa;
3. cai para o campo inteiro se não houver aspas.

⚠ **A ordem não é arbitrária.** Limpar as aspas primeiro falha: uma nota de revisão pode **citar
outra nota entre aspas**, e o `rfind` cai dentro da citação. **Editorial primeiro, aspas depois.**

**E o passo 3 é silencioso por desenho** — daí o guarda `_guarda_editorial()`, que falha o build
com o código do bloco se sobrar marca editorial. Cobertura medida com casos sintéticos: um bloco
sem aspas com `*(v…)*` ou `⚠` **já está coberto pela pré-limpeza**; o guarda pega **marca
editorial em prosa**, que é a que ninguém antecipa.

⚠ **O guarda NÃO enumera marcas, e a razão é medida.** O `gate` usa **19 formas** de anotação e
**inventou 4 delas num único dia** — uma lista persegue um alvo que ele move sozinho. A invariante
substitui as 19:

> **Nenhuma fala legítima tem crase.** O autor não diz caminho de arquivo, nome de variável nem
> número de seção em voz alta. Mas **toda** marca editorial que sobreviva ao `so_a_fala` carrega
> uma — `` `AUT-19` ``, `` `main.tex:759` ``, `` `§8.11` ``.

Medido nos dois lados antes de adotar: **0/56 falas extraídas têm crase**, e **3 campos brutos
têm** — isto é, zero falso positivo e a limpeza está funcionando. O glifo de status
(`✅🔴🛑⟵⚠`) entra junto: é a marca usada quando não se põe crase. **Testado: dispara inclusive
numa forma que o `gate` ainda não inventou.**

### 4.1 · Contar a fala

Regra: **tokens separados por espaço, sem filtro** (qualquer filtro subestima 15–20 % num idioma
latino). Divida por **140 ppm**.

- **o bloco de fala termina** no primeiro comentário que seja nota de projeto (`% NOTA`, data ISO,
  `% [BLOCO`, `⚠`). **Não liste palavras comuns como marcador** — foi assim que `Próxima` decepou a
  fala do S34;
- **pareie fala↔frame por posição no arquivo**, nunca por título: quatro overlays compartilham
  `\frametitle` e uma chave por título colapsa três deles;
- **uma fala que não precede imediatamente um frame é divisor de seção** e não pertence a nenhum.

---

## 5 · Estado do deck em 26/08, 19h

- **105 páginas · 48 slides impressos** — estado de 27/08, 02h
- **os 6 divisores e a capa desenharam o fundo** (verificado por luminância, não por fé)
- **0 colisões** com o número do frame · tinta máxima **0,977** · mediana **0,914**
- **17 páginas acima de 0,93**, duas delas deliberadas e registradas: **41 · The verdict** e
  **24 · The diagnostic result** — ambas completas, nada cortado
- **as chapas do DGI e do HGI integradas** (slides 14 e 22), sem `width=` — vêm em tamanho final,
  **`Overfull` zero nas duas** (DGI 50,4 mm, HGI 123,7 × 57,2 mm com a discriminação em faixa própria)
- **fala escrita: 7.607 palavras = 54:20 a 140 ppm.** Com as cinco reescritas do `gate` pendentes de
  aprovação do autor: **6.900 = 49:17**

⚠ **"49:17" e "cabe" não são a mesma frase.** É leitura corrida, sem pausa e sem uma frase a mais
para responder um olhar da banca. O Art. 23 é **teto**, não alvo.

- **slide 3** reconstruído na moldura do impresso 6 do template: frame comum, título + parágrafo
  em `\Large`, fora do `\specialframe` (ver §5.7 do `BOAS_PRATICAS`). A pergunta vem do objetivo
  geral do volume entregue, sem parênteses
- **slide 30** (`AUT-18`): só a imagem. ⚠ **A `fig1_dataflow` estava a `0.50\textwidth` sendo que
  o tamanho natural dela é 136,6 × 62,4 mm** — exibida pela metade, com o texto interno abaixo do
  piso de legibilidade. Os quatro marcadores é que a espremiam; a fala carrega os quatro
- **varredura visual** das 9 páginas mudadas, renderizadas a 1230 px (tamanho do Meet): todas OK

### 5.0b · A bijeção dos links não é frame↔alvo

**A regra de aceitação é `\hyperlink` ↔ `\hypertarget`: todo código resolve, nenhum alvo fica sem
link.** ⚠ **NÃO é "um alvo por frame".** Depois da reescrita da Série B, códigos fundidos mantêm o
próprio `\hypertarget` no frame de destino — é assim que um botão antigo continua resolvendo.
**Uma conferência que espere `N frames == N alvos` reprova um deck correto, com autoridade.**

Hoje: **50 frames, 50 alvos.** Previsto após a reescrita: **50 frames, 55 alvos.**

### 5.1 · Em aberto — tudo é decisão do autor

| | |
|---|---|
| **o corte de ~4 min** | 49:17 como está · −180 palavras para 48:00 · −320 para 47:00 |
| **as cinco falas curtas** | medidas (707 palavras cortadas), **não aplicadas** |
| **`S46`** | o `gate` segura a sincronização até o corte ser decidido |
| **SPEECH não regerado** | ordem obrigatória: `SLIDES.md` → reconstruir → regerar |
| **gênero da figura do 30** | `c2h_flow.pdf` pronto; **não bloqueia nada** — trocar é uma palavra |

---

## 6 · O protocolo, em ordem

```bash
cd articles/dissertacao/presentation

# 1 · SLIDES.md primeiro, depois propague para slides/main.tex
# 2 · TRÊS passes, sempre
cd slides && make all

# 3 · canária -- o último elemento visível de cada frame tocado aparece?
pdftotext main.pdf -            # SEM -layout

# 4 · tinta, e agora também a página pálida (§2.1)
cd .. && python3 ink_sweep.py slides/main.pdf

# 5 · OLHE, no tamanho real do Meet
pdftoppm -f <p> -l <p> -png -scale-to-x 1230 slides/main.pdf /tmp/s

# 6 · SPEECH só DEPOIS de reconstruir o deck
python3 build_speech_1_extract.py && python3 build_speech_2_emit.py
```

**O que cada passo não responde:**

> **Extrair o PDF pega termo errado; só renderizar pega conteúdo ausente.**
> **E só olhar pega o que foi desenhado em branco sobre branco.**

**Antes de escrever qualquer edição em lote: valide TODAS as âncoras primeiro, escreva só depois.**
Um `sys.exit` antes da primeira escrita já me impediu duas vezes de corromper arquivo alheio — uma
delas porque `MobiWac 2026, submitted` tinha duas ocorrências e a segunda era nome de artefato.

---

# 7 · A rodada de 27–28/08 — o que ela ensinou que as anteriores não tinham

Um dia inteiro de execução com o `gate` e o `extra`, na véspera da defesa. Sete classes novas, e a
maioria é sobre **instrumentos que funcionam e respondem outra pergunta** — a família que este
documento já registrava, agora com casos que a nomeiam melhor.

## 7.1 · 🛑 `columns` que transborda NÃO gera `Overfull`

**O defeito mais caro do dia, e ele quase foi para a defesa.** O slide 32 em `\small` perdia a
palavra `MERGE` — a última da frase que a própria fala designa como *"a que eu quero que fique da
tela"*. Log limpo, `Overfull` zero, metade da frase-chave fora da página.

> **Uma coluna de `columns` estoura em silêncio.** A varredura de caixa do deck é contagem de
> `Overfull`, então **todo slide de duas colunas esteve fora do alcance do instrumento principal**
> — e são ~11 frames, incluindo o índice B0.

**O instrumento:** `canaria_coluna.py`. Extrai a última palavra visível de cada `column` do `.tex` e
procura-a — **palavra única, nunca frase** — no `pdftotext` **daquela página**. Roda também o teste
dos botões do índice.

⚠ **Ela própria teve dois defeitos, e ambos são a lição:** colhia nome de cor de dentro de
`\textcolor{secondary}{...}`, e quando não localizava a página **caía para procurar em todas** — o
que transforma qualquer palavra comum num verde sem valor. **Agora responde `?  (página não
localizada)`.** Uma canária que não sabe dizer *não sei* não é canária.

## 7.2 · 🛑 O rótulo de um botão de índice é indistinguível do código do slide

**Três vezes no mesmo dia.** Qualquer busca por `\textbf{B6-6}` ou `\textbf{B-P1}` encontra **o botão
do índice B0**, porque o índice vem antes no ficheiro. Consequências reais:

- o detector de `Overfull` mediu o índice e respondeu **`✅ CABE`** num frame **45 pt fora**;
- uma medição de folga inteira foi feita no frame errado e reportada como boa;
- eu quase reportei ao `gate` que um slide não continha um termo que continha.

> **A âncora certa é o `\framesubtitle` do próprio frame**, resolvido dentro do intervalo
> `\begin{frame}…\end{frame}`. Nunca a string do código solta. Está em `/tmp/_ov.py` e devia ser
> promovido a ferramenta versionada.

## 7.3 · 🛑 Substituir um intervalo de frames leva as falas que estão entre eles

A fala vive no `% FALA:` **fora** do frame. Ao trocar dois frames por dois novos, **apaguei 57
palavras de fala** sem perceber — e nenhuma verificação de PDF a apanha, porque comentário não
renderiza.

> **A regra: contar os `% FALA:` antes e depois de qualquer substituição de intervalo.** Usei-a nas
> três migrações seguintes: `96 → 96 → 96`.

## 7.4 · Palavras não preveem altura — nos dois sentidos

| o que se pediu | o que custou |
|---|---|
| `+8 palavras` (par `hard`/`soft`) | **+27,64 pt** — o `\\` força duas linhas novas |
| *"corta as caixas 1 e 2 antes da 3"* | **zero** — a altura de uma linha de `minipage` é o **máximo** das três |
| tirar uma coluna 100% derivável | **zero** — o estouro era contagem de linhas, não largura |
| rebalancear larguras de tabela | **piorou** (11,56 contra 2,06) — estreitar uma coluna empurra linhas |

> **A fronteira, formulada com o `gate`:** *quando a minha alavanca muda **quais palavras estão na
> tela**, ela é dele; quando a spec dele contém uma instrução de composição (`\\`, `\vspace`,
> `minipage`, `tabular`), o custo é meu de medir.* **Nenhum dos dois prevê o lado do outro.**

## 7.5 · ⚠ Remover metade de um par simétrico não remove metade do efeito

Tirei só o `\vfill` de baixo de um frame: **de +6,1 para +22,6 pt.** Sem par, o de cima empurra tudo
para o fundo. **Forma pura, erro inteiro meu.**

## 7.6 · Sondas que fazem no-op silencioso

`str.replace(a, b)` devolve a string **intacta** quando `a` não existe. Duas sondas minhas mediram
ficheiros que não continham o que eu pensava estar a medir, e **reportaram `✅ CABE`**.

> **Toda substituição — em sonda também, não só em aplicação — leva asserção de contagem antes.**
> A partir daí as sondas passaram a recusar (`🛑 4 ocorrências, esperava 1`) em vez de mentir.

## 7.7 · Réguas que medem o próprio cromo

A varredura de tinta reportava **50 páginas** acima de 0,96. **Era o número do frame**, que vive na
faixa direita e desce a ~0,987 em toda página. Excluindo os 7% à direita: **16 páginas**, das quais
**uma** na trilha principal.

> **Quarta régua do dia a incluir no alvo alguma coisa que está lá por desenho** — junto com o
> `Overfull` ancorado no `\begin`, o detector que achava o índice, e a canária que caía para "todas
> as páginas". **O padrão é sempre o mesmo.**

## 7.8 · Duas coisas que a forma resolveu melhor que o corte

- **O `B7-3` pagou a dívida declarada com CONTEÚDO, não com cromo.** Eu tinha escrito *"as minhas
  alavancas de cromo estão esgotadas neste frame"* — e estavam. Dois cortes de prosa do `gate`
  compraram um **degrau inteiro de corpo** (`\footnotesize` → `\small`).
- **Dividir venceu caber.** O `B6-6` não comportava duas cláusulas novas mais o rodapé (medido:
  +2,06 · +17,28 · +36,28, com o rodapé a cair fora em silêncio). **Partido por eixo, tudo entra** —
  e cada ressalva fica ao lado da tabela a que pertence, que era o que o conteúdo já pedia.

## 7.9 · Coordenação: o ficheiro tem um dono de cada vez

Em 28/08 havia **duas sessões `ppt`** e a mesma spec podia chegar às duas.

> **Antes de escrever depois de uma pausa: `stat` no `main.tex` e conferir marcas conhecidas das
> próprias edições.** Uma resposta do outro agente é mais lenta e mais fraca que a evidência do
> ficheiro. E uma mensagem de coordenação pode ficar **retida à espera de aprovação** — não a
> esperes.

---

# 8 · A rodada de citações (28/08) — quatro classes que só aparecem ao inserir em massa

Quarenta e uma citações mapeadas, vinte e oito aplicadas, uma decisão devolvida ao autor.
As lições são sobre **inserir texto curto em muitos sítios de uma vez** — um regime que nenhuma
das rodadas anteriores tinha exercitado.

## 8.1 · 🛑 A unidade de custo é a LINHA, e linhas são quantizadas

Quatro medições no mesmo dia, todas contra a intuição de caracteres:

| pedido | previsto | medido |
|---|---|---|
| `+8 palavras` (par hard/soft) | pequeno | **+27,6 pt** — o `\\` força duas linhas |
| *"corta as caixas 1 e 2 antes da 3"* | libertaria espaço | **zero** — `minipage`: altura é o **máximo** |
| ordem de sacrifício do slide 21 | libertaria uma linha | **zero** — cortava a coluna **mais curta** |
| citação só com o ano (`251 → 84` caracteres) | `40,8 → 13,6 pt` | **+42,39 pt, idêntico** |

> **Caracteres não compram nada até removerem uma quebra.** E numa `columns`/`minipage`,
> **só a coluna mais alta paga** — cortar da outra é trabalho perdido por mais conteúdo que saia.

**O fluxo que funciona**, acordado com o `gate`: ele manda o conteúdo, **eu meço e digo onde o corte
tem efeito**, ele escolhe o quê. No slide 21 isso produziu um corte que era **redundância criada por
nós dois**, não sacrifício.

## 8.2 · 🛑 Um inseridor precisa de fronteira de palavra E de olhar à volta

Três defeitos distintos numa única passagem de 28 inserções:

- **`Sphere2Vec (Mai et al., 2023)-M`** — `str.find` casa `Sphere2Vec` dentro de `Sphere2Vec-M`.
  **A correção é `(?<![\w-])nome(?![\w-])`.** Também morde `STAN` dentro de `Standley` e `HGI`
  dentro de `Check2HGI`;
- **`(MTL (Caruana, 1997))`** — a citação entrou num parêntese que já existia. **Fronteira de
  palavra não resolve isto**: é preciso olhar o contexto. A saída melhor não é desaninhar (custou
  6,24 pt ao empurrar a quebra) — é **fundir**: `(DRRGNN, Zhu et al., 2022)`;
- **`\\scriptsize`** — o meu script de conserto escreveu barra dupla dentro de uma f-string. **Em
  LaTeX `\\` é quebra de linha e o build PASSA**, projetando uma quebra mais o texto literal.
  **Um conserto silencioso pior que o defeito.** Apanhado ao reler a linha, por nenhuma varredura.

## 8.3 · ⚠ Sucesso PARCIAL é mais perigoso que falha total

O aplicador resolvia o frame pelo número impresso. **Três versões, três resultados:**

    v1  exigia que o titulo casasse um padrao      ->  39 aplicadas, 6 falhas
    v2  contava TODOS os \begin{frame}             ->   2 aplicadas, 43 falhas
    v3  conta todos, exclui os comentados          ->  45 aplicadas, 0 falhas

> **A v1 é a perigosa.** Ela não deu erro — deu **39 sucessos**, e as 39 estavam em frames
> **deslocados**. As seis falhas fazem olhar para o sítio errado. Se eu não tivesse conferido as
> seis contra o PDF, teria medido outro deck e o `gate` teria decidido cortes com base nele.

⚠ E a causa da v2 é a mesma família do `% FALA:`: **eu próprio escrevi `% \begin{frame}{...}` em
comentários a explicar sintaxe**, e cada um contava como frame. **O comentário é invisível para o
leitor e visível para a ferramenta.**

## 8.4 · Um instrumento que acerta por acidente encerra a investigação

O `gate` foi confirmar a margem de 2 pp e encontrou `tost=0.02` em `finalize_phase3.py:267`.
**O número batia. A chamada era de outra etapa** (Check2HGI × HGI, não o teste do veredito).

> **Um instrumento que erra chama atenção; um que acerta pela razão errada fecha a pergunta.**
> O que o salvou foi o autor ter escrito *"confira se os 2 pp correspondem a esse teste e não a
> outra etapa"* — a pergunta certa veio de fora.

## 8.5 · Onde o deck ficou

    104 paginas · 6 Overfull, todos < 6,3 pt · 55/55 links · zero orfaos · 96 falas
    canaria de coluna: 21 colunas · canaria de indice: 54 botoes · SPEECH 48:23

**Aberto, e todo com outros:** as doze citações do slide 8 (não cabem em nenhuma das quatro formas
medidas — decisão do autor), o `tower` na Série B (`extra`), e a chapa `c2h_deep` a dizer
`pretrained` (`tikz`, com fallback armado).

---

## `HANDOFF_GATE.md` — o `gate` -- conteudo e ordem dos slides

# HANDOFF_GATE.md — para quem assumir o conteúdo da defesa

> **Escrito 2026-08-26, noite, pela sessão `gate`. Defesa: sexta, 28/08, 10:00, remota.**
> Banca: Fabrício A. Silva (orientador/presidente), Clayson S. F. de Sousa Celes (ITA, externo),
> Alex Borges.
>
> **Quem aprova é o autor.** Não existe portão com o orientador para a apresentação — decisão dele,
> registrada. Não reintroduza.
>
> **Este documento é o que a minha sessão sabe e os arquivos não dizem.** Os fatos estão no
> `considerations.md`; aqui está o que custou caro descobrir.

---

## 0 · Leia nesta ordem, e pare de ler quando puder agir

| # | arquivo | por quê |
|---|---|---|
| 1 | **este documento, §3** | os erros já cometidos. **É a seção que economiza o seu dia** |
| 2 | [`considerations.md`](considerations.md) **§✔ Decisões do autor** | 18+ decisões dele, com o efeito de cada uma. **Nada ali se reabre** |
| 3 | [`considerations.md`](considerations.md) **§🗺 As três numerações** | o deck tem três numerações em circulação. **Ancore por TÍTULO, sempre** |
| 4 | [`BOAS_PRATICAS_SLIDES.md`](../BOAS_PRATICAS_SLIDES.md) | a referência de forma, escrita pela `ppt`. Medida, não lembrada |
| 5 | [`HANDOFF.md`](HANDOFF.md) **§3** | os sete casos de *"o instrumento passou porque mediu outra coisa"*. Hoje viraram onze |

**A lei da palavra** continua sendo `../WRITING_LAW.md`, `../GLOSSARY.md` (**fail-closed**) e
`../AGENT_GUARDRAILS.md`. **A lei da estrutura** é o `PLANO_FLUXO_DEFESA.md` §8 — **com duas regras
revogadas pelo autor hoje**: a §8.13 (contribuição duas vezes) e a §8.5 (carimbo em arte reproduzida).

---

## 1 · Quem faz o quê

| sessão | escopo | fronteira |
|---|---|---|
| **`gate`** *(esta)* | **conteúdo e estrutura.** O que entra em cada slide, em que ordem, com que palavras. Dono do `considerations.md` e do `SLIDES.md` | **não toca no `slides/main.tex`** |
| **`ppt`** | **implementação.** Única mão no `.tex`. Mede caixa, renderiza, verifica | **não decide conteúdo nem redige ciência** |
| **`tikz`** | **os diagramas.** Entrega `.tex` standalone; a `ppt` integra | **não toca no `main.tex`** |
| *(a definir)* | **a série B (extras)** — 49 páginas. **O autor reservou para outro agente** | ver §6 |
| ~~`presentation`~~ | **desligada.** O histórico dela está absorvido no `considerations.md` §4E | — |

> **A divisão funcionou porque cada um recusou o trabalho do outro.** A `ppt` parou várias vezes
> dizendo *"aqui inventar seria eu escrevendo ciência"*; a `tikz` levou decisões de glossário ao
> `gate` em vez de escolher. **Mantenha isso.**

---

## 2 · Estado, 27/08 ~12:00 — o dia inteiro depois

**Deck: 102 páginas · 48 impressos · 5 `Overfull` na trilha principal (máx 2,3 mm) · Série B em ZERO ·
51 links / 51 alvos · zero órfãos.** Fala: **48:10**.

> ⚠ **Remeça antes de citar.** O deck andou ~15 vezes em 27/08. **E use padrão CURTO ao grepar o
> PDF** — a extração quebra linha no meio de frases, e eu dei um falso alarme hoje procurando
> `"absolute scores are optimistic"` inteiro num texto que a quebra tinha partido.

### O que foi decidido e executado em 27/08

| | |
|---|---|
| **três inversões de ordem** | Fundamentos `5↔6` · Seção 3 `13↔14` · Seção 4 (a arte vai para o fim) — `AUT-21/22/23` |
| **o `Result 1` saiu da trilha** | migrou para a Série B; `Result 2/3` renumerados — `AUT-29` |
| **o último terço mudou de GÊNERO** | 42 · 43 · 45 · 46 · 47 — *"a plateia já não lê, só escuta"* — `AUT-24` |
| **os cinco cortes de fala** | aplicados · **684 palavras · 4:53** — `AUT-30` |
| **a Série B refeita** | 44 faixas de título, todas auditadas por mim · zero `Overfull` |
| **o `1,1 M` de parâmetros** | **resolvido**: era `644.359 + 417.117`, e o primeiro termo é o build defeituoso de 2 camadas. **AL 4,2 vs 1,85 (2,3×) · CA 5,2 vs 2,80 (1,8×)** |
| **`stream`/`tower`** | **revogados pelo autor** depois de os ter autorizado. Nome padronizado = **o nome da tarefa** |

### O que está PRONTO e esperando só a palavra do autor

**As cinco falas curtas** (`S41`–`S44`, os quatro passos do protocolo, e `S46`, o Result 3).
Escritas, entregues à `ppt`, **medidas, NÃO aplicadas**. **As cinco vieram abaixo do alvo** — cortam
**707 palavras**, contra as 598 previstas.

| | antes | depois |
|---|---:|---:|
| os quatro overlays do protocolo | 6:51 | **3:23** |
| o `S46` · Result 3 | 195 s | **99 s** |
| **deck inteiro** | 7.607 palavras · **54:20** | 6.900 palavras · **49:17** |

> 🔴 **A decisão que espera o autor.** Ele **já não escolhe entre "no teto" e "com folga"** — escolhe
> entre **49:17** e algo menor: **−180 palavras** leva a 48:00, **−320** a 47:00.
>
> **49:17 dá 43 segundos de margem**, e continua sendo margem de **leitura corrida** — sem pausa, sem
> hesitação, sem uma frase a mais para responder um olhar. O Art. 23 é **teto, não alvo**.
>
> ⚠ **E há um dado novo que ele não tinha:** as cinco reescritas couberam com **13% de sobra sobre o
> alvo**, o que sugere **gordura da mesma classe** (a fala recitando a tela) em outros blocos.
> ⚠ **Mas só um candidato sobreviveu à remedição: o `S48`** (119 s). O `S30` mede **75 s** contra 100
> declarados e o `S52` mede **78 s** contra 96 — **os campos `Tempo:` deles é que estavam altos, não a
> fala.** Eu os listei como gordura sem remedir.

---

## 3 · 🔴 OS ERROS QUE EU JÁ COMETI

**Leia isto antes de confiar em qualquer coisa que eu escrevi.** Não são deslizes isolados — são
**nove classes**, e cada uma vai voltar. *(Nove classes + seis avulsos = quinze.)*

### Classe 1 · Eu li o meu relatório em vez do artefato

**Três itens sumiram em silêncio.** A frase do Florida no slide dos datasets, a inversão dos itens do
slide 1 e a menção redundante no slide 2 estavam **especificados na §9 e nunca entraram em lote
nenhum**. Pior: **a minha reconciliação da §14 os listou como "na fila"** — eu conferi a spec contra a
minha própria fila em vez de contra o `.tex`. **O autor reclamou duas vezes, e as duas tinha razão.**

> **A regra que decorre:** *"na fila" não é um estado verificável.* Ou está no `.tex`, ou não está.
> **Todo lote que você mandar deve vir com a lista do que ele cobre, e você deve conferir a spec
> inteira contra os lotes despachados antes de dizer que uma seção está coberta.**

### Classe 2 · Eu usei o instrumento errado e reportei o verde dele

**Eu afirmei que `fine class` tinha zero ocorrências no deck.** Rodei `grep 'fine class'` — e **a
fonte quebra a linha entre as duas palavras**. O termo estava vivo em tela. A `ppt` o achou
**renderizando**.

> **Os dois padrões que ficaram, e nenhum substitui o outro:**
> - **auditoria de termo sobre o PDF EXTRAÍDO**, não sobre a fonte — a fonte mente por quebra de linha
>   e por macro;
> - ⚠ **e ela não pega conteúdo ausente**: o PDF só mostra **o que foi desenhado**. Conteúdo empurrado
>   para fora da caixa **não aparece na extração**. **Extrair pega termo errado; renderizar pega
>   conteúdo ausente.**

### Classe 3 · Eu escrevi contra uma sensação em vez de um alvo medido

**Especifiquei "figura + duas linhas" para os slides de diagrama.** Contei "duas linhas" como duas
linhas **físicas**; elas quebravam em **cinco**. **Conteúdo obrigatório caiu da caixa nos dois slides,
sem um aviso no log** — inclusive a ressalva metodológica do HGI, que a §8.6 obriga.

> **O contrato que ficou: eu digo o CONTEÚDO, a `ppt` diz QUANTAS LINHAS ele ocupa.** Nunca especifique
> em linhas. Peça o orçamento em palavras e escreva contra ele.
> **Referência: a 140 ppm, 1 s = 2,33 palavras.**

### Classe 4 · Eu parafraseei texto entregue e introduzi defeito

**Duas vezes no mesmo dia:**
- escrevi a pergunta de pesquisa do slide 3 **com dois travessões dentro de frase completa** —
  violando a regra que eu mesmo estava aplicando. **O texto entregue usa parênteses**
  (`1_introduction.tex:133-134`). A paráfrase não ganhava nada e criava a violação;
- recomendei **substituir a frase do critério do balanceador** por uma descritiva de literatura. O
  defeito real era outro: **o deck tinha cortado o prefixo de escopo `For this dissertation`** do
  texto entregue (`2_fundamentals.tex:1391-1392`). **Restaurar três palavras resolvia** — e elas
  **já estão no deck** (`main.tex:321`).

> **A regra:** quando algo na tela soa errado, **vá ao texto entregue antes de reescrever.** Nove vezes
> em dez o defeito é um corte, não a redação.

### Classe 5 · Eu inventei estrutura sem verificar quem a consome

**Criei os identificadores `S5b` e `S26b`** no `SLIDES.md`. O extrator do roteiro lê `### (S\d+) · ` —
**o sufixo de letra não casa. Duas telas iriam para a defesa sem fala nenhuma**, e uma delas é o slide
das tarefas, que é conteúdo novo. **Zero avisos: a ferramenta não conta o que não viu.**

> 🔴 **E aconteceu de novo no mesmo dia, no mesmo arquivo, com o mesmo consumidor.**
>
> Ao sincronizar as falas eu marquei cada bloco corrigido com um parentético — *"(v3, 26/08 —
> sincronizada com o deck)"* — **dentro do campo `Fala (PT)`**. O extrator lê o campo **inteiro**.
> **Doze blocos** iam para o roteiro impresso com a minha nota de bastidor no meio do que o autor
> lê em voz alta.
>
> **E era invisível dos dois lados que alguém olha:** no `SLIDES.md` a anotação está formatada e
> parece obviamente editorial; no `.tex` ela não existe. **Só aparece no que o extrator produz** — e
> o `SPEECH` estava desatualizado desde a véspera, então ninguém tinha visto.
>
> A `ppt` corrigiu no extrator (tira o editorial, **depois** procura as aspas — nessa ordem, porque
> a minha nota do `S51` tem aspas internas). **Verifiquei por fora: 12 → 0, nenhuma fala vazia.**
> E registrei a convenção no cabeçalho do `SLIDES.md`, porque **o conserto depende dela**: sem
> aspas, o extrator devolve o campo inteiro e o vazamento volta calado.
>
> **A lição é a mesma da Classe 5 e por isso ela está aqui e não nos avulsos:** *toda vez que você
> escreve num campo, pergunte quem mais lê esse campo.* Duas vezes em um dia, no mesmo arquivo.

> ⚠ **E só metade está resolvida.** O regex já aceita sufixo de letra (`build_speech_1_extract.py:30`)
> e o `S5b` resolve. **O `S26b` continua sem número impresso**: o título do bloco traz `(a arte)`, que
> não existe em slide nenhum, e ele não está no `ALIAS` (`:60-66`). **Fica em aberto** — custa pouco
> porque o bloco **não tem fala própria**, mas não está fechado.

### Classe 6 · Eu escrevi um aviso que desligou a verificação certa

**E esta é a mais cara do dia, porque o defeito não estava em nenhum dos dois arquivos: estava na
diferença entre eles.**

No `considerations.md` §4F eu escrevi *"o `% FALA` do `.tex` NÃO é espelho da fala — para medir
sincronia, meça texto de TELA"*. **Sobre contagem de palavras eu estava certo.** Sobre conteúdo, não —
e o aviso autorizava a inferência *"não compare os dois"*, que é exatamente a comparação que faltava.

**Resultado, medido em 26/08: 17 das 50 falas divergiam.** Não por erro de um dos dois lados — por
**edição de um lado só**. E o `SLIDES.md` é a **fonte do `SPEECH`**: nas 17, é a versão dele que sai
pela boca do autor.

**Cinco decisões registradas estavam vivas no roteiro depois de terem morrido no deck** — a "sexta
limitação" que a `AUT-11` matou, o carimbo que a `AUT-5` matou, as janelas que a `C30`/`G5` matou,
o *"e concorda"* do Wilcoxon que não tem proveniência.

🔴 **E na direção contrária, que é pior: duas divulgações de honestidade existiam SÓ no deck** — a
ressalva de vazamento da tarefa estática e a de que o controle de dimensão equalizada **nunca foi
executado**. **Uma regeração do `SPEECH` apagava as duas da fala.**

> **A regra:** antes de regerar o `SPEECH`, rode **`presentation/diff_fala.py`**. Custa segundos.
> ⚠ **Ele pareia por POSIÇÃO, não por título** — dois frames com o mesmo `\frametitle` são dois
> frames. É a terceira vez que esse erro aparece com roupa diferente: **título não é identidade.**
>
> **E a lição maior, que é sobre mim e não sobre a ferramenta:** eu escrevi um aviso verdadeiro
> (*"não conte palavras por ali"*) e ele foi lido como um aviso mais largo (*"não olhe por ali"*).
> **Um aviso que desliga uma verificação precisa dizer o que ele NÃO desliga.**

---

### Classe 11 · Eu pus uma instrução de LAYOUT dentro de uma spec de CONTEÚDO, e o orçamento deixou de prever

**A Classe 3 estabeleceu o contrato: *eu digo o CONTEÚDO, a `ppt` diz QUANTAS LINHAS ele ocupa*, e
o orçamento vai em PALAVRAS. Cumpri o contrato na letra e quebrei-o no espírito.**

No `ITEM B` da rodada de 28/08 especifiquei o par `hard`/`soft` do slide 8 com o cálculo *"a metade
`hard` encolhe de 16 para 10 palavras, o custo líquido é **+8 palavras**"*. **O frame passou de
+0,44 para +27,64 pt.**

**A causa está na minha própria spec:** eu escrevi um `\\` entre as duas metades. Esse `\\` é uma
**instrução de composição**, não conteúdo — força a metade `hard` a passar de 2 linhas para 1 e dá
2 linhas à `soft`. **Duas linhas novas, não oito palavras.**

> **A regra:** o orçamento em palavras só prevê altura enquanto o texto **flui**. No instante em que
> a minha spec contém `\\`, `\vspace`, `minipage`, `columns` ou `tabular`, **eu deixei de
> especificar conteúdo e passei a especificar layout — e o número de palavras deixa de significar
> qualquer coisa.** Nesses casos não estime: mande o conteúdo **sem** a instrução de quebra e deixe
> a decisão de composição com quem mede.

**E a `ppt` devolveu o lado simétrico, que fecha a regra:** ela atravessa a mesma fronteira ao
contrário. Encurtou `Texas category` para `Texas` por parecer redundância de forma — *"isso era
conteúdo com roupa de forma, e passou porque cortes de uma palavra são os mais fáceis de
justificar"*. 🔴 **E eu tentei absolvê-la desse corte, medindo o slide errado.** Procurei `Texas` perto de
valores de `p` no PDF, caí no frame `Capacity control` (faixa `B-P1`, eixo REGIÃO, números
63.446/64.931/64.503) e respondi-lhe *"o teu corte estava certo, não te penalizes"*. **A linha que
ela editou é outra**: está no `V19-2` (`Next category, sealed test`), diz `Texas category is the one
disagreement: −0,13 excluding zero, −0,007 including it`, e os números que eu citei **não existem
nela** — aparecem uma vez cada, no outro frame. **Ela repôs o `category` e tinha razão**, com o meu
próprio argumento: no deck, `Texas` é célebre como ganho de **região** (+1,21), então numa tela de
categoria a palavra nua convida a importar o resultado errado.

> ⚠ **É a quarta aparição de *"título não é identidade"*, e desta vez a minha.** As três anteriores
> estão no §3 e nas regras de medição (o `diff_fala` que pareia por posição; o detector de
> `Overfull` ancorado no `\begin{frame}`; o `grep` que encontrou o **botão do índice** `B-P1` antes
> do frame). **Um padrão que ocorre em vários sítios devolve o PRIMEIRO, não o CERTO** — e o índice
> vem sempre antes. Eu cometi-o **na mensagem seguinte** àquela em que registei a lição dela.
> A âncora correta é o `\framesubtitle` do próprio frame, nunca o rótulo do botão.

> **A formulação dela, que é a melhor que temos:** *"quando a minha alavanca muda **quais palavras
> estão na tela**, ela é tua; quando a tua spec contém uma instrução de composição, o custo é meu
> de medir. **Nenhum dos dois consegue prever o lado do outro.**"*
>
> Os quatro casos de um só dia: `+8 palavras` → **27,6 pt**; a ordem *"corte as caixas 1 e 2"* →
> **zero**; `Texas category` → `Texas`; e o `\vfill` sem par → **o dobro** do estouro.

> 🔴 **A REGRA, medida quatro vezes em 27/08 e sempre a dar zero ou o dobro:** neste deck a unidade
> de custo é a **LINHA**, e linhas são **quantizadas**. **Caracteres não compram nada até removerem
> uma quebra** — a `ppt` mediu que doze citações custam o mesmo em `(2018)` ou em
> `(Kendall et al., 2018)`, porque o que custa é a quebra, não o que a provocou. E em `columns` ou
> `minipage`, **a altura é o MÁXIMO entre as colunas: só a coluna mais alta paga.** Cortar da mais
> curta é trabalho perdido, por mais conteúdo que se sacrifique.
>
> | o que eu previ | o que mediu |
> |---|---|
> | `+8 palavras` | **+27,6 pt** — o `\\` que eu escrevi forçava a quebra |
> | *"corta as caixas 1 e 2 antes da 3"* | **zero** — minipage, altura é o máximo das três |
> | ordem de sacrifício do slide 21 | **zero** — eu ordenei na coluna curta; paga a comprida |
> | `V1, só o ano` no slide 8 | **zero** — idêntico ao autor-ano completo |
>
> **O protocolo que decorre:** eu ordeno por **valor de conteúdo**; a `ppt` diz **qual coluna paga**
> antes de eu ordenar. Nenhum dos dois consegue fazer o do outro.

⚠ **É a segunda vez no mesmo dia.** No `ITEM 6` eu mandei *"corte as caixas 1 e 2 antes da 3"* para
poupar altura numa faixa de minipages — e a `ppt` mediu que **comprou zero**: a altura de uma linha
de minipages é o **máximo** das três, e a caixa 3 tem duas linhas. **A regra que eu apliquei valia
para prosa corrida, e eu apliquei-a a caixas lado a lado.** Nos dois casos o erro é o mesmo:
raciocinar sobre texto quando o objeto na tela já não é texto.

---

### Classe 9 · Eu aceitei a caracterização de um registro em vez de abrir o registro

**A `ppt` descreveu a `V3` como *"os dois termos que a `V3` trocou por Next Category e Next Region"*.
Eu repeti isso em três mensagens, para ela, para a `tikz` e para o autor — e quase mandei editar a
Figura 2 do volume depositado por causa disso.**

**Fui ao registro e a `V3` diz o oposto:** que a família `stream`/`tower` **não estava no
`GLOSSARY`** — *"é buraco do registro, não defeito do deck"* — e a **`AUT-14` do autor AUTORIZOU os
termos**. **Nunca houve troca. Nunca houve defeito.**

> **A caracterização de um registro não é o registro.** Eu passei o dia cobrando isso dos outros —
> *"não conclua de um grep"*, *"vá à fonte"* — e aceitei de segunda mão a descrição de uma decisão
> que estava a três linhas de distância.

⚠ **O que salvou não fui eu:** a `tikz` parou por **outra** razão (a legenda da Figura 2 diz
`(semantic)`/`(spatial)`), e foi essa parada que me obrigou a verificar.

---

### Classe 10 · Eu busquei num escopo que não podia conter a resposta, e li o vazio como ausência

**A `extra` citou `EVALUATION_PROTOCOL.md §10` e §1 para corrigir a linha `Partition` do `V19-1`.
Eu procurei o arquivo, não achei, procurei as strings citadas, não achei — e escrevi ao autor que
"a fonte que ele citou não existe neste repositório".**

**Ela existe.** Vive em `/Users/vitor/Desktop/mestrado/mtlcheck/`, que é **outro repositório**. As
três citações conferem verbatim (`:323-324`, `:331`, `:54`). E o **rodapé do próprio slide já
dizia onde** — `mtlcheck a6639c0a` — enquanto eu procurava em `ingred`.

> **Um `grep` vazio prova que a string não está no escopo, e nada mais.** A Classe 9 diz para abrir
> o registro em vez de aceitar a caracterização; esta diz o inverso e é mais fácil de cometer:
> **antes de declarar que um registro não existe, verificar se você o procurou onde ele viveria.**
> O sinal estava na tela que eu estava a corrigir.

⚠ **O agravante:** eu quase transformei um erro meu de escopo numa acusação de fabricação contra um
par que estava certo. **Reportei a dúvida como dúvida** — e foi só isso que a manteve reparável.
Se eu tivesse reportado como achado, teria queimado o trabalho dela e a correção não teria entrado.

---

### Classe 8 · Eu apliquei o contrato certo a uma cláusula que ele não cobre

**O contrato do dia era:** *nada sai da tela sem estar na fala.* Verifiquei, estava, cortei.
**A cláusula era `"absolute scores are optimistic"`, e o `SLIDES.md:830` registrava desde 24/08 que
ela devia FICAR na tela — com a razão escrita: *"mandá-la para a fala pareceria escondê-la"*.**

**Cobertura pela fala era exatamente o que aquela decisão tinha rejeitado.** Eu não li o bloco antes
de reescrever o slide; li só a fala.

> 🛑 **A exceção, e ela precisa viajar colada ao contrato** *(formulação da `ppt`)*: **para uma
> cláusula AUTOINCRIMINATÓRIA, mandar para a fala não a preserva — muda o que ela significa.**
> Uma ressalva contra si mesmo **dita e não projetada** lê-se como concessão arrancada; **projetada**,
> lê-se como honestidade oferecida. **A `R6` diz o mesmo por outro caminho: a ressalva acompanha o
> resultado.**

**A linha que separa as duas, e ela é o que decide cada caso:** vale para a cláusula que **qualifica
um número que está na tela** — essa desce com o número. Não vale para a que qualifica uma **escolha
de método** sem número associado: essa pode viver na fala e na reserva. *(Foi por isso que o
`"a convenção alternativa é mais favorável"` pôde sair da tela do 36 e o `optimistic` não podia.)*

✅ **Varri a classe inteira no deck depois disso.** A trilha principal mantém **quatro** cláusulas
contra si mesma na tela: `absolute scores are optimistic` · `Not width-matched` · `the evidence does
not separate the contributions of the shared trunk and the private spatial path` · `this chapter does
not isolate each encoder`. **Só uma tinha saído, e voltou.**

### E o protocolo que decorre, que é de mão dupla

- **Meu:** ao especificar reescrita, **leio o bloco do `SLIDES.md`, não só a fala** — é lá que moram
  as decisões sobre *onde* uma coisa tem de viver, e elas não aparecem em varredura de texto;
- **Da `ppt`:** ao devolver *"não cabe, corte N palavras"*, ela não sabe quais linhas estão
  protegidas. **Mando a marca `[INTOCÁVEL]` junto com o texto**, e ela mede contra o resto.

---

### Classe 12 · Eu especifiquei o conserto de uma ALEGAÇÃO para uma superfície só

**Encontrei que o slide 6 afirmava falsamente que todos os modelos nomeados predizem *"the exact
establishment"* — o `HST-LSTM` prediz AOI. Especifiquei tirá-lo da lista. Da TELA.**

**A alegação vivia em três superfícies**, e a `ppt` encontrou as outras duas: a **fala** (*"…ST-RNN,
DeepMove, HST-LSTM, Flashback… **Todos eles predizem o lugar exato**"* — **mais categórica que a
tela, sem hedge nenhum**) e o campo `Na tela:` do `SLIDES.md`. Tirar só da tela **deixaria o autor a
dizer em voz alta exatamente o que a tela acabara de parar de afirmar.**

> **A regra:** remover uma PALAVRA é edição de uma superfície. Remover uma **ALEGAÇÃO** é edição de
> todas as superfícies onde ela é feita. **Quando a spec corrige uma alegação, ela tem de enumerar
> onde a alegação vive** — tela, `% FALA:`, `SLIDES.md`, Série B — e o executor confere as três.

⚠ **É a `Classe 6` outra vez, do outro lado.** Lá eu escrevi um aviso que desligou a comparação
tela↔fala; aqui eu simplesmente não a fiz. **Eu cobro esta varredura da `ppt` desde ontem e não a
apliquei a mim.**

---

### Classe 7 · Eu deixei entrar conteúdo do autor sem validá-lo contra o que a tese entrega

**Apontado por ele, em 27/08, e a formulação é dele:** *"você que é o agente que deveria averiguar e
validar o conteúdo, não averiguou e nem validou o que estava entrando."*

O bloco de trabalho futuro do slide 47 propunha **"a shared trunk with MMoE, or with
cross-attention"**. O `5_mobiwac/04_method.tex:28` descreve o modelo entregue como *"the shared
trunk, **a cross-attention stack** of two blocks"*. **O slide final propunha, como trabalho futuro, a
arquitetura do Capítulo 5.** E "drop the embedding layer" também já estava feito.

**A causa não é desatenção, é PERDA DE ESCOPO na migração.** O item veio da lista crua dele
(`wrapup/Questions_author.md:118`), escrita sobre o **MTLnet do Capítulo 3** — ali "camada embedding"
é o FiLM. Ao entrar na **Conclusão**, virou trabalho futuro da dissertação inteira, e nesse escopo é
falso.

> **A regra:** quando um item do autor migra de um contexto para outro, **o escopo não migra junto —
> ele tem de ser reconstruído.** E a validação certa não é "isto faz sentido?", é **"isto já está
> entregue em algum capítulo?"**
>
> ⚠ **E o que torna isto uma classe e não um deslize:** eu auditei a lista de CONTRIBUIÇÕES dele na
> §13, com cuidado, e **não auditei a de TRABALHOS FUTUROS — que está no mesmo arquivo, quarenta
> linhas abaixo.** Auditar metade de uma fonte e tratar a fonte como auditada.

---

### E mais seis, avulsos, que valem pelo padrão

| erro | lição |
|---|---|
| Incluí o **slide 41 (veredito)** na regra de negrito/sublinhado | **é tabela de VEREDITO, não de placar.** Marcar "melhor" nas células dentro da margem **reintroduz o veredito de vencedor que a lei proíbe**. ⚠ **E eu escrevi depois que "ele não tem negrito" — tem:** `main.tex:1481-1490` marca **as três células que superam com Holm**, e só essas. **Sublinhado: zero. A lição está respeitada; a minha frase estava errada** |
| O meu **mapa de renumeração** estava deslocado, e **o deslocamento não era uniforme** — quatro faixas | **ancore por título.** O número é derivado e muda a cada remoção |
| Descrevi a **`fig1_dataflow` original** como se fosse a chapa nova, criando um dilema inexistente | **verifique o artefato de que está falando**, não a memória dele |
| Marquei a remoção da linha de `Controls` como **"risco de esconder"** | os números eram **pré-vazamento** e a frase presa a eles é **aritmeticamente falsa** contra a Tabela 9. **Remover era corrigir** |
| Repeti o **`+4:00`** da `ppt` sem somar a tabela dela (era `+2:36`) | **confira o número do par também.** Ela confere os meus o dia inteiro |
| Não vi que **o desenho do HGI do autor estava no `considerations.md`**, destruído por um formatador | procurei "HGI", vi texto colapsado e **descartei sem ler**. Ele teve de me dizer duas vezes |

---

### O padrão por trás das seis classes, formulado pela `ppt` melhor do que eu formulei

> *"Você escreveu num campo sem perguntar quem mais o lê; eu li um campo sem perguntar quem mais
> escreve nele."*

**Três defeitos do dia moram na FRONTEIRA entre dois artefatos, e nos três cada lado estava certo
sozinho:**

| o defeito | lado A | lado B | onde estava o erro |
|---|---|---|---|
| a ressalva de vazamento | correta no deck | ausente no `SLIDES.md` | **existia só em um** |
| a minha anotação de versão | legítima no `SLIDES.md` | inexistente no `.tex` | **no que o extrator fazia com ela** |
| `S5b` / `S26b` | códigos válidos | regex do extrator | **ninguém perguntou ao consumidor** |

> **A varredura que decorre, e ela é a que faltava o dia inteiro:** para cada artefato que você
> escreve, liste **quem mais o lê** e **quem mais escreve nele**. O defeito raramente está no
> arquivo; está no que o vizinho supõe sobre ele.

### E duas regras sobre COMO medir, que custaram um defeito cada

**1 · Um teste que injeta um defeito tem de provar que injetou.** A `ppt` testou um guarda copiando
o `SLIDES.md` para um sandbox, injetando a marca e rodando o extrator. **Passou.** Não disparou
porque o `re.sub` **não casou** — o arquivo saiu byte-idêntico ao original. Só o md5 denunciou.
**Ela estava medindo um guarda contra um alvo intacto e lendo o verde como resultado.**

**2 · Uma invariante medida em zero precisa de um segundo número que prove que o caso ocorre.** Eu
propus um guarda apoiado em *"nenhuma das 56 falas extraídas tem crase — 0/56"*. **Ela mediu o
campo BRUTO também: 3/56.** É esse 3 que transforma o zero em evidência — sem ele, o `0` não
distingue *"a limpeza funciona"* de *"nunca houve o que limpar"*, e o guarda podia estar guardando
uma porta que ninguém usa.

**3 · Uma âncora errada não erra às vezes — erra sempre, e sempre para verde.** A `ppt` verificava
`Overfull` com `grep "detected at line $n"`, com `$n` = a linha do **`\begin{frame}`**. **O LaTeX
reporta o estouro na linha do `\end{frame}`.** O grep nunca achava nada, para frame nenhum, nunca —
e cada "✔ sem `Overfull`" do dia consultava uma linha onde nada seria reportado. **Um instrumento que
erra às vezes te avisa; um que responde "limpo" a tudo parece funcionar para sempre.** A correção é a
mesma de sempre: **atribuir por INTERVALO `[begin, end]`, não por linha de abertura.**

**3b · `grep -o` destrói adjacência, e a saída parece uma frase.** A `extra` mandou-me, como
verbatim do Apêndice E, *"The region head deliberately keeps two routes. The **private route** reads
the raw 9×64 region history."* **A linha diz `private tower`.** Ela tinha rodado
`grep -o 'two routes[^.]*\.\|private route[^.]*\.'`, e o `-o` devolveu **duas linhas de saída
separadas** — de sítios diferentes do ficheiro, uma delas de uma legenda de figura 44 linhas antes.
**Ela costurou-as numa frase e atribuiu a uma linha.**

> **`-o` remove o contexto E o número de linha. Adjacência na SAÍDA não é adjacência no TEXTO.**
> Para extrair citação, use `grep -n` com a linha inteira, ou `sed -n 'N,Mp'`, e leia o que está à
> volta. **Nunca componha uma citação a partir de dois fragmentos de saída.**

⚠ **Esta é de espécie pior do que as outras quatro do dia.** Truncagem, substring, escopo de árvore
e âncora ambígua fazem **falhar em ver** ou **ver de mais**. Esta **produz evidência que não existe**
— num projeto cuja lei é *"copiado da célula, nunca re-derivado"*. E chegava à conclusão certa, o que
é exatamente o que faz ninguém voltar a verificar. **A regra que fica, e vale para os dois lados:
uma citação errada que chega à conclusão certa é o caso mais perigoso.**

**4 · Não leia um log que ainda está sendo escrito.** Duas leituras de `build/main.log` durante o
`make` devolveram **`0 Overfull`** — num log pela metade não há o que achar, então o zero não diz
nada. **Sintoma diagnosticável: `main.log` com mtime MAIS NOVO que `main.pdf` significa build em
curso.** Espere `pgrep xetex` esvaziar e o mtime parar.

**5 · Um controle que você escolheu depois da conclusão não é controle.** A `ppt` mediu que os slides
que o autor chamou de "textuais demais" tinham 6–23 palavras por unidade contra **3–4** dos que ele
não citou — linha limpa, medições individuais todas corretas. **Fui medir os 49 e a linha não
existe:** três dos quatro citados estão **na mediana ou abaixo** (o `43` é dos mais magros do deck), e
os seis mais pesados **não foram citados**. O controle dela eram quatro slides que ela escolheu — os
quatro de **tabela de números**. Contra 3 palavras por célula, qualquer slide de prosa parece fora da
curva. Nas palavras dela: *"eu não escolhi o controle, eu escolhi a conclusão e fui buscar o controle
que a produzia."*

> ⚠ **A defesa desta é diferente das quatro acima, e é por isso que ela é a mais perigosa.** Contra
> falso verde a pergunta é *o vermelho era possível?*. **Contra amostra enviesada não há pergunta que
> salve** — só **medir a população inteira antes de traçar a linha**. Ela traçou com nove de
> quarenta e nove.

> **As cinco dizem a mesma coisa: um verde só vale se você provar que o vermelho tinha por onde
> aparecer — e que você não escolheu onde olhar depois de saber o que queria ver.**

**6 · Um lote parcialmente liberado cria estados que ninguém desenhou.** O `B6-6` ficou, no PDF de
27/08, com a **faixa nova** (lote 2, liberado) e a **linha velha do corpo** (lote 3+, bloqueado) na
**mesma página** — e a faixa existia justamente para corrigir a linha. **O slide passou a afirmar e
refutar na mesma respiração, o que é pior que o defeito original**, que ao menos era coerente
consigo mesmo.

> **Ao cortar trabalho em lotes, pergunte o que cada fronteira deixa VISÍVEL ao mesmo tempo.**
> O teste: *a afirmação da faixa contradiz alguma linha do corpo?*

### E um padrão de caixa que vale antes de qualquer corte de texto

🔧 **Quando faltam poucos pontos, procure o AMBIENTE antes de procurar a palavra.** Três casos medidos
em 26/08: a moldura do `block` (**~28 pt**), o `\begin{center}` (**8 pt**, e ele cobra `\topsep` dos
dois lados), o `itemize` de **um** item (**~6 pt** de `topsep`+`partopsep`, sem ganhar nada). **Somados,
42 pt — mais que o pior estouro do deck inteiro.**

> 🛑 **E aqui eu escrevi uma consequência ERRADA, corrigida pela `ppt` na mesma hora. Deixo o erro à
> vista porque ele é fácil de repetir.**
>
> Eu escrevi: *"antes de eu especificar corte de conteúdo num slide apertado, varra o ambiente —
> talvez não precise cortar nada."* **Isso confunde três orçamentos que não se convertem:**
>
> | orçamento | unidade | o cromo devolve |
> |---|---|---|
> | **o relógio** (49:17 contra 50 min) | **palavras de FALA** | **nada.** O autor lê o mesmo texto |
> | **a tela cheia demais** (o que o autor pediu) | **palavras na TELA** | **nada.** 8 pt de padding a menos não fazem cinco linhas de prosa virarem âncora |
> | **o `Overfull`** | **pontos de altura** | **isto sim** |
>
> **O cromo compra pontos de página, e só.** As 707 palavras das cinco reescritas continuam
> necessárias inteiras para levar 54:20 a 49:17, e um slide que o autor chama de "excessivamente
> textual" continua textual depois de trocar `center` por `makebox`.
>
> **O padrão do ambiente vale — mas só contra `Overfull`.** Não o ofereça como alternativa a cortar
> texto.

---

## 4 · O que eu estava fazendo quando parei

**A `ppt` executa; eu escrevo e verifico.** Enquanto ela trabalha no `.tex`, o meu trabalho é:

1. **🔴 As cinco falas curtas** — escritas, entregues, **seguradas até o autor decidir o corte**. Ver §2;
2. **As falas de categoria B** — nove blocos em que a fala descreve outra estrutura (itens que viraram
   tabela, blocos que sumiram) **mas nada de errado seria DITO**. Custa fluência, não credibilidade.
   **É a única fila minha que sobrou, e é opcional**;
3. ✅ **Re-auditoria feita às 20:30, com o deck estável** (105 pp · as duas chapas sem `Overfull`).
   A de 18:07 tinha rodado sobre um arquivo que mudou seis vezes durante a corrida. **A nova está
   limpa**, e o que ela conferiu está logo abaixo;
4. ✅ **A sincronia `.tex` ↔ `SLIDES.md`** — **16 das 17 fechadas em 26/08.** Sobra o **`S46`**, que eu
   segurei de propósito: é uma das cinco falas reescritas, e sincronizar antes da decisão do autor
   seria escrever por cima da reescrita. **Ver a Classe 6.**

### A re-auditoria de conteúdo, 26/08 20:30 — o que foi conferido e o que passou

Sobre o texto de tela extraído do `main.pdf` estável (13.419 palavras).

| o que | resultado |
|---|---|
| **`outperforms`** | **3 ocorrências, as três legítimas**: a meta-frase que declara a própria lei, o cabeçalho da tabela de veredito marcando **só as três células que sobrevivem a Holm**, e uma da reserva |
| **`match` / `ties`** (21 no total) | **nenhuma é verbo de veredito.** São `matched folds`, `capacity-matched`, `width-matched`, a frase anti-match do capítulo (*"A claimed gain and a claimed match require different tests"*) e **duas que ENFORÇAM a lei** (*"deficits, not ties"*, *"None of them is a tie"*) |
| **`venue`** | 2, as duas `venue-type feature`, **verbatim de `4_courb.tex:42`** — ver §7B item 2 |
| **`novelty`** | 1, **verbatim de `5_mobiwac/02_related.tex:71`**, e a `WRITING_LAW.md:277` diz explicitamente *"do not over-ban: robust, novel, framework…"* |
| **`next place`** | 7, e **todas necessárias**: o deck tem de nomear o que ele NÃO prediz |
| `AUT-5` carimbos | **0 na tela** ✓ |
| `AUT-11` task-pair confound | **0** ✓ |
| `AUT-12` `Contrastive infomax` | **1** ✓ |
| `AUT-13` linha `Controls` | **0** ✓ |
| `AUT-2` `Contributions` como título | **1 cópia** na trilha principal ✓ |
| `AUT-6` `POI-RGNN` · `ReHDM` | presentes ✓ |
| `AUT-17` `Category Classification` | presente ✓ |
| ✅ `AUT-18` **slide 30** | **FEITO às 20:40** — só a imagem, `Overfull` zero. ⚠ **e eu errei ao dizer que dependia do gênero da figura**: a `fig1_dataflow` estava sendo exibida **pela metade** (`width=0.50\textwidth`), e tirados os marcadores ela entra no tamanho natural e fica legível. **O gênero segue aberto e não bloqueia nada** |

**Nenhum achado novo, e a `AUT-18` fechou logo depois. Nenhuma decisão registrada continua pendente na tela.**

---

**Nada mais está esperando em mim.** A especificação inteira foi despachada em seis lotes e executada.

---

## 5 · Os padrões que valem mais que os itens

**Anotados porque cada um custou pelo menos um defeito hoje.**

- **O contêiner custa mais que o conteúdo.** A moldura de um `exampleblock` custa **~28 pt** sem
  carregar texto nenhum; um `\begin{center}` é uma `trivlist` e cobra `\topsep` **dos dois lados**,
  **8 pt de graça**. **Quando um slide estoura por poucos pontos, examine a moldura antes do conteúdo.**
- **Um guarda que parece folga vai ser removido por quem estiver otimizando folga — inclusive por quem
  o pôs.** O guarda tem de **se declarar**. *(`\begin{frame}{título}{grupo}` é sintaxe válida: abrir o
  corpo com uma chave joga o conteúdo para dentro da faixa do título, com log limpo. Aconteceu três
  vezes hoje.)*
- **Validar o preview não é validar a entrega.** A `tikz` revisou onze rodadas no render do beamer
  enquanto o PDF que ia entregar saía em fonte serifada. **É a mesma classe do `src_fix/`**, que rodou
  nove dias de portões verdes sobre a árvore errada.
- **Um número certo com uma tabela errada é o pior artefato possível** — o total confere e ninguém
  desconfia da linha. Aconteceu na medição do relógio: **7.607 palavras estáveis nas três versões, e a
  atribuição por bloco só ficou certa na terceira.**
- **Meça, não estime.** Três sessões cometeram o mesmo erro hoje, de ângulos diferentes: largura de
  célula, largura de palavra, e a minha fila. **Uma estimativa bem fundamentada é mais difícil de
  contestar que um erro de execução.**
- **O que a tela precisa carregar sozinho tem prioridade de corpo sobre o que a fala carrega junto.**
  ⚠ **Ela decide corpo entre dois elementos obrigatórios; NÃO decide o que sai da tela.** Para isso
  vale o protocolo do `HANDOFF` §4c: **localizar a cláusula no destino ANTES de removê-la.**
- **Quando um termo está numa lista fail-closed e a defesa dele depende de uma distinção sutil, o termo
  sai** — explicá-la ao vivo custa mais do que ela vale.

---

## 6 · O que está aberto, e de quem é

| item | dono | nota |
|---|---|---|
| **O corte da fala** | **autor** | as cinco falas estão prontas com a `ppt`, medidas e **não aplicadas**. Escolha: **49:17** como está · **48:00** (−180 palavras) · **47:00** (−320) |
| ~~O slide 30 · Check2HGI~~ ✅ **FECHADO 26/08** — só a imagem, no tamanho natural | — | escolher o **gênero** da figura: *fluxo de dados* (a chapa existe, mostra os quatro andares, o check-in marcado e as duas saídas) ou *fluxo de treino* (irmã da chapa do HGI). **Nos dois casos o slide fica sem marcador.** A `ppt` deixou `graphicspath` e `.gitignore` prontos: **é edição de dois minutos** |
| **As duas divergências dos diagramas** | **autor** | a `tikz` desenhou **contra o pedido literal dele**, com a evidência no cabeçalho de cada `.tex` (`figures/src/dgi_flow.tex:18-24`). ⚠ **as duas estão CERTAS** — verifiquei no código e na descrição escrita por ele. 🛑 **NÃO as chame de `Q7`/`Q8`**: esses são rótulos da `tikz`, e colidem com as perguntas `Q7`/`Q8` do `considerations.md` §8, que são **outras** e já estão fechadas pela `AUT-3` |
| ~~A chapa do HGI~~ | — | ✅ **INTEGRADA** (`main.tex:759`), renderiza no impresso **22**. ⚠ eu a dei como pendente e não estava. Sobra só corrigir `figures/src/hgi_flow.tex:2`, que diz "impresso 23" |
| **A série B (49 páginas)** | *(outro agente)* | ver abaixo |
| **Regerar o `SPEECH`** | `ppt` | ⚠ **só depois** que a fila de falas fechar. Ordem: `SLIDES.md` → reconstruir o deck → regerar. ⚠⚠ **e o `SLIDES.md` carregava dois defeitos JÁ corrigidos no deck** — a linha *"Florida appears twice"* e o termo `fine class`. **Corrigidos em 26/08.** Se aparecer outro, **corrija no `SLIDES.md` ANTES de regerar**, senão o roteiro ressuscita o que o deck já enterrou |

### Para quem assumir a série B

> 🛑 **PROCURE PELO TEXTO, NÃO PELA LINHA.** Eu tinha escrito 2362 / 2067 / 2310 aqui. Quando fui
> reconferir, **na mesma noite**, os três estavam em **2289 / 1994 / 2244** — o deck andou 60 linhas
> debaixo da citação. **Toda linha da série B neste handoff é chute.** Use `grep -n` pela frase.

**Dois defeitos registrados e não executados**, porque o autor a reservou:
- **`inferential unit`** — `grep -n 'inferential unit' slides/main.tex`. **Termo que não existe no
  documento entregue.** §8.11 é fail-closed e **não distingue trilha principal de reserva**;
- **`Reported alongside, and it agrees`** — `grep -n 'and it agrees' slides/main.tex`, o slide
  `B1-4`. **Afirmação sem proveniência.** O Cap. 5 registra o Wilcoxon como sensibilidade no setup e
  **nunca reporta o resultado**. Grep em `06_results.tex` e `07_discussion.tex`: **zero ocorrências.**

🛑 **E uma coisa que NÃO pode ser "atualizada por consistência":** o slide que diz
*"**Submitted paper**, p. 9, limit 4 of 5"*. **Ali `submitted paper` não é status — é o NOME DE UM
ARTEFATO**, a versão submetida do manuscrito, cuja lista de limites **difere da da dissertação**. É
essa distinção que o slide existe para fazer. **O artigo foi aceito; esta linha continua `submitted`.**

---

## 7 · Cinco fatos que você vai precisar e que não estão em lugar óbvio

1. **O artigo do Cap. 5 foi ACEITO no MobiWac**, em 26/08. Está em três lugares do deck (slide 4, a
   nota do 27 e a fala do divisor). ⚠ **O volume entregue diz *submitted / under review* em CINCO
   lugares** — `tables/frame/lineage.tex:8`, `1_introduction.tex:168`, **`:342`**, `:376`,
   `5_mobiwac.tex:29`. ⚠ **eu tinha escrito quatro e o `:342` ficaria para trás numa errata** — por isso a nota carrega *"after the dissertation was deposited"*. **Sem essa ressalva,
   um arguidor lê `accepted` na tela e `under review` no volume e pergunta qual vale.**
   ⚠ **Provável errata para o depósito final** — não é escopo do `gate`, mas ninguém vai lembrar
   depois de sexta.
2. **A dissertação usa intervalo de confiança de 90%**, não 95% (`05_setup.tex:115`,
   `06_results.tex:208`). O slide do veredito rotulava **95%** — **em duas metades da mesma linha**,
   região e categoria. Corrigido. **Se voltar, é erro factual no slide que decide a defesa.**
3. **O piso de Markov de região está ACIMA dos três sistemas externos publicados** na maioria dos
   conjuntos — **acima do HMT-GRN nos seis**. **É o achado mais forte do Cap. 5 e ninguém o tinha
   dito assim.** Substituiu *"superamos a literatura"*, que superafirmava duas vezes.
4. **O termo `venue` é banido** como sinônimo de lugar (`GLOSSARY.md:84`). **Exceção única:
   `venue-type feature`**, que é verbatim do Cap. 4 e nomeia uma **coluna de dados**.
5. **`category classification` é o termo da Def. 2.6** — **não** *"categorical classification"*. A
   §8.11 é fail-closed.

---

## 7B · ⚠ O que uma verificação independente NÃO conseguiu confirmar

**Este handoff foi verificado por três agentes contra os artefatos, e eles acharam 17 afirmações
erradas minhas — todas corrigidas acima.** Mas cinco coisas ficaram **não verificáveis**, e quem
assumir precisa saber quais:

1. 🔴 **O total de palavras da fala.** Eu contei **7.898**; a `ppt` contou **7.607**. **Fui atrás da
   diferença: 347 tokens são NOTAS DE PROJETO dentro dos blocos de comentário** — avisos, datas, `⚠`
   — que a minha contagem ingênua somou como fala. **A da `ppt` está certa.** ⚠ **Mas o número não
   reproduz de nenhuma fonte sozinha**: o `SLIDES.md` bruto dá 8.691 e o `main.tex` dá 12.968 (que
   inclui a série B). **Todo o cálculo do relógio repousa nesse total. Se for remedir, declare o
   método.**
2. ✅ **FECHADO em 26/08 — a exceção `venue-type feature` tem fonte, e ela é forte.** Eu tinha
   registrado isto como "afirmação minha, não regra escrita". **Fui ao volume: é verbatim.**
   `src/chapters/4_courb.tex:42` traz a frase inteira que o deck reproduz — *"the venue-type feature
   maps one-to-one onto the seven top-level categories"* — dentro da própria ressalva de vazamento do
   capítulo. **A regra fail-closed governa termo que NÓS introduzimos, não texto reproduzido.**
   As duas ocorrências do deck (impresso 29 e a reserva) são a mesma frase do capítulo.
3. **A quebra de linha do `fine class`** não é mais verificável: o defeito foi corrigido, e o grep dá
   zero em toda a história commitada. **A evidência é de segunda mão.**
4. **As medições de render** (`exampleblock` ~28 pt, `center` 8 pt dos dois lados) vêm dos relatórios
   da `ppt`, não de medição minha.
5. **Os auto-relatos de sessão** — quantas rodadas, quem parou quando. **Trate como narrativa.**

---

## 8 · A armadilha final, e é a mais barata de evitar

**Quando o corpo de um slide muda, TRÊS textos envelhecem em silêncio junto com ele: o título, a
fala e a proveniência.** Nenhum dos três dispara `Overfull`, nenhum aparece no render, e o único que
alguém relê é o corpo.

O slide 3 passou o dia inteiro chamado **`The question, and the answer in one line`** — **depois que a
resposta foi removida dele.** Nem eu, nem a `ppt`, nem uma auditoria de quatro agentes pegou. **Todos
verificaram o corpo.**

**E aconteceu de novo no MESMO slide, horas depois.** A pergunta de pesquisa perdeu o parêntese
(`AUT-19`) e entrou na tela corretamente. **O bloco `% FALA:` logo acima continuou recitando a versão
velha** — a tela dizia *next-category and next-region prediction* e a boca ia dizer *point-of-interest
prediction*, o termo exato que a edição existiu para tirar. **Peguei por acaso, olhando o frame por
outro motivo.**

> **Acrescente à sua varredura, para cada slide que você editar:**
> 1. **o título** ainda descreve o que está na tela?
> 2. **o `% FALA:`** ainda diz o que a tela diz? *(a fala é o que sai da boca na frente da banca)*
> 3. **a proveniência** ainda aponta para a linha de onde o texto novo veio?
>
> E o mesmo trio no `SLIDES.md`, que é a fonte do `SPEECH` — corrigir só o `.tex` deixa o roteiro
> ressuscitar a versão velha na próxima regeração.

⚠ **E uma correção ao que eu tinha escrito aqui.** Eu afirmei que os `\specialframe` **não têm
`\frametitle`**. **Falso em três dos cinco:** `{The question}`, `{Closing}` e `{Obrigado}` têm título
e **são alcançados pelo extrator**. **Só dois não têm** — as duas transições internas, nas linhas 683
e 942.

**A lição sobrevive, e é sobre esses dois:** um frame sem `\frametitle` **não é alcançável pelo
extrator**, e **o texto dele só se confere lendo o corpo**. Foi assim que um cartão do roteiro ficou
com o título velho por horas.
