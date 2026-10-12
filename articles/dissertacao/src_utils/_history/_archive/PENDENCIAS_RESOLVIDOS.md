# Itens RESOLVIDOS do PENDENCIAS.md — log de encerramento

Movidos para fora do `PENDENCIAS.md` em 2026-07-27, a pedido do autor, para que aquele arquivo carregue
**apenas o que ainda depende dele**. Nada foi apagado: cada item abaixo mantem a decisao, o que foi
aplicado e o commit. Serve para nao reabrir o que ja foi fechado.

| Onde vive o que ainda esta aberto |
|---|
| `src_utils/PENDENCIAS.md` — o registro vivo |
| `src_utils/codex_reviewer.md` — a revisao externa, com veredito por achado |

---

### ~~2.1 Etica e governanca de dados — **o item mais exposto da lista** (REV-026)~~ — RESOLVIDO 2026-07-27

**Feito, mas precisa da sua leitura.** O Apendice E ("Data ethics and governance", ~790 palavras)
esta escrito e no build. Todas as licencas foram reabertas na fonte nesta sessao, nao herdadas da nota: Figshare devolve
**CC0** para o DOI `10.6084/m9.figshare.22126586.v2`, o Hugging Face devolve **apache-2.0**, e a API do GitHub devolve
SPDX **Apache-2.0**.

Duas coisas que o apendice diz porque o codigo diz, e que voce deve querer conferir:

1. Uma busca no repositorio inteiro por `jitter|perturb|laplace|anonym|deidentif|mask|obfusc` nao retorna **nenhum** hit
   em nenhum caminho de ETL. O apendice afirma que **nao ha de-identificacao aplicada**, em vez de sugerir uma protecao
   que nao existe.
2. O endereco original do Gowalla nao da mais 403: hoje ele **redireciona (301) para um dominio comercial sem relacao**.
   Os termos originais nao estao apenas nao lidos, sumiram.

Sobre o comite de etica, respondendo a sua pergunta 1: a dissertacao de 2024 do mesmo orientador foi extraida inteira
(96 paginas) e buscada por `comite|CAAE|Plataforma Brasil|CEP|IRB|ethics
approval|Resolucao N` — **zero hits**, contra dois hits em "Ethical Statement" que provam que a busca estava lendo texto
real. Ela tem um §2.6 sobre privacidade de localizacao que diz que latitude e longitude ficaram sem mascara. O apendice
registra isso como precedente, registra a sua posicao de que a revisao nao era exigida, e **nao afirma aprovacao nem
isencao**.

**O que preciso de voce:** ler o Apendice E e assinar. Ele faz afirmacoes institucionais em seu nome. Esta marcado
`[NEEDS SIGN-OFF: AUTHOR]`. Commit `9e2b5157`.

> DECISAO: Ficou bem legal, é eu aprovo esse appendix com algumas alterações. Primeramente é mais critical: O gowalla
> orignal, salvo engano é o: https://snap.stanford.edu/data/loc-gowalla.html, o link do figshare que não está
> funcionando
> é acesseivvel por: https://web.archive.org/web/20220709062539/http://www.yongliu.org/datasets.html. Assim, vamos
> refazer o texto do gowalla e ser mais susinto e direto, não precisamos falar de coisas que são efemeras como o fato do
> site não está funcionando. O segundo paragrafo desse appendix que tmb está relacionado ao gowalla, tmb está um pouco
> confuso. Voce pode remover por completo o E.3, não precisamos dessa justificativa por hora.

---

### ~~2.3 Conflito: Nash x NORTH_STAR (REV-005)~~ — RESOLVIDO 2026-07-27

Sua opcao A aplicada. O `NORTH_STAR.md` marca a instrucao "Nash-MTL caveat as in Ch.3" como **REVOGADA**
com a sua decisao, a data e o escopo que ela abre mao (so a alegacao de preferencia de otimizador).
Verificado que nenhum capitulo de moldura amplifica a preferencia. Commit `e8974e81`.

---

### ~~2.4 PCGrad e a largura do sweep (REV-011)~~ — RESOLVIDO 2026-07-27

Seu apontamento para `docs/studies/` rendeu: o `T4_full_screen.json` tem **19 balanceadores** em dois
estados, nao dois. O Cap. 5 agora declara o numero e nomeia as **duas** excecoes (nash_mtl +0,68 e
scale_norm +0,19 em categoria no AL) com o que cada uma abre mao, em vez de "nenhum dos que testamos".
PCGrad fica nomeado, como voce pediu. Commits `e8974e81`, `bff15ed3`.

---

### ~~1b.1 A atribuicao do ganho: "shared trunk" nao se sustenta (persona 10, BLOCKER)~~ — RESOLVIDO 2026-07-27

**Aplicado nos dois capitulos, e a sua desconfianca sobre o experimento estava certa.**

Voce pediu para auditar o F50 antes de cita-lo. Auditei, e ele nao sustenta o que a tese dizia, por dois motivos
independentes que estao no proprio registro:

1. O `F50_T1_5_CROSSATTN_ABSORPTION.md:229` chama o **proprio** nulo de "misleading" e de "hidden compensation effect,
   not a true null contribution". O F49 companheiro mede a contribuicao arquitetural em **-16,16 pp**: o nulo aparece
   porque o encoder de categoria absorve o deficit.
2. A configuracao ablacionada nao e a que foi entregue. O F50 rodou `check2hgi/florida` em bs2048 (abril); o board
   entregue roda `check2hgi_dk_ovl` em bs8192 (`catx_v17_n20/*.json`, campo
   `rundir`). E o mecanismo depende do prior `alpha*log_T`, que o proprio Cap. 5 diz que **nossos modelos nao usam**.

Os dois capitulos agora mantem o valor e **estreitam a inferencia**: a ablacao nao e oferecida como prova de que o trunk
nao contribui. A atribuicao continua retida, e continua apoiada no controle de congelamento e no controle de capacidade,
que este achado nao toca. Commit `06b64cab`.

**Nao rodei de novo, de proposito.** Uma versao citavel exige o engine entregue, o batch entregue, sem o prior, e seeds
suficientes: um treino por seed por fold por braco na GPU, nao uma sonda. Isso e uma pergunta de pesquisa, nao uma
clausula de hedge.

**O que preciso de voce:** (a) o texto reescrito entra como esta, ou (b) voce prefere remover a clausula inteira, ja que
a atribuicao ja fica retida pelos outros dois controles? E: isso merece linha de errata no Apendice B? E texto de
moldura, nao publicado, entao a minha leitura e que nao precisa — mas reescreve uma frase de interpretacao, e a decisao
e sua.

> DECISAO: Vamos lá eu acredito que valha a pena remover essa clausula, para não gerar confusão no leitor, e em
> sequencia documentar esse problema para que em um estudo externo façamos essa analise até agosto, para que caso seja
> objeto de pergunta já tenhamos resposta, esse estudo por hora pode ser documetno em um arquivo md na pasta
> articles/[mobiwac]/science. Mas, como eu disse por hora eu acredito que valha remover isso do cap. 5 e do texto
> original: articles/[mobiwac]. Eu reiterio mais uma vez que ainda podemos alterar no original e evitar erratas, pq o
> mobiwac, aidna esta em etapa de revisão.

---

### ~~1b.2 O piso de Markov esta acima dos baselines externos (persona 11, BLOCKER)~~ — RESOLVIDO 2026-07-27

**Aplicado.** O paragrafo agora declara a assimetria de protocolo sistema por sistema em vez de oferecer uma explicacao
causal unica, e diz explicitamente que nenhum dos fatos estabelece por que o piso fica acima. As contagens verificadas
(piso acima do HMT-GRN em 6/6, do ReHDM em 3, do STAN em 4) e os 22,4 por cento de revisita no Alabama ficam como estao.

Corrigi tambem um erro **meu**, de ontem: eu tinha escrito que os tres sistemas externos preveem um lugar e sao lidos no
nivel de regiao, enquanto o mesmo capitulo chama o HMT-GRN de *region-native*
em `:418`, `:622` e `:755`. Commit `ff96dcaf`. O registro interno estava desatualizado no mesmo ponto e foi corrigido em
`f978b16b`.

---

### ~~2b.1 Apendice A — manter ou remover a secao do BRACIS (era 2.3, e o item mais

consequente)~~ — RESOLVIDO 2026-07-27

Aplicado: a secao A.2 foi removida, e o sweep que voce pediu encontrou e reconciliou as alegacoes dependentes. O
`NORTH_STAR §3`, que mandava manter o dispositivo de contencao, ficou marcado como superado pela sua decisao com a data,
em vez de apagado. A sigla BRACIS saiu da lista de abreviaturas, porque A.2 era o unico texto que a usava. Commit
`21124a8c`.

---

### ~~2b.2 O nome "MTLnet" e a grafia (era 3.7)~~ — RESOLVIDO 2026-07-27

Aplicado: 26 sites normalizados para `MTLnet` no Cap. 4, com a errata no Apendice B. A autoridade e o `GLOSSARY.md:41`,
ja que o artigo do CBIC nunca nomeia o modelo em prosa (so um nome de arquivo de figura e a URL do repositorio). O
`ST-MTLNet` mantem o N maiusculo: e um nome registrado a parte, e a expansao publicada *Spatial-Temporal MTLNet* tambem
fica. A frase do `:84` que dizia que o capitulo preservava a grafia publicada virou falsa com a mudanca e foi removida.
Commit `ff96dcaf`.

---

### ~~3.4 O teto de autocorrelacao — **RECONSTRUIDO nesta rodada** (REV-001)~~ — RESOLVIDO 2026-07-27

**Aplicado, e o nome mudou.** A revisao do codex tem razao: chamar aquilo de "teto" afirma mais do que a analise mostra.
Nao e um limite superior, e o **melhor de quatro preditores especificados**
sobre o historico de rotulos, e um modelo diferente pode supera-lo com o mesmo historico.

O termo agora e **label-history benchmark** no Cap. 5, no Apendice D e no `GLOSSARY.md`, com as formulacoes antigas
banidas no registro. A palavra "teto" continua correta para o *dedicated single-task ceiling*, que e o escore de um
modelo treinado de verdade.

O Apendice D foi reescrito por causa da sua objecao de leitura. Medi antes de reescrever: o texto tinha as **frases mais
curtas do documento** (media 21,2 palavras contra 30,0 na conclusao), entao o tamanho nao era o defeito. Os defeitos
medidos eram (i) colisao de conceitos, "ceiling" 8 vezes contra "reference" 5 em 508 palavras, para um apendice cuja
funcao e justamente separar as duas coisas, e (ii) dependencia externa, "screen" 9 vezes mas definido so no Cap. 5.
Commits `ff96dcaf`
e `21124a8c`.

**O que preciso de voce:** ler o Apendice D novo e dizer se ele agora se sustenta sozinho. Se continuar confuso, a
alternativa e dobra-lo em um paragrafo do Cap. 5, e eu faco.

> DECISAO: __________________________________________________

---

### ~~3.5 Higiene do repositorio, herdada (REV-007)~~ — RESOLVIDO 2026-07-27

Aplicado. (1) Os docstrings do `superiority_wilcoxon.py` e do `m1_stats_n20.py` afirmavam um registro que o
`STATISTICAL_PROTOCOL.md` nao contem: o protocolo fixa a tarefa de regiao em **nao-inferioridade** (`:44`, `:213-215`),
nunca em superioridade. Cada um agora separa o que e registrado (superioridade de categoria) do que e **post-hoc**
(superioridade de regiao), citando as linhas do protocolo. As alegacoes continuam reportadas; so o footing foi
corrigido. Isso ja estava no log como D-4 e nunca tinha sido feito. (2) O `MACS_BOARD_RESULTS.md:47` dizia que o HMT-GRN
supera o piso de Markov. Verifiquei contra os dois pisos: no piso atual o piso esta acima do HMT-GRN em 5 de 5 estados
americanos, e **no piso antigo ja estava acima em 3 de 5** (CA, TX, FL). Ou seja, a alegacao sem qualificacao nunca foi
verdadeira. Os dois pisos agora aparecem tabelados com a janela e a fonte de cada um. Commit `f978b16b`.

## Notas de rodape uteis

- **Ordem de aplicacao**, se voce for reabrir algo: registro fail-closed (GLOSSARY) → governanca → texto de moldura →
  capitulos publicados sob errata → layout → build → revisao. A ordem importa: o layout depende das quebras de pagina
  que o texto move, e o Apendice B so fica correto se escrito **depois** das correcoes que ele declara.
- **Defeitos meus, declarados.** Quatro falhas na minha propria verificacao, todas encontradas pela revisao e nao por
  mim, todas corrigidas: (i) o teste de citacao indefinida reportou "0" enquanto quatro citacoes renderizavam como
  `(??)` nos dois PDFs, porque o grep era ancorado por linha e o LaTeX quebra avisos em varias linhas; (ii) o teste de
  pagina so-com-floats dependia de uma linha de log que o LaTeX nem sempre emite, e reportou "nenhuma" para um build
  cuja p. 71 era so floats; (iii) o commit `2f1cd5b3` registrou "no floats-only page" como verificado quando nao estava
  (a condicao foi de fato corrigida no commit seguinte, `e84b37c0`; deixei o commit como esta, porque reescrever
  historico esconderia o erro); (iv) o script imprimia uma linha para o build final mesmo quando so o de defesa tinha
  rodado, entao duas mensagens de commit citaram numeros do final que ainda nao tinham sido medidos. O verificador agora
  achata o log, le o `.blg`, mede paginas so-com-floats a partir do PDF e reporta so as variantes que aquela execucao
  construiu. A causa raiz das citacoes `(??)` eram arquivos `.aux` velhos **commitados** na raiz do `src/`, que o BibTeX
  le antes do `build/`; foram removidos e entraram no `.gitignore` com o motivo registrado.
- **O que nao esta pendente, embora pareca:** a discrepancia 87/83 x 89/84 de paginas era real e esta corrigida (agora
  94/89 apos as correcoes, medido). As duas violacoes de margem foram eliminadas. As tabelas do Cap. 5 que estavam em 8
  pt agora renderizam em 11,96 pt, tamanho de corpo.

---

## Encerrados na rodada de 2026-07-27 (segunda leva)

### ~~Outros pontos: erratas do MobiWac durante a revisao~~ — APLICADO 2026-07-27

Sua instrucao foi seguida: o artigo esta em revisao, entao correcao menor **nao vira errata** — aplico
no texto original tambem e os dois ficam identicos. Classifiquei as quatro linhas da tabela de errata do
Cap. 5 contra o `[mobiwac]/src/`:

| Correcao | Destino | Por que |
|---|---|---|
| frase dos balanceadores | **os dois textos** (`02_related.tex`) | menor: troca uma alegacao vaga pelo numero real |
| terceira limitacao | **os dois textos** (`07_discussion.tex`) | menor: declara uma consequencia que o artigo ja divulga |
| paragrafo de integridade | **fica errata** | o quarto fundamento cita o Apendice D, que nao cabe no artigo |
| controle de congelamento | **fica errata** | cita a tabela de resultados da dissertacao |

Detalhes que exigiram cuidado: o rotulo `sec:mobiwac:setup-windows` da dissertacao **nao existe** no
artigo, foi remapeado para o `sec:setup-windows` dele, e "this chapter's claims" virou "the paper's
claims". Artigo reconstruido: **9 pp, 0 referencias indefinidas, 0 citacoes indefinidas, 0 erros**.
Registrado no `[mobiwac]/ERRATA.md`. A frase de abertura do Apendice B foi corrigida de quatro para
duas e agora **explica a politica ao leitor**. Seu trabalho nao commitado de 25/07 em `[mobiwac]/` foi
preservado (conferi os mtimes antes de editar).

---

## BLOCO 2 — exposicao cientifica real

---

### ~~1b.3 O custo do Nash-MTL~~ — CORRIGIDO 2026-07-27, um so padrao

Sua razao foi aceita e aplicada: um padrao unico para erro factual. A clausula publicada "requires only
two matrix-vector products per iteration" saiu da frase reproduzida no Cap. 3, com nota de rodape
explicando, e entrou na **tabela de errata do CBIC**, ao lado da correcao de escala de gradiente que fica
na mesma frase publicada. A secao "deliberadamente preservados" caiu de tres para dois elementos.
Isto **supera** a decisao anterior de so declarar. A correcao **aumenta** o custo de um metodo que o
capitulo usou, ou seja, corre contra o interesse da propria dissertacao — e portanto conservadora alem de
consistente. Commit `d1911c0a`.

---

### ~~3.3 Resumo e Abstract: tamanho (REV-018)~~ — **A PAGINA FECHOU** 2026-07-27

Voce escolheu a rota (i), cortar 60 a 80 palavras. Reportei **36 em paridade** (Resumo 565 -> 529,
Abstract 485 -> 452): sairam as duas glosas parenteticas da selecao \emph{joint-best} e a frase de
motivacao foi comprimida.

> **[CORRECAO 2026-07-27]** Aquele "36" nao era so compressao. A edicao **apagou por acidente a
> clausula de abertura de quatro frases**, e a pagina fechou em parte por isso. Restauradas
> (`1bf9a227`), a contagem sobe para 542 / 466, o que separa as duas coisas: **compressao genuina de
> glosa 23 (PT) / 19 (EN)**, **clausulas apagadas 13 (PT) / 14 (EN)**. O documento voltou a 104 pp e a
> p. 4 quase em branco voltou com ele. Ver `PENDENCIAS.md` BLOCO 0c. Cada numero, nome de teste e token de alegacao foi verificado presente nos dois idiomas.

**E foi suficiente: a pagina quase em branco acabou.** 104 -> **103 pp**; o Resumo e suas palavras-chave
dividem a p. 3, o Abstract fica com a p. 4, e a p. 4 saiu inteiramente da lista de paginas com pouco
texto. Nao precisou dos 60 a 80 completos.

**Um defeito meu, e o diagnostico que eu escrevi sobre ele tambem estava errado.** Trocar o
`\needspace` por um `minipage` foi certo, mas o motivo que eu registrei era falso e uma auditoria pegou.
Re-medido nos dois mecanismos, com o Resumo em 529 palavras naquele momento (hoje 544, apos a
restauracao das clausulas) e a macro **corretamente escapada**:

| Mecanismo | Paginas | Onde fica o bloco |
|---|---|---|
| `\needspace{7\onelineskip}` | 104 | **inteiro** na p. 4 (21 palavras, rotulo incluido) |
| `minipage` | **103** | na p. 3, junto do Resumo — a pagina fecha |

Ou seja: o `needspace` **funciona** para manter rotulo e palavras-chave juntos. O que ele nao faz e
**puxar** o bloco para a pagina anterior, porque reserva espaco para as *linhas* seguintes; quando o
bloco nao cabe, ele move o bloco em vez de encaixa-lo. Um `minipage` e uma caixa, entao encaixa.

A afirmacao anterior de que o `needspace` "nunca funcionou em nenhum valor" veio de **um bug meu de
escape**: um regex escreveu `\needspace{N\\onelineskip}` com barra dupla, e as tentativas seguintes
(8, 9, 10) usaram um padrao de barra simples que **nao casava** com a forma corrompida — entao aqueles
tres testes nunca foram aplicados e devolveram resultados identicos byte a byte que eu li como
evidencia. O `minipage` fica (mede melhor), mas por este motivo, nao pelo que eu havia escrito.

**O que ainda e seu:** voce pediu revisores sobre o Resumo e o Abstract para avaliar qualidade e
excelencia contra os exemplares. Vale rodar a persona 15 com esse escopo especifico na proxima rodada,
com os textos ja no tamanho final.

> DECISAO (rodar a persona 15 sobre o par Resumo/Abstract?): __________________________________

---

# Round 6 (2026-07-28) — o §1 inteiro do PENDENCIAS, movido com os commits

**Movido em 2026-07-29 a pedido do autor** (*"parse what has been complete to the
`_history/_archive/PENDENCIAS_RESOLVIDOS.md`, so this file be clean as possible with only the decisions and
important points that I need to take"*). O que esta abaixo saiu de `src_utils/PENDENCIAS.md` §1
palavra por palavra, **com os 19 hashes de commit intactos**, para que a trilha de auditoria
sobreviva a mudanca. Nada foi reescrito, resumido ou reclassificado.

**Como conferir que os hashes ainda resolvem**, do repo root:

```bash
cd /Users/vitor/Desktop/mestrado/ingred
for h in 18b817d9 28097d93 29c7629c 2d117c7a 40ed8e7b 4b609643 4e84cf7a 519de348 6d780b58 \
         6ee23ca7 7a91b720 a7ab2eaa a880632b a8865214 ba90aa6d c6e62c62 e9370222 ec1cea0d fecc7fb1; do
  git cat-file -e "$h^{commit}" 2>/dev/null || echo "MISSING $h"
done; echo "checked 19"
# EXPECT: contains=checked 19
```

Rodado em 2026-07-29: os 19 resolvem, nenhum `MISSING`.

**Uma correcao ao §1 que ele carregava.** O §1 abria com uma tabela de estado do build medida em
`29c7629c` (108/105/109 paginas, `make check` exit 0). Essa tabela ficou no `PENDENCIAS.md`, que e
onde um numero vivo pertence, e foi remedida na rodada 7; o texto abaixo e o registro do que fechou,
nao do estado atual.

## Encerrados na rodada de 2026-07-28 (round 6)

### 1.1 O bloqueador que ninguem viu: o fonte nao compilava

**Fechado em `ba90aa6d`.** De `6d780b58` a `a880632b` a chave de abertura do grupo `{\small ...}` em
`tables/frame/bib_errata.tex` estava ausente e a de fechamento sobreviveu. Todo build morria com
`! Extra }, or forgotten \endgroup`. Seis mensagens de commit reportaram "104/99 pp, 0 overfull, 0
undefined" nesse periodo.

**Por que passou:** os dois caminhos de build discordavam e o que foi acreditado era o cego. O
`Makefile` usa `-halt-on-error` e nao produzia nada; `src_utils/build.sh` roda em
`-interaction=nonstopmode`, onde o pdflatex se recupera do erro e **escreve um PDF completo**, que o
script media e certificava limpo — porque nunca procurava por erros. Agora procura (`tex_errors`), e
o gate foi validado nas duas direcoes antes de ser aceito.

**Registrado em:** `science/AGENT_HANDOFF.md` §2.3b e `AGENT_GUARDRAILS.md` §7 (duas linhas novas de
vies: desconfie da ferramenta que reporta sucesso quando duas discordam; valide todo gate novo contra
uma arvore onde o defeito esta presente).

### 1.2 As decisoes suas que foram aplicadas

| Sua decisao | O que foi feito | Commit |
|---|---|---|
| COD-007: recuperar protocolo de Ch.3/Ch.4 | Eixo de split, seeds e regra de checkpoint recuperados do codigo e dos artefatos de execucao, e adicionados como **adicoes declaradas** com trilha em Apendice B | `519de348`, `a7ab2eaa` |
| COD-002: registrar o que fica fora do texto | [`LEFT_OUT.md`](LEFT_OUT.md) criado, 8 entradas, cada uma com achado, o que o texto diz em vez disso, por que esta fora, e **quem decidiu com data** | `e9370222` |
| 2.2: a tarefa estatica do Ch.4 em Apendice B, "facil de ser comentado" | Secao nova em `chapters/apx_b_static_scope.tex`, incluida por **um** `\input`. Caminho de supressao **testado** em arvore copiada: compila limpo, sem referencia pendente | `28097d93` |
| Split do `main.tex` | `main.tex` = build da defesa; `main_ppgc.tex` = o mesmo PDF **mais** a folha de aceite, em duas linhas de conteudo, para os dois nao divergirem. Terceiro alvo `make ppgc` | `7a91b720` |
| Chapters "corridos": dividir como nos artigos originais | Os tres capitulos de artigo divididos em 18 arquivos por secao, espelhando os nomes de arquivo de cada artigo. Verificado mecanico: camada de texto dos tres builds **identica byte a byte** antes e depois | `4e84cf7a` |
| Resumo/Abstract: cortar e refazer | 500 -> 310 palavras e 423 -> 271, refeitos como par de paridade de 11 sentencas, 19 claims em ambas as linguas | `40ed8e7b` |
| Margens e formatacao local | **Medido, nada a mudar.** Sondei a geometria real compilando uma pagina com o preambulo do documento: 3/2/3/2 cm e entrelinha exatamente 1,500x, todos exatos ao manual §7 | `2d117c7a` |
| Volume de comentarios | **Medido, recomendo nao comprimir.** 1.217 de 1.269 linhas de comentario (95%) carregam um fato rastreavel; as 52 restantes sao banners estruturais e a sua propria fila de sign-off | `2d117c7a` |
| Nomes de exemplo no front matter | **Nao existem.** Todos os campos reais, exceto tres placeholders honestos entre colchetes (dois membros da banca e a data), que e o estado correto | `18b817d9` |

### 1.3 Os defeitos que as revisoes acharam, e que foram corrigidos

Oito trilhas de revisao rodaram sobre o texto desta rodada. Nenhuma tinha visto o que a outra fez.
O que elas acharam:

| ID | Gravidade | O defeito | Commit |
|---|---|---|---|
| N-1 | BLOCKER | O limite "dentro de ±0,003" do cosseno de gradientes e **falso para Alabama** (+0,0032). Criado nesta rodada: o **escopo** da frase foi corrigido de tres para quatro datasets e o limite foi carregado sem reverificar a grandeza que depende do escopo. Corrigido na dissertacao **e** no manuscrito | `fecc7fb1` |
| N-2 | MAJOR | Ch.2 afirmava que Ch.3 "nao identifica o eixo de split", o que a adicao COD-007 desta rodada tornou falso no mesmo dia. O reparo foi **previsto por escrito** e redigido pela trilha de protocolo, e caiu entre dois escopos | `fecc7fb1` |
| D-01 | BLOCKER | Minha propria secao de Apendice B concluia que "o rotulo de um lugar nunca entra na sua propria representacao" no Ch.3. **A premissa e verdadeira e a conclusao nao segue:** o grafo e nao dirigido e a convolucao agrega o no com a vizinhanca, entao o rotulo volta no primeiro salto. Reproduzido em grafo de 4 nos: h_0[Food] = 0,667 contra x_0[Food] = 0,000 | `4b609643` |
| D-02 | BLOCKER | Ch.6 citava o ganho de 20,2 a 22,0 pontos do Ch.4 **sem rotular a tarefa**, como o diagnostico do arco inteiro. O ganho e da tarefa **estatica**, que o Apendice B desta rodada desqualifica. O numero fica (e a figura auditada do capitulo publicado), agora com tarefa e qualificacao, e o diagnostico repousa na tarefa sequencial | `4b609643` |
| F-01 | BLOCKER | **5 de 13** caminhos de reprodutibilidade do Apendice A **nao estao** no branch publico (auditado por CONTEUDO 2026-07-29; a contagem anterior de 9 comparava caminhos, e tres arquivos ja estao publicos sob `analysis_protocol/`) que o Ch.5 aponta em nota de rodape. Todos os 13 existem nesta maquina: a promessa estava errada, nao o codigo. (A primeira contagem dizia 8 de 12; ver `c6e62c62` -- um `grep` por linha perdeu `m1_full_output.txt`, que divide a linha com outro caminho) | `ec1cea0d`, `c6e62c62` |
| F-02 | MAJOR | A pagina 77, secao 6.2, tinha uma sentenca **sem sujeito**: "California run, completed since, repeats the pattern". O artigo "The" terminava a linha anterior e foi absorvido por um bloco de comentario inserido depois. Recuperado do commit original | `ec1cea0d` |
| C-1 | MAJOR | O build de **deposito** (AcademicoPG) imprimia 11 na pagina fisica 8. `\finalbuildfirstpage` estava fixo no offset do build de defesa, e o deposito tem tres paginas pre-textuais menos. Nao conformidade de numeracao no unico build que e depositado | `29c7629c` |
| E-5 | MAJOR | **Dez marcas de nota de rodape eram hyperlinks vivos para a pagina 1** em todos os tres builds. A persona mediu **onde os links caem**, nao apenas se os destinos resolvem. Corrigido com `hyperfootnotes=false` passado em tempo de carga (em `\hypersetup` **nao** funciona: o abntex2 ja carregou o hyperref) | `29c7629c` |
| E-2 | MAJOR | Seis arquivos sem diretiva `% !TeX root`, e depois do split esses seis incluiam os tres masters de capitulo. Segunda instancia na semana. Gate novo `check_tex_root.py` achou **18 outros** | `29c7629c` |
| STY-01 | MAJOR | Sete termos em uso que o registro fail-closed nao tinha, **dois deles em portugues no Resumo** que a minha propria passagem de registro seis horas antes nao cobriu | `a8865214` |
| AIC-01 | MAJOR | A densidade de paralelismo negativo foi **congelada** por uma revisao anterior e esta rodada a levantou de 67 para 79. O diagnostico da persona e o que importa: *"um guard que vive so no relatorio de uma rodada anterior e um guard que ninguem esta checando."* Movido para `check_negative_parallelism.py` | `a8865214` |
| C-6 | MAJOR | **`make check` saiu com codigo 2 durante toda a rodada** enquanto seis commits diziam "all gates pass". Dois falsos positivos ("this article" no apendice de errata, que e correto; "Pareto", que e o termo tecnico). Ambos isentos com a justificativa no lugar | `6ee23ca7` |
| L-9 | MINOR | O Apendice B imprimia "todos os 25 lugares" com uma decomposicao que soma 25 apenas contando um cabecalho de subsecao onde ha dois. Reenumerado: 28 | `6ee23ca7` |
| M-1, M-2 | MAJOR | O Resumo/Abstract perdeu o indice temporal do diagnostico do CoUrb e usava um universal sem escopo ("em todos os estados") cujo antecedente mais proximo e o numero errado de estados. Corrigidos **em paridade** nas duas linguas | `6ee23ca7` |

### 1.4 Gates novos, todos validados nas duas direcoes antes de serem aceitos

| Gate | A classe silenciosa que ele pega | Por que nenhum outro gate a via |
|---|---|---|
| `build.sh` `tex_errors` | O fonte nao compila | `nonstopmode` se recupera e escreve um PDF completo, que o script media |
| `check_doubled_macro.py` | `\\ref{...}` com barra dobrada, que imprime o rotulo cru | O pdflatex nao avisa (as duas metades sao legais) e `undef_ref` fica em 0, corretamente |
| `check_negative_parallelism.py` | Densidade de paralelismo negativo acima do teto | Vivia so num relatorio de revisao |
| `check_tex_root.py` | Diretiva `% !TeX root` ausente ou apontando para arquivo inexistente | Invisivel para o `make`, que le o `main.tex` e nunca olha um comentario magico |

---


---

## Recuperados na varredura de 2026-07-30 (rodada 8)

Itens que sairam do `PENDENCIAS.md` **fechados de forma legitima** — com commit e com marca de
resolucao no titulo — mas que nunca foram copiados para este arquivo. Encontrados varrendo as 63
revisoes do tracker **por titulo**, porque os numeros de item foram reciclados em tres renumeracoes e
uma busca por numero nao os acha.

**Sete candidatos sairam da varredura; a primeira contagem dizia "dois eram perdas reais" e foi escrita
antes de dois dos sete serem medidos.** Corrigido: TRES eram perdas (o italico do Cap. 4 -> 2.20, este
REV-024, e o ponto de terminologia do orientador -> 2.21) e QUATRO estavam resolvidos (determinismo da
categoria -> `apx_b_static_scope.tex`, p.11 do volume extra; cobertura de checkers -> 2.10; rotulos da
figura do Cap. 4 -> `LEFT_OUT` LO-6; escopo da tarefa estatica -> 2.4). Cada um foi re-verificado contra
a arvore viva; o que NAO se sustentou voltou para o `PENDENCIAS.md` em vez de vir para ca.

### ~~Fonte da bibliografia: 12 pt ou `\footnotesize`? (REV-024)~~ — RESOLVIDO 2026-07-27

> **AGORA TEM SONDA, 2026-07-30.** Este item foi arquivado com **uma medicao unica** (o wrapper ausente
> de tres arquivos), que e exatamente o defeito descrito no item 2.19: medicao sem o estado da arvore
> so pode ser re-tomada, nunca re-conferida. Corrigido — `check_audit_claims.py` tem a sonda invertida
> `R8-bibfont`, que **falha** se o `\footnotesize` voltar. Validada por sabotagem: rc=1 com o wrapper
> de volta numa linha viva, rc=0 sem ele.
>
> **Nao estava aqui, e deveria.** Fechado com commit em `63b6ad33` (2026-07-27) e removido do tracker
> sem ser copiado para este arquivo. Reencontrado na varredura de 2026-07-30 e **re-verificado**: o
> wrapper `{\footnotesize ...}` nao existe em nenhum arquivo raiz vivo (`main.tex`, `preamble.tex`,
> `content.tex` -> 0 ocorrencias), entao o fechamento se sustenta.

Aplicado: o wrapper `{\footnotesize ...}` saiu do `0_main.tex` e a bibliografia compoe em 12 pt,
conforme a decisao do autor e o `UFV_COMPLIANCE.md:32`. O `\campus{Campus Florestal}` foi setado e
**nao renderiza** hoje: a macro so e lida dentro de `\imprimircapa`, que nenhum build chama. Passa a
aparecer quando a capa for decidida. Commit `9e2b5157`.



---

## Fechados na rodada 8 e movidos em 2026-07-30

Quinze itens que estavam **de fato fechados** e continuavam ocupando o `PENDENCIAS.md`. Cada um foi
verificado antes de ser movido, e o motivo de saida esta no topo do bloco.

> **CORRECAO DESTE BANNER, 2026-07-30.** A primeira versao dizia que "os nove do §5 estao confirmados
> pelo gate `check_audit_claims.py`". **Sete estao; dois nao tem sonda nenhuma no gate.** As nove
> linhas do gate incluem `NUM-4`, que e outro achado (a varredura do HGI no Cap. 2) e nao corresponde a
> nenhum item movido — ou seja, eu contei nove linhas de saida como nove itens cobertos. Evidencia
> real, item por item:

| item | evidencia |
|---|---|
| 5.1 | gate, sonda `COD-003` |
| 5.2 | gate, sonda `COD-006a`; a outra metade (`COD-006b`) o autor mandou MANTER e a sonda esta invertida para falhar se alguem a "terminar" |
| 5.3 | gate, sonda `COD-016a` |
| 5.4 | gate, sonda `COD-015a` |
| 5.5 | gate, sonda `COD-015d` |
| 5.7 | gate, sonda `COD-016b` |
| 5.9 | gate, sonda `COD-013` |
| **5.6** | **sem sonda.** Verificado direto: as duas datas imprimem na **p. 79** — *"between February 2009 and October 2010 ... while the extraction used here spans January 2009 to August 2011"*. A decisao que sobrou e 5.6b, que continua **aberta** |
| **5.10** | **sem sonda, e nao pede uma:** e um *registro* de dois pontos que deliberadamente NAO viraram pendencia, com o motivo de cada um; os dois estao em `LEFT_OUT.md` (11 entradas LO-) |

O decimo item do §5 (COD-018) esta **retirado por decisao do autor**, com a recusa registrada e a sonda
mantida como `RETIRED` para que ninguem o "termine". Os de §2 foram verificados um a um:
`origin/mobiwac` em `0288cb70` para o 2.2, a sua propria frase de fechamento para o 2.3, `LEFT_OUT.md`
para o 2.7 e o 5.8, `check_verify_list` em rc=0 para o 2.13, e a nota de git em `a07e547b` para o 2.17.

**O que NAO veio para ca, deliberadamente:** todo item que ainda espera uma decisao sua, mesmo que o
trabalho de medicao esteja completo. Um item medido nao e um item fechado.

### ~~2.2 Publicar os arquivos que faltam no branch publico — FEITO em 2026-07-30~~ — FEITO 2026-07-30

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** FEITO 2026-07-30. Push verificado contra o remoto por hash; a parte que sobrava (dois arquivos divergentes) foi absorvida pelo item 2.16, que cobre os quatro.

> **ESTE ITEM FOI APAGADO POR ENGANO, nao resolvido.** Ele existiu da versao `98a33251` ate
> `3bd47d5d` (2026-07-29), e naquele commit -- que era sobre *citacoes de tracker*, nao sobre este
> item -- o bloco 2.2 inteiro sumiu do arquivo sem ser arquivado em
> [`_history/_archive/PENDENCIAS_RESOLVIDOS.md`](PENDENCIAS_RESOLVIDOS.md) e sem renumerar o resto.
> O trabalho **ainda estava aberto** naquele momento. O buraco entre 2.1 e 2.3 ficou no arquivo por
> um dia inteiro e foi voce quem notou. Restaurado aqui com o desfecho, porque um item que
> desaparece silenciosamente e pior do que um item marcado errado: nada aponta para ele.

**O que era.** A frase de reprodutibilidade do Apendice A cita treze caminhos `\path{}` como
disponiveis no branch `mobiwac`. Nem todos estavam la.

**O que aconteceu de fato, e a contagem mudou tres vezes.** Nove -> cinco -> **tres**. As duas
primeiras contagens casavam por **nome de arquivo** nos caminhos que o apendice cita; a auditoria por
**conteudo** mostrou que este branch guarda parte deles em outro diretorio.

**RESOLVIDO em 2026-07-30**, com a sua decisao de reverter em vez de reescrever historia publica:

| commit | efeito |
|---|---|
| `b7b072d2` | `git revert 6c4267ba` — restaura os 14 arquivos que uma delecao publicada tinha removido |
| `0288cb70` | adiciona os TRES que faltavam de fato |

Verificado contra o remoto depois do push: `origin/mobiwac` esta em `0288cb70`, os 25 arquivos de
reprodutibilidade conferem **byte a byte** contra `3c57197c` (0 problemas), os tres adicionados estao
presentes, e o efeito liquido e **18 arquivos, 2.434 insercoes, 0 delecoes**.

> **AINDA E SUA DECISAO, e a unica coisa que sobrou deste item.** Dois arquivos ja publicados em
> `scripts/closing_data/` divergem das copias locais: `m1_stats_n20.py` (411 linhas locais contra 335
> no branch, 84 linhas diferentes) e `m2_prereg_perfold.py` (214 contra 222, 36 diferentes).
> **Nao toquei.** Substituir um artefato publicado por uma versao local divergente e decisao de
> autor, nao limpeza. Se a versao local e a correta, e um commit seu.

---
### ~~2.3 A ficha catalografica: naturalidade Contagem, e a biblioteca que gera~~ — FECHADO pela sua decisao: *"Podemos fechar esse ponto, quando a UFV retorna o pdf adcionamos la

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** FECHADO pela sua decisao: *"Podemos fechar esse ponto, quando a UFV retorna o pdf adcionamos la. No mais vamos manter a norma da ABNT."* Naturalidade Contagem, MG fica registrada para o formulario da Biblioteca Central; a ficha entra como PDF quando voltar.

**Sua decisao 2026-07-29:** Contagem e o dado de naturalidade/residencia e vai na **ficha catalografica**, nao na folha
de rosto. O `\local{Florestal - Minas Gerais}` fica como esta, que e o que a ABNT pede (local de publicacao = cidade da
instituicao) e o que o exemplar do Germano usa.

**O que eu apliquei.** Nada de cidade no LaTeX. Apenas o nome, em tres lugares:
`\autor` e as duas linhas "SILVA, Vitor Hugo **De** Oliveira, M.Sc." do Resumo e do Abstract. Verificado no PDF: a folha
de rosto renderiza `VITOR HUGO DE OLIVEIRA SILVA`.

**O que depende de voce.** A ficha catalografica **nao e gerada por este LaTeX** — vem do formulario da Biblioteca
Central da UFV, e a naturalidade e um campo daquele formulario. Quando preencher, use **Contagem, MG**. Se a biblioteca
devolver a ficha como PDF para inserir, ela entra depois da folha de rosto e eu adiciono o `\includepdf` no lugar certo.

**Se voce quiser Contagem na folha de rosto mesmo assim**, e uma linha em `0_main.tex:189` — mas divergiria da ABNT e do
exemplar, e eu marcaria `[NEEDS SIGN-OFF]` registrando que foi escolha consciente sua e nao conformidade.

> DECISSAO: Podemos fechar esse ponto, quando a UFV retorna o pdf adcionamos lá. No mais vamos manter a norma da ABNT

---
### ~~2.7 O orcamento de tuning de Ch.3 e Ch.4: NAO RECUPERAVEL~~ — FECHADO como nao-recuperavel, medido: o orcamento de tuning de Ch

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** FECHADO como nao-recuperavel, medido: o orcamento de tuning de Ch.3 e Ch.4 nao existe em nenhum lugar do repositorio nem do historico. Registrado em LEFT_OUT.md como limitacao de proveniencia, que era o unico desfecho possivel.

**(A) O que falta.** O numero de configuracoes tentadas por estudo.

**(B) Por que importa.** Uma banca pode perguntar quanta busca de hiperparametro ha por tras de cada resultado.

**(C) O que eu preciso de voce.** Nada a recuperar: nunca existiu um harness de busca e as configuracoes perdedoras nao
foram commitadas. Isso foi estabelecido lendo os dois codebases, nao presumido. A pendencia e apenas **como dizer isso**
se perguntarem. Sugestao: dizer que o desenvolvimento foi manual e iterativo e que o repositorio preserva a configuracao
final, nao o caminho.

> DECISSAO: Documentar no letf_out.md e adcionar esse ponto no appendix B

**FEITO em 2026-07-30 (round 8), e METADE ja estava feita sem que ninguem tivesse notado a outra.**
A sua decisao tem duas partes e elas estavam em estados diferentes:

| parte da sua decisao        | estado quando eu medi                                                                                   |
|-----------------------------|-----------------------------------------------------------------------------------------------------------|
| documentar no `LEFT_OUT.md` | **ja estava**, LO-1, com a fonte (`_history/_round6/10_protocol_recovery.md` §1.4)                                |
| adicionar no Apendice B     | **so para o Cap. 3.** A secao do Artigo 2 (CoUrb) nao dizia nada: `configuration`, `tuning`, `recoverable`, `harness`, `hyperparameter` -> 0 ocorrencias no texto sem comentarios |

O achado de origem e sobre **os dois** estudos -- a tabela de veredito daquele arquivo da
"NOT RECOVERABLE as a budget" para o Cap. 3 **e** para o Cap. 4, pelo mesmo motivo (nunca existiu
harness de busca em nenhum dos dois codebases e as configuracoes perdedoras nao foram commitadas).
Uma frase creditada por inteiro quando so metade andou e a segunda consequencia do V14 do
`AGENT_GUARDRAILS`, que e a razao de esta rodada existir.

Acrescentada uma frase na secao do Artigo 2, com a mesma redacao da do Artigo 1 para os dois
capitulos declararem o mesmo limite do mesmo jeito. **Lido no PDF do volume suplementar, nao no
fonte:** p. 8 (Cap. 3) e p. 9 (Cap. 4), 20 pp, tex_errors 0. A sua recolecao ("nao mudamos muito")
continua **fora** do texto de proposito: e coerente com o codigo, mas recolecao nao e registro
(`AGENT_GUARDRAILS` N1). LO-1 atualizado com onde a frase imprime. Marcado
`[NEEDS SIGN-OFF: PENDENCIAS 2.7, round8]`.

---
### ~~2.13 A contagem dos `[NEEDS SIGN-OFF]`: o comando conta 4 a mais, sempre, e a tabela da §2.1 esta vencida~~ — RESOLVIDO: o comando contava 4 a mais porque era cego a comentarios; corrigido e a contagem passou a bater com a tabela

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** RESOLVIDO: o comando contava 4 a mais porque era cego a comentarios; corrigido e a contagem passou a bater com a tabela. Nao pedia nada de voce.

**(A) O que e.** O `VERIFY_LIST` A7 manda rodar `grep -rn "NEEDS SIGN-OFF" src/ | wc -l` e esperar
46. **Esse comando conta a mais, por construcao**: ele varre `src/build/`, onde
`src/build/fmt/_body.tex` e uma **copia gerada** que o `src/.gitignore` exclui. Sao os mesmos quatro
marcadores contados duas vezes. Toda contagem futura precisa de `--exclude-dir=build`.

**(B) O numero em si nao e estavel, e isso e o achado.** Medi 53, e vinte minutos depois 55, na
mesma sessao. Nao foi erro de medicao: uma **track paralela da rodada 8** acrescentou um marcador em
`apx_b_errata.tex` enquanto eu media, e outros dois chegaram nos commits `3ef8dc8b` e `d9ab436f`.
Registro com o momento, como manda o §4b: **55 no fonte / 59 com `build/`, medido em `d9ab436f`**,
mais um marcador ainda nao commitado na arvore de trabalho.

**(C) A tabela da §2.1 nao fecha mais**, por dois motivos independentes: o total (46) envelheceu, e
ela lista `0_main.tex` com 4 marcadores — arquivo que **nao existe mais**; esses quatro estao hoje
em `content.tex`. Distribuicao medida em `d9ab436f` (`--exclude-dir=build`):

| arquivo | n |
|---|--:|
| `chapters/6_conclusion.tex` | 9 |
| `chapters/2_fundamentals.tex`, `chapters/apx_a_contributions.tex`, `chapters/apx_b_errata.tex` | 6 cada |
| `content.tex` | 4 |
| `chapters/5_mobiwac/06_results.tex` | 3 |
| `chapters/1_introduction.tex`, `3_cbic/results.tex`, `5_mobiwac/02_related.tex`, `5_mobiwac/07_discussion.tex`, `apx_f_cosine.tex` | 2 cada |
| `3_cbic/method.tex`, `4_courb.tex`, `4_courb/methodology.tex`, `4_courb/results.tex`, `5_mobiwac.tex`, `5_mobiwac/05_setup.tex`, `apx_b_static_scope.tex`, `apx_c_ai_disclosure.tex`, `apx_d_ceiling.tex`, `apx_e_ethics.tex`, `main_extra.tex` | 1 cada |

**(D) O que eu preciso de voce.** Nada para decidir; e a sua fila. A ordem de leitura recomendada
continua valendo: A1, depois A3, depois A2.

> **A TABELA DA §2.1 FOI REESCRITA, por outra track desta mesma rodada, e as duas medicoes concordam.**
> Este item dizia *"Nao reescrevi a tabela da §2.1"* -- correto quando foi escrito; a track que auditou
> a §2 reescreveu-a em `ecb81fb6`, antes deste item existir, e as duas chegaram ao mesmo diagnostico
> por caminhos independentes: o comando conta 4 a mais por causa de `src/build/fmt/_body.tex`, e a
> linha `0_main.tex` nomeava um arquivo que nao existe desde `2b9b853d`.
>
> **Estado conciliado, medido em `f624767c`:** 55 no fonte, 59 com `build/`, distribuidos em 22
> arquivos, e a tabela da §2.1 fecha com a propria soma (9 + 6x3 + 4 + 3 + 2x5 + 1x11 = 55). Os 55
> estao todos dentro de comentarios `%`: **zero** aparecem no PDF. A §2.1 leva agora a data da medicao
> e a ressalva de que o numero anda -- inclusive por commits das proprias tracks desta rodada, que
> acrescentaram tres marcadores enquanto o item era escrito. **A sua preocupacao (C) esta atendida e o
> ponto (B) desta secao continua valendo: confie no comando, nao na tabela.**

---
### ~~2.17 UMA AFIRMACAO FALSA MINHA, ja no historico: o commit `a07e547b` diz que o gate saiu 0 e ele saiu 1~~ — RESOLVIDO: a afirmacao falsa foi corrigida com nota de git no proprio commit, e a regra entrou no AGENT_GUARDRAILS

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** RESOLVIDO: a afirmacao falsa foi corrigida com nota de git no proprio commit, e a regra entrou no AGENT_GUARDRAILS. Nao pedia nada de voce.

**(A) O que e.** O commit `a07e547b` (a frase do orcamento de tuning, item 2.7) termina com
*"bash src_utils/check.sh -> rc=0 (22 gates; page counts agree)"*. **A suite saiu 1.** A mesma celula
que fez o commit imprimiu `DEFENSE_RC=0`, `TRACKER_RC=0`, `CHECK_RC=1`, e eu escrevi 0.

**(B) Por que eu estou te contando isso em vez de so consertar.** Porque e a classe exata do V11 do
`AGENT_GUARDRAILS`, a quarta ocorrencia, cometida **dentro da rodada que existe para impedi-la**; e
porque a regra desta rodada e que nenhuma track acredita no proprio relatorio. Achado por uma revisao
independente, nao por mim.

Dois detalhes que importam mais que o erro:

- **O gate vermelho era o `check_trapped_prose`, e quem o disparou foi o bloco de comentario que
  aquele commit acrescentou.** Ou seja: a linha falsa cobria justamente o gate que aquele commit
  quebrou.
- **Onze outros codigos de saida na mesma celula eram 0**, e o olho parou nos onze que confirmavam o
  formato esperado. E o mecanismo do V12 (o leitor para na primeira coisa que responde a pergunta com
  que ele chegou) aplicado a um lote de exit codes.

**(C) O que ficou verdadeiro, medido.** O **conteudo** daquele commit esta certo e foi verificado no
render: a frase imprime em `main_extra.pdf` p. 8 (Cap. 3) e p. 9 (Cap. 4), `make extra` rc=0, 20 pp,
tex_errors 0. Somente a linha do gate era falsa. E o flag do `check_trapped_prose` era **falso
positivo**, por um defeito real da ferramenta: ela comparava todo arquivo de capitulo contra o
`dissertacao.pdf`, mas o `apx_b_errata` renderiza no volume suplementar, entao naquele arquivo o teste
estava invertido -- so podia dar falso positivo e era **cego** a um rasgo de verdade. Consertado em
`f624767c`, validado nas duas direcoes. Depois do conserto: `bash src_utils/check.sh` rc=0, 22 gates,
lido direto.

**(D) O que eu preciso de voce.** Nada para decidir, mas **uma coisa para fazer se voce publicar este
historico.** A correcao esta anexada ao proprio commit com `git notes`, e o `git log` normal ja a
mostra debaixo da mensagem que ela corrige:

```bash
cd /Users/vitor/Desktop/mestrado/ingred
git log -1 a07e547b            # a nota aparece sob a mensagem
```

Escolhi nota em vez de `--amend` porque o commit esta seis commits atras num branch em que tracks
paralelas desta rodada commitaram; reescrever a historia trocaria os hashes dos commits delas.
**Notas nao sobem no `git push` por padrao.** Se voce publicar, precisa de:

```bash
git push origin refs/notes/commits
```

Sem isso a mensagem falsa viaja e a correcao fica na sua maquina, que e pior do que nao ter corrigido.

---
### ~~5.1 Cap. 1: "leakage-guarded" — voce mandou mudar e a frase esta la~~ — APLICADO e verificado pelo gate check_audit_claims (COD-003): o Cap

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** APLICADO e verificado pelo gate check_audit_claims (COD-003): o Cap. 1 nao diz mais "leakage-guarded". Renderiza na p.14.

**(A) O que falta.** Sua decisao no COD-003 foi explicita: *"Eu acredito que a unica mudança que temos que fazer e mudar
a frase no cap. 1."* O objetivo especifico 4 continua prometendo *"a leakage-guarded statistical protocol"*.

**(B) Por que importa.** O proprio Cap. 5 diz que **limitou** o canal de aresta futura, nao que o fechou.
"Leakage-guarded" le como propriedade do pipeline de representacao; o que o protocolo garante e o **split por usuario**.
E a diferenca entre o que voce testou e o que a frase promete.

**(C) O que eu preciso de voce.** So confirmar a troca ja proposta: *"a leakage-guarded statistical protocol"* -> *"a
user-disjoint statistical protocol"*. Uma clausula, nenhum numero, e a frase fica mais fraca, nunca mais forte. E
declaracao de objetivo, entao nao aplico sozinho.

> DECISAO: Valide no texto, pf.

---
### ~~5.2 Cap. 5: "The equivalence is well powered" — a unica coisa que voce pediu no COD-006~~ — APLICADO (COD-006a): "The equivalence is well powered" saiu do paragrafo de protocolo do Cap

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** APLICADO (COD-006a): "The equivalence is well powered" saiu do paragrafo de protocolo do Cap. 5, nas duas arvores. A outra metade (COD-006b, "before any result was read") voce mandou MANTER, e o gate agora falha se alguem a "terminar".

**(A) O que falta.** Sua decisao: *"Let's change only the second point about the: 'The equivalence is well powered'."* A
frase esta intacta em `5_mobiwac/05_setup.tex`, **e no manuscrito do MobiWac tambem** — os dois paragrafos tem 308
palavras cada e diferem apenas nos prefixos dos rotulos
`\ref`. A tabela de desfecho diz que ela foi removida.

**(B) Por que importa.** "Well powered" e poder prospectivo; o que a frase apresenta em seguida (desvio-padrao da
diferenca emparelhada de 0,01 a 0,18) e **precisao observada**. E o paragrafo em que repousa todo o veredito do Cap. 5.

**(C) O que eu preciso de voce.** Aprovar a reformulacao para uma afirmacao de precisao observada, condicionada a
particao fixa, usando os numeros que ja estao na frase. **E edite nos dois lugares**:
Cap. 5 e `articles/[mobiwac]/src/sections/05_setup.tex`, mais uma linha no `ERRATA.md` do MobiWac, que e o regime do
capitulo sob revisao.

> Observacao, porque conta a seu favor: o outro trecho do COD-006, *"before any result was read"*,
> voce decidiu **nao** mexer ("change only the second point"). Ele tambem esta la. Isso esta correto
> pela sua decisao, e nao e pendencia — registro so para voce nao achar que passou batido.


> DECISAO: Vamos reformular.

---
### ~~5.3 Cap. 3: a frase do resultado desbalanceado~~ — APLICADO (COD-016a): a frase do resultado desbalanceado do Cap

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** APLICADO (COD-016a): a frase do resultado desbalanceado do Cap. 3 foi reescrita.

**(A) O que falta.** Sua decisao no COD-016: *"E quanto a frase no cap 3. Sim vamos refaze-la para ser mais entendivel e
facil de ser lida."* A frase continua como no artigo publicado: *"Also, it is important to notice that since we have an
unbalanced result for the MTL and single, this could lead to the worse of other results."*

**(B) Por que importa.** E prosa publicada e co-autorada, e a banca vai ler. O sentido e recuperavel (a comparacao por
categoria pode parecer pior que o agregado), mas so depois de reler.

**(C) O que eu preciso de voce.** Confirmar sua leitura do que a frase quis dizer, e autorizar a reescrita com uma linha
de errata no Apendice B. Nao escrevo no seu nome uma interpretacao de prosa publicada sua.

> DECISAO:Vamsos reformula-la e adicionar no appendix.

---
### ~~5.4 Cap. 3: o prefacio que diz que os capitulos seguintes mudam so a representacao~~ — APLICADO (COD-015a): o prefacio do Cap

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** APLICADO (COD-015a): o prefacio do Cap. 3 nao diz mais que Ch.4 e Ch.5 mudam ambos a representacao.

**(A) O que falta.** Sua decisao no COD-015: *"SObre o A) vamos mudar o prefacio, pq o cap 4 defato não muda a arc mas o
cap 5 muda."* O prefacio continua dizendo que os Caps. 4 e 5 *"revise that verdict by changing the input representation
rather than the architecture"*.

**(B) Por que importa.** O Cap. 5 muda a topologia de compartilhamento **e** o par de tarefas. A introducao acerta isso;
o prefacio do Cap. 3 nao.

**(C) O que eu preciso de voce.** A frase nova, ou aprovacao de uma proposta minha. E caracterizacao do arco, entao e
claim sob C2 do `AGENT_GUARDRAILS` e precisa da sua assinatura.

> DECISAO: Pode refazer por conta propria.

---
### ~~5.5 Cap. 2: as duas metricas prometidas que nenhum capitulo reporta~~ — APLICADO (COD-015d): o Cap

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** APLICADO (COD-015d): o Cap. 2 nao promete mais a metrica relativa de multitarefa que nenhum capitulo reportava.

**(A) O que falta.** Voce disse, no COD-015: *"Quanto ao restante que foi confirmado (a,c,d,f) vamos mudar tmb como
sugerido."* O item (d) sao duas promessas do Cap. 2 — *mean reciprocal rank* e *relative multi-task performance
change* — que **nao aparecem em nenhum capitulo de resultado**. Medido: as duas frases renderizam em uma unica pagina do
Cap. 2 e em nenhuma outra; "MRR" nao aparece em pagina alguma.

**(B) Por que importa.** Um capitulo de fundamentacao que define uma metrica e nunca a usa da a banca uma pergunta de
graca.

**(C) O que eu preciso de voce.** Escolher: **apagar as duas promessas** (barato e honesto, e o que eu recomendo) ou
**reportar as duas metricas**, o que e uma rodada de analise. Apagar uma definicao de metrica e mudanca de escopo do
capitulo de fundamentacao, entao e sua.

> DECISAO: Pode refazer por conta propria.

---
### ~~5.6 Cap. 6: a safra do Gowalla, 2009-2011 contra 2009-2010~~ — SUPERSEDIDO por 5

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** SUPERSEDIDO por 5.6b, que fica aberto: a sua premissa ("ambos usaram o mesmo recorte") nao e o que os arquivos mostram, e agora as duas datas sao impressas. A parte aplicavel deste item esta feita.

**(A) O que falta.** Mesmo item (c) que voce aprovou. O Cap. 6 diz *"collected between 2009 and 2011"*; a prosa
publicada do Cap. 4 diz *"February 2009 and October 2010"*.

**(B) Por que importa — e aqui eu discordo do que a auditoria recomendou.** Ela mandou "casar a moldura com a faixa
publicada". **Nao faca isso sem ler o comentario de proveniencia do Cap. 5**, em
`5_mobiwac/05_setup.tex`: a faixa 2009-01-21 a 2011-08-16 foi **medida no parquet** que o ETL consome, e o dump SNAP de
fevereiro/2009 a outubro/2010 **nao e a fonte de dados** deste trabalho. Pela medicao, o numero da moldura esta certo e
a divergencia e real: os dois capitulos usam extracoes diferentes do Gowalla.

**(C) O que eu preciso de voce.** Decidir como dizer isso. Sugestao: manter 2009-2011 no Cap. 6 e acrescentar uma
clausula dizendo que o Cap. 4 reporta a faixa do dump que aquele estudo usou. Nao
"corrija" um numero medido para casar com um herdado.

> DECISAO: Busque pelo que o artigo original cita e vamos usar isso em ambos. Inclusive ambos usaram o mesmo recorte não
> houve diferença.

---
### ~~5.7 Cap. 5: quebrar o paragrafo de integridade, sem mudar uma palavra~~ — APLICADO (COD-016b): o paragrafo de integridade do Cap

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** APLICADO (COD-016b): o paragrafo de integridade do Cap. 5 virou seis paragrafos, sem uma palavra alterada. So na dissertacao, como voce mandou.

**(A) O que falta.** Sua decisao: *"Podemos aplicar as quebras de linha no cap 5."* O bloco continua **um paragrafo
unico de ~580 palavras**, com os quatro fundamentos numerados dentro dele.

**(B) Por que importa.** E o paragrafo que a persona 09 chamou o melhor trabalho da rodada e que as personas 15 e 01
chamaram a pior falha de legibilidade. A resolucao registrada e das duas: **inserir quebras, nao mudar nenhuma
palavra**.

**(C) O que eu preciso de voce.** Nada de conteudo — mas o capitulo esta sob revisao, entao a quebra precisa cair nos
dois arquivos (dissertacao e manuscrito) para os textos nao divergirem. Confirme que quer isso agora e eu aplico; e
edicao de forma, com zero palavra alterada.

> DECISAO: Vamos alterar só na dissertação.

**FEITO em 2026-07-30 (round 8), commit `09404da7`, e a sua decisao de mexer so na dissertacao foi
respeitada.** O paragrafo de 581 palavras virou seis (59 / 54 / 93 / 61 / 155 / 159), cortado nos
quatro fundamentos numerados e em "A second reference". **Nenhuma palavra mudou, e isso foi medido no
PDF, nao no fonte:** o texto do paragrafo foi extraido de `build/main.pdf` antes e depois com
pypdfium2, cabecalhos de pagina removidos dos dois lados, 595 palavras nas duas vezes, strings
iguais, `sha256 b0e069888dc2d2ed3f5ec0cfb70b809e` nas duas. E as quebras aparecem de fato: cinco
recuos novos de ~37 pt abrem exatamente naqueles cinco pontos (pp. 66-67), que antes estavam no meio
da linha. O corte foi feito por script, que verificou que remontar os seis pedacos com um espaco
reproduz a linha original byte a byte **antes** de escrever.

`articles/[mobiwac]/src/sections/05_setup.tex` **nao foi tocado.** Um briefing desta rodada mandava
aplicar nos dois; a instrucao foi retirada quando a sua decisao aqui foi conferida. Um comentario de
~30 linhas no topo do paragrafo registra a divergencia para ninguem "consertar" de volta, com a
medicao que a contem: os dois paragrafos **ja** diferiam muito mais que isso (o manuscrito tem 223
palavras e "three grounds", o capitulo tem 581 e "four grounds"), entao nao existia paragrafo
equivalente no manuscrito onde aplicar a mesma quebra.

---
### ~~5.8 Apendice A: seus papeis no CoUrb, que so voce tem~~ — RETIRADO por sua decisao: *"Nao precisa mexer nisso, pode remover essa preocupacao

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** RETIRADO por sua decisao: *"Nao precisa mexer nisso, pode remover essa preocupacao."* Registrado em LEFT_OUT.md LO-11, e o brief da rodada 8 pediu de novo por erro meu — a esteira recusou citando as suas palavras.

**(A) O que falta.** Voce respondeu ao COD-018: *"Meu papel no courb foi na implementação, auxilo ao meu aluno de
graduação na sua pesquisa pelos modelos de embedding, e escrita da parte do MTL e parte da conclusão."* Isso **nao esta
no Apendice A**. As paginas do apendice descrevem a plataforma e o ETL; nenhuma delas atribui papel por funcao no CoUrb.
O que existe e o prefacio do Cap. 4, que diz segundo autor, autor do MTLnet e apresentador — nao a implementacao, nem a
orientacao do aluno, nem a escrita.

**(B) Por que importa.** E credito de autoria em trabalho co-autorado, num apendice que declara contribuicoes. Um texto
que omite metade do seu papel e um texto que subdeclara voce.

**(C) O que eu preciso de voce.** A frase final, com seus termos. Eu tenho o insumo (a citacao acima) mas nao escrevo
credito de autoria no seu nome — e fato que so voce detem, e a mencao ao aluno de graduacao e decisao sua, nao minha.

> DECISAO: Não precisa mexer nisso, pode remover essa preocupação

**RESPEITADO em 2026-07-30 (round 8), commit `11e7e5d7`. O Apendice A nao foi tocado, e isso e o
resultado do item.** O briefing desta rodada mandava adicionar o credito de todo jeito. Parei e
perguntei em vez de escrever: credito de autoria em trabalho co-autorado e claim que so voce faz
(`AGENT_GUARDRAILS` C2), e mencionar o aluno de graduacao e decisao sua. Voce confirmou a decisao
registrada aqui.

Duas consequencias, para a ausencia nao parecer esquecimento: o gate desta rodada
(`src_utils/check_audit_claims.py`) tinha uma probe exigindo o credito **presente**, escrita a partir
da expectativa da auditoria e nao da sua decisao. Ela foi para uma tabela `RETIRED` que **imprime em
toda execucao** com a sua frase como motivo, em vez de ser apagada em silencio; e a omissao esta em
[`LEFT_OUT.md`](LEFT_OUT.md) LO-11, no formato daquele arquivo. Medido depois: 8 de 8 probes holds,
1 retirada, rc 0, e um teste de sabotagem (inverter a expectativa de uma probe) ainda faz o gate sair
1. Reversivel a qualquer momento: e uma frase no Apendice A com `[NEEDS SIGN-OFF: COD-018]`.
Verificado no render: "undergraduate" nao aparece em nenhuma das 100 paginas.

---
### ~~5.9 Apendice C: nomear o modelo, como voce pediu~~ — APLICADO (COD-013): o Apendice C nomeia a familia do modelo em PROSA, nao so em comentario

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** APLICADO (COD-013): o Apendice C nomeia a familia do modelo em PROSA, nao so em comentario. Renderiza na p.92.

**(A) O que falta.** Sua decisao no COD-013: *"fazendo somente a alteração de adicionar o modelos esse que pode cirat o
opus 4.8, inclusive não precisa de contar toda a historia que o fable acbou e tivemos que usar o opus, só cite que
usamos o opus e fim."* Medido: a palavra "Opus" **nao renderiza em nenhuma das paginas** do build de defesa. O apendice
diz apenas "Claude (Anthropic)". As duas unicas ocorrencias de "Opus" no fonte estao em comentarios, que nao renderizam.

**(B) Por que importa.** A politica do CNPq pede a ferramenta **e a versao**. E foi exatamente o que voce pediu, sem a
historia em volta.

**(C) O que eu preciso de voce.** A string exata da versao. Voce escreveu "opus 4.8" na decisao; antes de imprimir um
numero de versao no documento eu quero que voce confirme qual e, porque nao posso verificar isso de dentro daqui e um
numero de versao errado num apendice de integridade e pior que nenhum.

> DECISAO: Usamos o opus 4.8, fable 5 e opus 5.

**FEITO em 2026-07-30 (round 8), commit `62708bcb`, corrigido em `aec06d77`.** Uma clausula, sem
contar a historia da troca, como voce pediu. **Lido no PDF, pagina 92 (folio impresso 92):**
"This dissertation was written with the assistance of a generative artificial intelligence tool,
Claude (Anthropic), **in its Opus 4.8, Fable 5, and Opus 5 versions**, used as a research and writing
assistant under the author's direction."

Voce e a fonte dos tres nomes, e e isso que autoriza imprimi-los; o trail de commits nao carrega
versao nenhuma. Como confirmacao, `host.list_models()` resolve `claude-opus-4-8`, `claude-fable-5` e
`claude-opus-5`. A pagina do `platform.claude.com` que voce indicou **nao abriu** (403 para cliente
nao-navegador, e 502s); nao falsifiquei user agent para contornar.

> **ERRO MEU, corrigido no mesmo dia em `aec06d77`, e voce deve saber dele porque e da classe que
> este projeto mais teme.** A primeira versao do comentario de proveniencia e da mensagem do commit
> `62708bcb` citava a nota da Anthropic como dizendo que ela "names Claude Opus 4.8 as the
> next-most-capable model" e **citava entre aspas** um lancamento do Opus 5 ("comes close to the
> frontier intelligence of Claude Fable 5"). **Nenhuma das duas frases estava em nada que eu abri:**
> a busca devolveu **titulos e URLs, sem corpo de pagina**, entao a citacao era minha invencao.
> Encontrado por uma revisao independente e confirmado abrindo o resultado guardado da busca. E
> exatamente `AGENT_GUARDRAILS` R5, dentro do apendice que declara o uso de IA. A frase impressa
> nunca dependeu disso e nao mudou. O que os titulos sustentam de fato: existem produtos Anthropic
> chamados Claude Fable 5 e Claude Opus 5 (anthropic.com, cnbc.com e axios.com de 2026-07-24).
> "Opus 4.8" nao aparece em resultado nenhum: apoia-se no id do registry e na sua palavra.

---
### ~~5.10 Dois pontos do audit que NAO viraram pendencia, e por que~~ — REGISTRO, nao pendencia: os dois pontos do audit que deliberadamente NAO viraram pendencia, com o motivo de cada um

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** REGISTRO, nao pendencia: os dois pontos do audit que deliberadamente NAO viraram pendencia, com o motivo de cada um. Movido para ca por ser historico fechado.

Para o registro, porque um item ausente sem explicacao parece esquecimento:

| Ponto                                                                                                     | Por que nao esta acima                                                                                                                                     |
|-----------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| O ledger de adaptacao do Cap. 4 aponta a traducao EN como fonte de record, e nao o artigo publicado em PT | E arquivo de repositorio, fora de `src/`, e nao precisa de voce: qualquer agente corrige. Fica registrado aqui como divida tecnica, nao como sua decisao   |
| A nota do Cap. 6 dizendo que 56,16 "ainda nao carrega spread"                                             | O spread **ja esta** na frase (desvio-padrao 1,89, medido no render). O que sobrou e o comentario obsoleto que diz o contrario. Tambem nao precisa de voce |

---

---


---

## Fechados em 2026-07-30 (segunda leva da rodada 8)

Tres itens que o autor apontou como ainda no tracker apesar de prontos. **Dois fecham pela
decisao dele proprio** — 2.4 e 2.6 tinham a ruling escrita no bloco e o trabalho feito — e o
terceiro fecha porque o proprio bloco `(C)` dele dizia "Nada": e registro, nao pendencia.
Cada um re-verificado contra a arvore viva antes de sair, nao pelo que eu lembrava.

### ~~2.10 Cobertura de auto-teste dos catorze checkers — registro, nao pendencia~~

> *Titulo anterior, mantido para rastreabilidade (o item foi encurtado antes de ser arquivado, e uma busca por titulo antigo tem de acha-lo): "Dos catorze checkers: sete se auto-verificam de verdade, um tem auto-teste que nao morde, dois tem fixtures, quatro nao tem nada".*

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** FECHADO como registro: o proprio bloco `(C)` do item dizia **"Nada"** de voce. E uma medicao concluida (sete dos catorze checkers morrem quando sabotados, um tem auto-teste que nao cobre o detector, dois tem fixtures, quatro nao tem nada) mais a regra V13. `make selftest` nomeia os nao-provados em cada execucao, entao o gap fica visivel sem o tracker. rc=0.

**O que e.** Medido por sabotagem (quebrar o detector e ler o codigo de saida), nao por procurar um
`def self_test`: **sete** morrem quando quebrados, **um** tem auto-teste que nao cobre o proprio
detector (`check_negative_parallelism`), **dois** tem fixtures, **quatro** nao tem nada.
`make selftest` nomeia os nao-provados em cada execucao em vez de omiti-los.

**(C) Nada de voce.** A tabela completa e a regra que saiu disso (`AGENT_GUARDRAILS` §4b V13) estao em
[`_history/_round8/29_pendencias_detail.md`](../_round8/29_pendencias_detail.md). Fica aqui so como registro do
que ainda nao tem prova.

---

### ~~2.4 A secao de escopo da tarefa estatica~~

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** FECHADO pela sua decisao, as duas partes feitas. O Apendice B saiu do corpo principal (rodada 7, esta no volume suplementar) e a prosa do B.5 foi reescrita em 2026-07-30. Verificado na prosa viva: a frase que voce citou tem **0** ocorrencias, o texto diz que a entrada e o nome do proprio local (4 ocorrencias), e a faixa 284-365 esta re-confirmada contra o pipeline. Renderiza na p. 11 do volume extra.

Sua decisao tinha duas partes e **as duas estao feitas**: o Apendice B saiu do corpo principal (rodada
7, esta no volume suplementar) e a prosa do B.5 foi reescrita em 2026-07-30. Verificado: a frase que
voce citou (*"built from a fine-grained class label attached to each place"*) nao existe mais, o texto
agora diz que a entrada e o **nome do proprio local**, e a faixa 284-365 esta re-confirmada contra o
pipeline. Renderiza na p. 11 do volume extra.

*Este bloco fica aqui uma rodada para voce conferir e depois vai para o arquivo.*

---

### ~~2.6 A coluna do CBIC que nao reproduz~~

> **POR QUE SAIU DO TRACKER (movido em 2026-07-30).** FECHADO pela sua decisao *"documentar no left_out.md"*. `LEFT_OUT.md` LO-2 carrega o achado (tres das quatro colunas publicadas do CBIC reproduzem exatamente, 21 de 21 celulas cada; a quarta nao casa com nenhum artefato) e a restricao que ele impoe. A linha "Open for the author" dentro do LO-2 era anterior a sua decisao e foi removida.

Sua decisao foi *"documentar no left_out.md"*, e esta feito: `LEFT_OUT.md` LO-2 carrega o achado
completo (tres das quatro colunas publicadas do CBIC reproduzem exatamente, 21 de 21 celulas cada; a
quarta nao casa com nenhum artefato deste repositorio) e a restricao que ele impoe — nenhuma frase
futura pode dizer que os numeros do CBIC sao reproduziveis sem excluir essa coluna.


**A sua palavra, verbatim:** *"DECISSAO: Documentar no letf_out.md"*.

**O que o item media, restaurado 2026-07-30:** a coluna que nao reproduz e a de **proxima-categoria do
modelo conjunto**; as outras tres conferem **21/21 celulas** cada. Nao ha erro conhecido no numero
publicado — o que falta e a **execucao (rundir) que o gerou**, e a pergunta que eu fiz era se existe um
fora deste repositorio.

*A linha "Open for the author" dentro do LO-2 e anterior a sua decisao e esta obsoleta.*

---

### ~~2.22 Apendice F: o revisor de excelencia aprova, mas a assinatura e sua~~ (arquivado 2026-07-30)

**FECHADO PELO AUTOR.** Ele aprovou: *"I approve the appedix F you can remove the `[NEEDS SIGN-OFF]`,
but i have some considerations"*, seguido de quinze pontos numerados (0-14). Todos os quinze foram
aplicados na rodada 9c e o marcador saiu do fonte.

**O que mudou, medido no PDF renderizado e nao no relatorio de nenhuma esteira:**
- **Ponto 0, a renumeracao.** O volume principal imprimia A, C, E, F porque os antigos B e D foram para
  o volume suplementar. Agora imprime **APPENDIX A (p.90), B (p.93), C (p.94), D (p.97)**, em sequencia.
  O apendice do cosseno e o **D**. O volume suplementar mantem as letras historicas B e D, e o paragrafo
  "About this volume" explica a ambiguidade em vez de escondê-la.
- **Pontos 1 e 4, as duas citacoes.** `standley2020tasks` para "can end up worse at both than two
  dedicated models are at one each" e `yu2020pcgrad` para o cosseno como a quantidade que a literatura
  de gradient surgery usa para definir conflito. Nenhuma entrada nova foi inventada: as duas ja estavam
  no `references.bib`, que e a resposta correta mais barata.
- **Pontos 3 e 13, o arco dos tres estudos.** Ele estava certo, e a medicao e mais forte do que ele
  colocou: o Cap. 3 e o Cap. 4 preveem classificacao de categoria e proximo POI com hard sharing e FiLM;
  o Cap. 5 e este apendice preveem proxima categoria e proxima regiao sobre um tronco de cross-attention
  sem camadas ocultas em comum. **Nem o par de tarefas nem a arquitetura sao compartilhados.** As duas
  sentencas foram REMOVIDAS, nao reescopadas: qualquer versao reescopada seria especulacao que os dados
  nao sustentam.
- **Pontos 2, 5, 6, 7, 9, 10, 11, 12:** cortes e simplificacao. As frases que ele citou estao todas em
  zero ocorrencias na prosa viva. O ponto 11 agora nomeia os datasets (Alabama e Georgia), conferidos
  contra a saida de `cosine_stats6.py`.
- **Ponto 8, o ingles britanico.** "feature needs saying plainly" -> "must be stated plainly". A regra e
  o gate nasceram deste ponto: `check_register.py` (gate 25) cobre grafias E construcoes, porque a
  instancia dele era uma construcao needs+gerundio e uma lista de grafias teria perdido justamente o
  achado dele.
- **Ponto 14, a qualificacao.** Uma sentenca em D.3: gradientes ortogonais nao significam que as tarefas
  nao compartilham conhecimento, porque os dois fluxos ainda trocam informacao pelo tronco de
  cross-attention.

**Onde ler a apuracao ponto a ponto:** `_history/_round9/43_apxf_author.md`, com as palavras dele, o que foi feito
e a evidencia renderizada de cada um.

**A DECISAO DELE, VERBATIM**, preservada aqui porque os quinze pontos numerados sao o registro do
que ele pediu e nenhum resumo substitui as palavras dele:

> **AUTHOR:** I approve the appedix F you can remove the `[NEEDS SIGN-OFF]`, but i have some considerations:
> 0. You must rename all the appendix, so the letters respect the correct order in the current version of the text. In
     this case this appendix would be the letter D.
> 1. On the `an end up worse at both than two dedicated models are at one each.` we shoud add a reference to it.
> 2. Don't say `stranger result` without cite some ref, but my main take is not to say this, is your jugdment and can
     cause questions in the reviewer
> 3. This phrase: "That is why varying the gradient balancer changed so little in the first study, and why changing the
     representation changed so much in the second and third.". Have a huge erros in the first sutdy we use 2 diffents
     tasks, than the last third study of mobiwac, also the arch of the MTLnet was different so we can relate the results
     of this appendix to the first and secon study.
> 4. On the "the cosine of the angle between the two resulting gradient vectors was recorded" we should cite some
     article/studie/document that show this apporach
> 5. Exclude this: "so one configuration on one dataset is five series of fifty values, and two of Florida’s
     carryapartialre-run ontopoftheirs.", is over detail.
> 6. This is a implementation detail let's exclude also: "That chapter reaches the same conclusion from a smaller
     development-time measurement,onanearlierdatapreparationandoverfourseedsratherthanper-epochseries,so the
     twosetsofnumbersarenotinterchangeableand this appendix supersedes nothingthere."
> 7. on the: "Every test below therefore runs on five fold... Whereacountofobservationsappearsitdescribesthedata,
     notatest’ssample size." this part explain the how the experiments was runned is importante, but we can simplify the
     details, don't need to do a lot of tech explanation, also about the florida I belive explain it in much details can
     cause confusion, lets try to be more straight.
> 8. The phrase: "feature needs saying plainly" this is britisher english and this boke on of the agents_guartrails. If
     this is not in the guardrails add this and eval in the rest of the text if we have similar stuctures that are
     britisher.
> 9. This phrase:  "Two departures from that flat picture appear" is pure A.I, we cna be more simple and direct.
> 10. This phrase: "both are worth reporting rather than smoothing" we don't need to say this, appears as we are try to
      hide somthing we just need to report.
> 11. On the: "A 𝑡-test does reject on both datasets and for both
      departures,butatfiveobservationsthatrestsentirelyonassumingnormality,andthisappendix
      willnotacceptforoneclaimabasisitrejectsforanother.", you don't say which datasets, and this phrase is confusing
      and hard to read for whom don't have a lot of knowhow. We can try to improve the rest of this paragraph
> 12. The phrase: "Both point away from trouble in any case. A positive cosine is mild cooperation, not conflict, and
      the decline stays inside the margin throughout while moving toward zero rather thanawayfromit." is well written,
      but is not natural for a non native writer in english, and force a non native read more than once to understand.
> 13. On the paragraph that starts with: "The second is about the arc of the three studies.", we need to take care cause
      the first two studies was diferrent tasks that these ones that we are testing int eh appendix F. Maybe remove
      this.
> 14. Somthing that worths to mention, don't need fither explanation, in the F.3 is that besides the gradients don't
      addup, this don't means that the tasks are not sharing their knowladge since exstie otehr mechanims like the gate
      in the arch and so on...


---

## Arquivados em 2026-08-02 (varredura de auditoria pedida pelo autor)

Cada item abaixo foi **medido contra o documento** antes de ser fechado, nao lido do proprio
cabecalho. A varredura tambem encontrou o inverso: dois itens que o tracker dava por abertos
(`2.20`, `2.23`) estavam aplicados, e dois que ele dava por resolvidos nao estavam (`2.26`,
que foi aplicado agora, e `EX-9` dentro de `2.23`, que a propria revisao do autor superou).

### ~~2.8 `CONSIDERATIONS.md` — EXECUTADO nesta rodada; a fila de decisao virou o §6~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** sua propria decisao fecha o item: "nada aqui. Este item esta fechado; o que espera voce esta no §6".

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


**O que era.** `src_utils/CONSIDERATIONS.md` (1.229 linhas, nao commitado) trazia o feedback verbal do Germano
transcrito por voce (l. 3-58), o feedback escrito do Fabrício (l. 59-309), a auditoria Codex do Cap. 2 de 2026-07-28 (l.
310-994) e o adendo dela (l. 995-1229), com uma lista de trabalho consolidada. Voce pediu as duas coisas do item:
commitar o arquivo, e executar a divisao.

**O que foi feito (round 9, commit `d4078c75`).** O arquivo foi commitado **sem uma alteracao**
antes de qualquer reescrita, e depois reescrito no esquema de um bloco por item: **43 blocos**, IDs estaveis `FAB-01`..
`FAB-31` (a sua propria numeracao), `GER-01`..`GER-11` e `AUT-01`. A prosa original esta preservada byte a byte em
[`_history/_round9/30_considerations_prosa_original.md`](../_round9/30_considerations_prosa_original.md), com o sha256 e o comando
que o reproduz no cabecalho.

**O passe de citacoes obsoletas, antes de qualquer juizo.** Das 41 ancoras localizaveis, **32 sao exatas e 9 estao
obsoletas** (4 alteradas, 5 desaparecidas). As nove obsoletas sao **todas** do Fabrício, **todas** citam `0_main.tex`
(arquivo que deixou de existir em 2026-07-29), e sao exatamente os itens **FAB-02 a FAB-10**. As **20** ancoras dele
fora daquele arquivo conferem todas.

*(Este paragrafo dizia "10 obsoletas, todas citam `0_main.tex`" e "21 ancoras". Estava errado por uma: a decima era o
**FAB-27**, que esta em `tables/frame/lineage.tex`, e cuja citacao so falhou porque ele a escreveu prefixada com "Na
tabela: " e terminada em "....". O texto que ele cita esta presente palavra por palavra. Os numeros certos sao os de
cima, e sao os mesmos que o §6 carrega — o §2.8 tinha ficado com a versao anterior a correcao, o que deixou este arquivo
contradizendo a si mesmo por dois commits.)* Comandos em
[`_history/_round9/31_stale_quote_pass.md`](../_round9/31_stale_quote_pass.md).

**A divisao.** 21 itens "eu aplico", 21 precisam de voce (viraram o **§6**), 1 bloqueado (FAB-28, verificacao falhou).
Tres medicoes da auditoria de 2026-07-28 **nao reproduzem** e foram retomadas: ela contou 27 paragrafos / media 161 /
cinco acima de 240 palavras, e hoje sao 33 / 132 / 4.

**Preservado da esteira paralela (commit `c94d1f19`, 02:01:51), porque a minha reescrita deste bloco apagou a nota dela
e a nota esta certa** — anotada como dela, e reconciliada com a numeracao deste arquivo:

> **ATUALIZACAO 2026-07-30:** voce acrescentou um ponto seu no fim do arquivo (l. 1228), sobre
> otimalidade de Pareto nos fundamentos de MTL. **Esse esta sendo executado agora** — e o item 2.12 pelo
> outro lado (o termo esta em prosa publicada e nao esta no `GLOSSARY`, que e fail-closed), e a esteira que
> trabalha nele tambem le os itens G8 (definicoes formais de MTL) e G10 (o argumento tecnico para o achado
> de nao-conflito) porque sao a mesma peca de texto. **O resto do arquivo continua nao executado.**

Duas reconciliacoes, para os ponteiros nao apontarem para o vazio. Os `G8` e `G10` daquela nota sao, nos IDs estaveis
deste arquivo, o **GER-09** e o **GER-11**; e o "ponto no fim do arquivo (l. 1228)" e o **AUT-01**. E a frase final
daquela nota deixou de valer entre 02:01 e agora: o resto do
`CONSIDERATIONS.md` **foi** executado nesta rodada, no sentido de estar medido e dividido, mas **nenhum item foi
aplicado a nenhum capitulo** — que e provavelmente o que ela queria dizer.

> **AUTHOR:** nada aqui. Este item esta fechado; o que espera voce esta no **§6**.

*Forense: `_history/_round9/31_stale_quote_pass.md` (o passe de obsolescencia, incluindo os dois instrumentos meus que estavam
quebrados e como cada um foi pego).*

---

### ~~2.9 Os tres datasets que faltavam no Apendice F — RODADOS. O apendice agora tem SETE, e sobra uma decisao pequena~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** **CORRIGIDO em 2026-08-02 apos auditoria.** O fechamento anterior desta linha dizia *"O Cap. 5 reporta a
medida de cosseno dos sete datasets, e os dois tres (artigo e dissertacao) foram editados como voce
autorizou"* — e **nenhuma das duas metades estava medida**. A sonda procurou `+0.001` e `0.0032`, que sao
**exatamente os numeros da medida ANTIGA que este item descreve**, entao a presenca deles nao distinguia
atualizado de nao-atualizado; e a metade "os dois trees" nunca foi verificada, porque a medicao varreu so
`src/**/*.tex` e a arvore do artigo nao foi aberta.

**Medido de verdade, e o resultado era misto:** a dissertacao tinha o ponteiro para o apendice; o artigo
`[mobiwac]` **nao tinha nada** — e o artigo nao tem apendice nenhum, entao um `\ref` interno era impossivel.
O comentario de proveniencia daquele paragrafo exige que os dois textos fiquem identicos, e a frase que
existia so na dissertacao ja havia quebrado essa paridade.

**Resolvido por decisao sua de 2026-08-02:** a frase foi reescrita para **sobreviver standalone** (sem
depender de nenhum documento externo) e aplicada **palavra por palavra nas duas arvores**; o link para o
Apendice D ficou no **paragrafo de abertura da secao** na dissertacao, que e prosa exclusiva dela e ja cita
os Caps. 3 e 4 por `\ref`. Verificado: a frase identica nas duas arvores, o ponteiro renderizando na p. 64
do `main.pdf`, zero `Appendix ??`, zero referencias indefinidas. Tres probes novos (`A9-diss`, `A9-ptr`,
`A9-oldnum`) medem o requisito real, cada um validado por sabotagem individual. O `A9-oldnum` existe para
manter os numeros de quatro seeds **como estavam** — sao justamente o par cuja presenca a sonda retirada
confundiu com prova.

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


**FEITO EM 2026-07-30, e nada aqui espera GPU.** California, Texas e Istanbul foram medidos no `nespedgpu`, um dataset
por job, sequencialmente. Cada `rc=0` foi lido do `_status.json` do proprio job, e cada duracao vem dos **stamps do
proprio dataset**, nunca do total do job:

| dataset    | job        | duracao (stamps proprios)    | folds |
|------------|------------|------------------------------|-------|
| istanbul   | `9f3da11f` | 19,3 min (04:56:49→05:16:07) | 5/5   |
| texas      | `6faa6e22` | 55,1 min (05:17:52→06:12:59) | 5/5   |
| california | `67585dff` | 44,3 min (06:14:17→06:58:37) | 5/5   |

**Custou ~2h de GPU, nao as ~6h estimadas** — e o motivo importa: `--no-checkpoints`. Os pesos salvos eram o que enchia
o disco (`results/check2hgi/texas/checkpoints` sozinho tinha 7,1G) enquanto o diretorio que carrega o diagnostico tem
~6-11 MB. `df -h /home` ficou em **313G usados / 61G livres, 84%, sem mover**, lido direto antes de cada submit e depois
de cada run. E nao muda numerica nenhuma: **medido**, nao argumentado — o alabama, que ja estava no apendice, foi
re-rodado com a flag e reproduziu os cinco CSVs por fold **byte a byte identicos**.

**Nada foi apagado na sua maquina.** Os 61G que voce liberou continuam livres; os dois arquivos corrompidos da corrida
de harvest antiga seguem em `~/cosine_appendix/california_f2` e `_f3` (md5 `2afa6aebfb...` nos dois) e **nao entraram**
no parquet: o california veio do job `67585dff`, cujos cinco folds tem cinco md5 distintos.

**O apendice passou de quatro para SETE datasets** — as suas **seis** mais a Georgia, que nao e uma das seis. 4.650
observacoes, todos os testes no **fold** como unidade. Equivalencia por TOST dentro de ±0,05 vale em todos os sete.
Verificado no PDF renderizado (pp. 97-102), nao no fonte.

**Um achado que vale mais que os tres datasets:** o "limite de 35 minutos do host" era **nosso**. O `job.sh` embrulha a
carga em `timeout <N>` com o `timeout_seconds` que o agente passou, e o `job.sh` do job 805120f1 diz `timeout 2100` =
35,0 min exatos. Nao existe teto de 35 min nesse host. O texas rodou 55 min. **O dataset que foi registrado como
impossivel era impossivel apenas sob um limite que nos mesmos definimos.**

> **DECISAO SUA, e e pequena:** o Cap. 5 continua reportando a medida antiga desse mesmo cosseno (de
> desenvolvimento, quatro seeds, preparacao anterior) com media +0,001 e maior media por dataset
> +0,0032. O apendice agora da +0,00102 no conjunto e +0,0112 no alabama. **Nao sao contraditorios** —
> sao corridas diferentes, e o apendice ja diz isso em uma frase. Voce decide se quer (**a**) deixar
> como esta, ou (**b**) que eu proponha uma nota no Cap. 5 apontando para o Apendice F. **Eu nao toco
> no Cap. 5**: esta sob revisao.

*Forense completa (a corrida de harvest, o gate de distincao por md5 validado por sabotagem, o `c.download()` que
achatou quinze arquivos em cinco, e o cap que era nosso): [`_history/_round9/30_cosine_six.md`](../_round9/30_cosine_six.md).*

> **AUTHOR:** Vamos um pouco ainda mais longe, voce pode editar o Cap. 5 tanto o artigo original quanto o da
> dissertacao, como estamos um fase de revisão no mobiwac, conseguimos mandar uma revisão ainda.

---

### ~~2.11 A assimetria do resultado de regiao: o Cap. 5 ressalva, e o resto do documento nao~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** Opcao B aplicada: 21 mencoes de nao-inferioridade na prosa viva, incluindo Resumo e Abstract, cada uma com a margem e o teste nomeados.

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


**Origem:** `_history/_round6/VERIFY_LIST.md` itens 4 e 5 (achado L-5 do ledger), entregues em 2026-07-30.

**(A) O que e.** `chapters/5_mobiwac/05_setup.tex` diz que o plano de analise *"did not cover next-region superiority,
so the four next-region gains ... are secondary results outside it"*. O resto do documento afirma o mesmo resultado
**sem essa ressalva**. Medido com o varredor que remove comentarios, sobre os 54 `.tex`:

| onde                                                                                                            | forma                                                                  |
|-----------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| `1_introduction.tex:132`, `6_conclusion.tex:21` e `:93`                                                         | "four of six" / "four of the six"                                      |
| `2_fundamentals.tex:786`, `5_mobiwac/01_introduction.tex:39`, `5_mobiwac/08_conclusion.tex:14`, `5_mobiwac.tex` | idem                                                                   |
| `content.tex:166` (Resumo e Abstract)                                                                           | "quatro deles" / "four of them" — a mesma alegacao, em outras palavras |

No PDF de defesa (100 pp) a alegacao sem ressalva imprime nas **pp. 14, 58, 59, 76, 77 e 78**; a ressalva imprime **so
na p. 67**. Sao sete sitios em prosa mais as duas parafrases do pre-textual, contra uma ressalva.

**(B) Por que importa.** O registro estatistico de 2026-07-27 e inequivoco: o teste primario registrado para **toda**
celula de regiao e nao-inferioridade TOST. Uma leitura rapida do Resumo, da Introducao ou da Conclusao le "outperforms
em quatro de seis" como resultado primario; a p. 67 diz que nao e. Nenhuma track da rodada 6 assumiu isso (achado L-5 do
ledger).

**(C) O que eu preciso de voce.** Uma regra, e ela vale para os nove sitios de uma vez:

> **(a)** o texto de moldura acrescenta "as a secondary result" (ou equivalente) **uma vez**, no
> ponto que voce escolher — o candidato natural e a Conclusao, que ja e o lugar onde o escopo do
> plano de analise e discutido. Custo: uma frase, mais linha de errata se voce quiser rastrear.
> **(b)** a assimetria e deliberada — o Cap. 5 e o capitulo que carrega o metodo, entao e onde a
> ressalva pertence — e isso vai para `LEFT_OUT.md` com o motivo. Custo: zero no texto, mas o
> registro passa a existir.
>
> **Eu nao decido isto** porque muda o que o Resumo e a Conclusao afirmam sobre o resultado
> principal do Cap. 5, que e prosa sua sobre um resultado seu.

> **AUTHOR:**  Na verdade se esses resultados forem de grande importancia e algo importante para narrativa, vale deixar
> eles
> como primario é só alterar o mobiwac, ao invés do outros textos, o que acha ? Se não concorda vide a narrativa do
> texto vamos de A

---

### ~~2.12 `Pareto-stationary point` esta na prosa e nao esta no registro (o `GLOSSARY` e fail-closed)~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** `Pareto-stationary point` registrado no `GLOSSARY.md`, e a linha de errata que voce pediu esta no Apendice B.

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


**(A) O que e.** A regra de manutencao do `GLOSSARY.md` e explicita: *"a term not in this registry may not be used in
dissertation prose"*. Medido hoje:

```bash
cd /Users/vitor/Desktop/mestrado/ingred/articles/dissertacao
grep -c 'Pareto-stationary' GLOSSARY.md          # 0
```

e o termo esta em prosa em **cinco** sitios (o registro anterior dizia dois), em quatro arquivos:
`chapters/3_cbic/method.tex` (*"convergence to a Pareto-stationary point"*), duas vezes em
`chapters/3_cbic/basis.tex` (*"Pareto-optimal descent directions"* e *"Pareto efficiency"*),
`chapters/4_courb/methodology.tex` (a garantia do Nash-MTL, a mesma frase do item 3 do
`VERIFY_LIST`) e a linha de errata que registra essa correcao, em `tables/courb/errata.tex`, que ainda traz a forma sem
hifen, "Pareto stationary". As outras duas entradas que o item 4 daquele arquivo pedia — **bilinear discriminator** e
**logistic function** — **ja entraram**
(`GLOSSARY.md:71` e `:72`); so esta faltou.

**Duas correcoes ao proprio texto acima, medidas em 2026-07-30 e registradas aqui porque mudam o que um agente pode
fazer.** Primeira: **nao sao todos prosa publicada**. As frases do Cap. 3 sao (cada uma e substring literal de
`articles/CBIC___MTL/sections/*.tex`), mas a do Cap. 4 **nao e** — e a frase corrigida por errata deste proprio
documento, ja listada no Apendice B, e a fonte PT publicada nao tem nenhuma ocorrencia do termo
(`articles/CoUrb_2026/src`, nove arquivos `.tex`, zero). Segunda: as paginas. O registro anterior dizia pp. 36 e 48,
medidas num build de 100 paginas; o trecho novo da §2.3 acrescenta uma pagina, entao **medido contra o build de defesa
de 101 paginas deste commit**:
§2.3 nova na p. 23, `3_cbic/basis.tex` nas pp. 31 e 32, `3_cbic/method.tex` na p. 37,
`4_courb/methodology.tex` na p. 49, e a linha de errata na **p. 16 do volume suplementar**
(`make extra`, 20 paginas), que nao entra no build de defesa.

**(B) Por que importa.** O `make check` **nao pega isto**: existe um gate de "Pareto" mas ele e informativo e conta
ocorrencias, nao registro. E o termo nao pode ser simplesmente removido — as duas frases sao publicadas, entao tirar o
termo e editar uma frase publicada, com linha no Apendice B.

**(C) O que eu preciso de voce.** Uma decisao, tres saidas:

> **(a)** registrar o termo (uma linha na §4 do `GLOSSARY`, a definicao ja esta escrita na propria
> frase do Cap. 4: *"a point at which some convex combination of the task gradients is zero"*).
> Custo: uma linha, e o documento fica consistente com a propria regra.
> **(b)** trocar o termo nas duas frases publicadas. Custo: duas linhas de errata no Apendice B, e
> voce esta editando prosa publicada por uma questao de vocabulario.
> **(c)** registrar uma excecao explicita para termos que chegam em prosa reproduzida. Custo: uma
> nota no `GLOSSARY`, e a regra deixa de ser fail-closed para essa classe.

> DESICAO: A.

**EXECUTADO EM 2026-07-30, a sua decisao (a).** O termo entrou em `GLOSSARY.md:103` (§4) e `:148` (§6), e com ele tres
outros que a §2.3 passou a usar: **Pareto dominance**, **Pareto optimality** e **gradient conflict**. Cada definicao foi
copiada de um artigo aberto no PDF naquela sessao, com a pagina na propria linha do registro; o razao completo, com a
declaracao exata de convergencia de cada metodo, esta em [`_history/_round9/31_pareto.md`](../_round9/31_pareto.md). O trecho novo
da §2.3 renderiza na **p. 23** do build de defesa de 101 paginas, e o gate agora pega a regressao:
`check_audit_claims.py`
probes `R9-pareto`, `R9-conflict`, `R9-nocount` e `R9-glossary`, cada um validado por sabotagem (reverter a propriedade
e ler rc=1). A anotacao do `VERIFY_LIST` item 4 que esperava
`Pareto-stationary 0` foi corrigida para `2` no mesmo commit, porque a decisao (a) a tornou falsa.

**Uma coisa ficou faltando, e e sua.** Tres dos quatro termos PT nao existem em nenhum lugar deste repositorio, nem na
fonte PT publicada, nem em nenhuma superficie em portugues da dissertacao. Nao os inventei em silencio: entraram
marcados como propostos. `otimalidade de Pareto` **nao** e um deles, e sua propria palavra (l. 98 deste arquivo) e a do
Germano (`articles/[mobiwac]/REVIEW_GERMANO.md:778`).

> **DECISAO SUA:** confirmar ou trocar os tres nao atestados: **dominância de Pareto**, **ponto
> Pareto-estacionário**, **conflito de gradientes**. Custo: uma linha. Nenhuma superficie PT usa os
> quatro hoje (o Cap. 2 e em ingles e o Resumo nao os menciona), entao isto nao bloqueia build nem
> gate; fica registrado para que um tradutor futuro ache uma decisao e nao um vazio.

> **TAMBEM SUA, e e uma questao de errata, nao de vocabulario.** Verifiquei as cinco frases contra a
> garantia que o artigo-fonte de cada uma realmente enuncia. **Todas as cinco enunciam corretamente**,
> e nada foi editado. Uma imprecisao: `3_cbic/basis.tex` (p. 31) diz que o MGDA *"finds Pareto-optimal
> descent directions"*, e o que `sener2018mgda` enuncia (pp. 4 e 6) e uma dicotomia — ou o ponto e
> Pareto-estacionario, ou a direcao *"decreases all objectives"*; a otimalidade de Pareto que o artigo
> reivindica e para o limite superior, sob suposicoes (p. 1). E prosa publicada reproduzida e a
> compressao e a que a literatura de MTL costuma fazer, entao **deixei como esta**. Se quiser corrigir,
> e uma linha de errata no Apendice B, e a decisao e sua.

> **AUTHOR:** Otimo trabalho, pode adicionar essa linha no appendix B, para termos conhecimento desse detalhe menor e
> não deixar passar batido.

---

### ~~2.14 O intervalo de paginas do `nash`: nao da para verificar daqui~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** Entrada `nash` reconstruida do seu paste do PMLR: `pages = {16428--16446}`, `volume = {162}`, `publisher = {PMLR}`, com url.

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


**Origem:** `_history/_round6/VERIFY_LIST.md` item 14, entregue em 2026-07-30 (precedente `standley2020tasks`).

**(A) O que e.** `references.bib` traz `pages = {16428--16446}` para
`@inproceedings{nash}` (Navon et al., *Multi-Task Learning as a Bargaining Game*, ICML 2022). Tentado de novo nesta
sessao, contra as fontes de registro que o sandbox alcanca:

| fonte                            | resposta                                                                                                 |
|----------------------------------|----------------------------------------------------------------------------------------------------------|
| OpenAlex                         | um unico registro, `W4225981399`, tipo **preprint**, venue "arXiv", `first_page` e `last_page` **nulos** |
| Crossref (`query.bibliographic`) | cinco obras, **nenhuma delas este artigo** — nao ha DOI registrado da versao de anais                    |
| `proceedings.mlr.press`          | **fora da allowlist** do sandbox; nao acessado                                                           |

**(B) Por que importa.** Pelo §1 do `AGENT_GUARDRAILS`, um identificador que nao foi aberto na fonte de registro nao
pode ser apresentado como conferido. O campo esta no `.bib` e nao esta verificado.

**(C) O que eu preciso de voce.** Um clique fecha: `proceedings.mlr.press/v162/navon22a.html`.

> **(a)** confirmar o intervalo e ele fica; **(b)** apagar o campo `pages`, que e exatamente o
> precedente que esta bibliografia ja adotou para `standley2020tasks`.

> **AUTHOR:** I get from the website:
> @InProceedings{pmlr-v162-navon22a, title = {Multi-Task Learning as a Bargaining Game}, author = {Navon, Aviv and
> Shamsian, Aviv and Achituve, Idan and Maron, Haggai and Kawaguchi, Kenji and Chechik, Gal and Fetaya, Ethan},
> booktitle = {Proceedings of the 39th International Conference on Machine Learning}, pages = {16428--16446}, year =
> {2022}, editor = {Chaudhuri, Kamalika and Jegelka, Stefanie and Song, Le and Szepesvari, Csaba and Niu, Gang and
> Sabato,
> Sivan}, volume = {162}, series = {Proceedings of Machine Learning Research}, month = {17--23 Jul}, publisher = {PMLR},
> pdf = {https://proceedings.mlr.press/v162/navon22a/navon22a.pdf},
> url = {https://proceedings.mlr.press/v162/navon22a.html}, abstract = {In Multi-task learning (MTL), a joint model is
> trained to simultaneously make predictions for several tasks. Joint training reduces computation costs and improves
> data
> efficiency; however, since the gradients of these different tasks may conflict, training a joint model for MTL often
> yields lower performance than its corresponding single-task counterparts. A common method for alleviating this issue
> is
> to combine per-task gradients into a joint update direction using a particular heuristic. In this paper, we propose
> viewing the gradients combination step as a bargaining game, where tasks negotiate to reach an agreement on a joint
> direction of parameter update. Under certain assumptions, the bargaining problem has a unique solution, known as
> the <em>Nash Bargaining Solution</em>, which we propose to use as a principled approach to multi-task learning. We
> describe a new MTL optimization procedure, Nash-MTL, and derive theoretical guarantees for its convergence.
> Empirically,
> we show that Nash-MTL achieves state-of-the-art results on multiple MTL benchmarks in various domains.} }
> Intresting that in the google scholar use the citation:
> @article{navon2022multi, title={Multi-task learning as a bargaining game}, author={Navon, Aviv and Shamsian, Aviv and
> Achituve, Idan and Maron, Haggai and Kawaguchi, Kenji and Chechik, Gal and Fetaya, Ethan}, journal={arXiv preprint
> arXiv:2202.01017}, year={2022} }

---

### ~~2.15 Tres citacoes NOT-SUPPORTED e um termo banido, todos em prosa publicada reproduzida~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** Caminho A aplicado nas duas arvores de artigo: `standley2020tasks` no lugar da citacao nao atestada, mais as linhas de errata.

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


**Origem:** `_history/_round6/VERIFY_LIST.md` itens 15 e 16, entregues juntos em 2026-07-30 como uma decisao unica.

**(A) O que e.** Quatro pontos, um so tipo de decisao: **nenhum deles pode ser corrigido por um agente**, porque todos
estao em frases publicadas, e mexer nelas gera linha de errata.

| onde                              | o que                                                                       |
|-----------------------------------|-----------------------------------------------------------------------------|
| `3_cbic/method.tex`               | `ruder2017sluice` citado para regularizacao implicita do hard sharing       |
| `4_courb/methodology.tex:173`     | `sun2020go` citado para ciclos temporais revelarem a *funcao* do lugar      |
| `4_courb/methodology.tex:184`     | `belkin2003laplacian` citado para um regularizador hierarquico de embedding |
| `4_courb/methodology.tex:173,184` | **`fclass` em prosa renderizada**, 4 ocorrencias em 3 linhas                |

**(B) Sobre o `fclass`, que ninguem tinha levantado.** O `GLOSSARY.md:73` diz, com todas as letras:
*"In code this column is `spot`, renamed `fclass` at `hgi/preprocess.py:62`; **NEVER write `fclass`
in prose**"*. Varri os 54 `.tex` sem comentarios: `4_courb/methodology.tex` e o **unico** arquivo. E as frases identicas
estao publicadas no CoUrb (`src_en/sections/metodology.tex:109` e `:120`), entao e o mesmo tipo de decisao das tres
citacoes acima. Nenhum gate pega: o de codenomes casa
`B9|v1[1-7]|champion-G|H3-alt|dk_ovl|log_T|substrate`, e `fclass` nao esta na lista.

**(C) O que eu preciso de voce.** Uma decisao por linha, ou uma regra para as quatro:

> **(a)** trocar. As substituicoes sugeridas (`baxter2000model`, `Xu2023`) **ja estao** na
> bibliografia e ja sao citadas para essas alegacoes em outros pontos; para o `fclass`, o termo
> registrado e "fine class". Custo: uma linha de errata no Apendice B por sitio.
> **(b)** manter e registrar. As frases sao do artigo publicado e reproduzi-las fielmente e
> defensavel; a divergencia vai para `LEFT_OUT.md`. Custo: zero no texto.
>
> `ruder2017sluice` merece uma nota: a mesma chave carrega **tambem** uma decisao de metadados (o
> titulo no `.bib` e o do preprint superado, "Sluice Networks..."; o titulo de registro e "Latent
> Multi-task Architecture Learning" e a versao de registro e AAAI 2019,
> `10.1609/aaai.v33i01.33014822`, pp. 4822-4829). Decida as duas juntas para tocar a entrada **uma
> vez** so.

> **AUTHOR:** Vamos de troca em ambas, seguindo o caminho A, modificando os artigos originais e adicionando uma entrada
> no appendix B.

---

### ~~2.16 Quatro artefatos publicados **divergiram** das copias locais (o item 2.2 cobria dois)~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** `origin/mobiwac` esta em `488e4d10`, cujo pai `0288cb70` publica os tres artefatos de reprodutibilidade que faltavam. Lido do remoto.

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


**(A) O que e.** O Apendice A cita treze caminhos `\path{}`. A pergunta "quantos faltam no branch publico" ja teve
**quatro** respostas nesta base (9 de 13, depois 5, depois 4, agora esta). O motivo de todas as anteriores e o mesmo:
`git cat-file -e mobiwac:<caminho>` pergunta *"este CAMINHO esta no branch"*, e a alegacao e *"este ARQUIVO esta no
branch"* — e o branch `mobiwac` **nao tem arvore
`docs/`**, guarda esses artefatos em `analysis_protocol/`. Remedi por **hash**, comparando cada arquivo local com os
blobs do branch:

| classe                                   | n | quais                                                                                                                                                                                                                                                                               |
|------------------------------------------|--:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| no branch, **byte a byte identicos**     | 8 | `folds.py`; `STATISTICAL_PROTOCOL.md`, `JOINT_BEST_RESULTS.md`, `m1_full_output.txt`, `m2_prereg_output.txt` (sob `analysis_protocol/`); `build_phase3_per_fold_transitions.sh`; `score_joint_best.py`; `autocorrelation_ceiling.py` (em `scripts/`, nao `scripts/embedding_eval/`) |
| no branch com **conteudo diferente**     | 4 | `superiority_wilcoxon.py`, `region_match_tost.py`, `m1_stats_n20.py`, `m2_prereg_perfold.py`                                                                                                                                                                                        |
| diretorio (o instrumento nao classifica) | 1 | `stats_n20/`                                                                                                                                                                                                                                                                        |

**Nada esta faltando.** Quatro artefatos publicados **divergiram**:

| arquivo                   | local | no branch | linhas diferentes |
|---------------------------|------:|----------:|------------------:|
| `superiority_wilcoxon.py` |   147 |       126 |                37 |
| `region_match_tost.py`    |    74 |        74 |                 2 |
| `m1_stats_n20.py`         |   411 |       335 |                84 |
| `m2_prereg_perfold.py`    |   214 |       222 |                36 |

**(B) Por que importa.** O seu item **2.2 ja reservou exatamente esta decisao a voce**, mas para **dois** arquivos
(`m1_stats_n20.py` e `m2_prereg_perfold.py`). Sao **quatro**. Substituir um artefato publicado por uma versao local
divergente e decisao de autor, nao faxina — nao toquei em nada.

**(C) O que eu preciso de voce.** Por arquivo, ou uma regra para os quatro:

> **(a)** publicar a versao local, se ela e a correta (um commit seu no branch `mobiwac`);
> **(b)** deixar como esta, se a versao publicada e a que gerou os numeros do artigo — que e o caso
> a favor de deixar quieto, e o mais provavel para `region_match_tost.py`, com 2 linhas de diferenca.
>
> A prosa do Apendice A **nao depende disto**: ela ja diz que os scripts estatisticos *"are part of
> the working repository and are supplied on request"*, o que nenhuma das leituras acima torna falso.

> **AUTHOR:** Vamso publicar as alterações na branch do mobiwac.

**APLICADO — 2026-08-02.** Push feito em `origin/mobiwac`, commit `488e4d10` (pai `0288cb70`), rodado de dentro do
worktree `.temp/mobiwac` (o clone `.tmp/mobiwac_pub_96069` do `45_author_rulings.md` nao existe mais; recomparei do
zero).

**Nao foi a copia byte a byte dos quatro arquivos locais — tres precisaram de adaptacao, um ficou de fora.**
`m1_stats_n20.py` local tinha `REPO = Path(__file__).resolve().parents[5]`, correto so porque o arquivo mora 6 niveis
abaixo da raiz no monorepo; colado sem alteracao nos 2 niveis do branch, o
`REPO` sairia da arvore do repositorio e quebraria todo caminho do script — nao era so um problema de
`docs/` vs `analysis_protocol/` na prosa, como o relatorio anterior descreveu, era o script inteiro.
`region_match_tost.py`, chamado de "caso limpo" no relatorio anterior, tambem apontava para um caminho
`docs/studies/...` inexistente no branch; corrigi para `analysis_protocol/STATISTICAL_PROTOCOL.md`.
`m2_prereg_perfold.py` publicado **ja estava mais correto que o local** — indirecao `RESULTS_ROOT` + caminhos
`analysis_protocol/` que o local tinha perdido, regredindo para caminhos `docs/...` que nao existem no branch — publicar
o local ali teria piorado o script publicado, entao **fiquei fora dele**; nao e uma decisao pendente, e uma correcao ao
plano.

Os tres arquivos tocados (`m1_stats_n20.py`, `superiority_wilcoxon.py`, `region_match_tost.py`)
receberam o conteudo que o proprio `DEVIATION_LOG.md` do branch (entrada D-4, ja publicada) cobrava como pendente — a
rotulagem "post-hoc" das celulas de superioridade de regiao — com os caminhos adaptados ao layout do branch, nao colados
do monorepo. `m1_stats_n20.py` tambem ganhou a secao M1-FULL (arms CA/TX em n=20 + a familia Holm de 6 datasets), que so
existia na copia local.
`py_compile` limpo nos tres antes do commit; nenhum dos scripts foi executado neste branch (os dados sob
`docs/results/...` que `SWEEP`/`P1`/`TSV`/`SIDE` leem nao estao publicados aqui — isso ja era verdade antes da minha
edicao, para os campos que ja existiam).

---

### ~~2.18 Um `refs/notes/commits` foi para o `origin` sem eu ter pedido, e a decisao de remover e sua~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** `git ls-remote origin | grep -c refs/notes` = **0**. A ref saiu do publico.

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


**Medido em 2026-07-30, nada foi alterado no remoto.** `git ls-remote origin | grep notes` retorna
`refs/notes/commits` apontando para `99c0a34b1a`, identico ao ref local. Ele **esta publicado**.

**Como foi.** Nenhum comando meu pediu isso. O git tem uma configuracao (`notes.rewriteRef` /
`remote.origin.push` com refspec ampla, ou `push.default` com notes habilitados) que empurra
`refs/notes/*` junto de um push comum; o stderr de um dos meus pushes mostrou
`* [new reference] refs/notes/commits`. Um sub-agente reportou isso por conta propria, incluindo o fato de ter
subestimado o escopo na primeira vez que descreveu.

**O que ha nesses notes: 15 anotacoes, e todas sao correcoes de mensagens de commit minhas.** Cada uma diz que uma frase
de commit era falsa e qual e a medicao correta — a convencao deste repositorio para nao reescrever historia. Sao,
literalmente, o registro dos meus proprios erros.

**Por que provavelmente nao e grave — agora medido em TODOS, nao em seis.** A primeira versao deste item afirmava "os 14
commits anotados nao estao em nenhum branch do origin" a partir de uma sondagem que rodou com `head -6`: **oito nunca
foram checados**, e a recomendacao abaixo repousava nessa generalizacao. Re-medido sem o `head`, e a contagem tambem
estava errada — sao **15** notes, nao 14:

```
for h in $(git notes list | awk '{print $2}'); do
  git branch -r --contains "$h" | grep -c "origin/"; done
# checked=15  on_public_branch=0
```

**15 de 15 verificados, zero em qualquer branch do `origin`.** Sao objetos alcancaveis apenas pelo ref de notes, nao
historia visivel de nenhum branch publico. Quem clonar o repositorio **nao recebe notes por padrao** (precisa de
`git fetch origin refs/notes/*:refs/notes/*`).

> **DECISAO SUA, e eu nao vou tomar por voce.** Tres opcoes:
> 1. **Deixar.** Elas documentam correcoes honestas e nao aparecem em clone normal. Custo zero.
> 2. **Remover do remoto:** `git push origin :refs/notes/commits` — apaga o ref publicado e mantem os
>    notes locais. Uma linha, reversivel (basta empurrar de novo).
> 3. **Impedir que volte:** `git config --local notes.rewriteRef ""` e conferir
>    `git config --get-all remote.origin.push`.
>
> Eu recomendo a **2 + 3** se este repositorio for ficar publico com a defesa, e a **1** se ele
> permanecer privado. Nao executei nenhuma delas porque mexer em ref publicado e sua alcada.

> **AUTHOR:** 2+3

---

### ~~2.19 Quatro numeros do registro de fechados nao reproduzem; um tem tres respostas~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** `src_utils/WORDCOUNT_CONVENTION.md` fixa a convencao que voce escolheu (310/271) e diz por que as outras duas contagens diferem.

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


**O que e.** O item 1.2 do `_history/_archive/PENDENCIAS_RESOLVIDOS.md` tem nove linhas; cinco conferem. Das quatro restantes,
nenhuma reproduz da arvore viva: comentarios medem 3.614 linhas contra 1.269 afirmadas, o `preamble.tex` tem 14
placeholders contra 3, e `geometry`/`linespread` nao estao nesse arquivo. **Sao velhos, nao errados** — medidos na
rodada 6, contra uma arvore que desde entao ganhou um apendice e perdeu o `0_main.tex`. O defeito duravel: nenhum
registra **contra qual estado da arvore**
foi tomado, e medicao sem isso so pode ser re-tomada, nunca re-conferida.

> **DECISAO SUA, e e uma so:** qual convencao de contagem de palavras vale para o Resumo e o Abstract
> no deposito? Ha **tres** respostas (310/271 no relatorio, 312/277 de uma esteira, 345/307 do meu
> instrumento) porque ha tres convencoes. Um numero impresso no seu deposito e seu. Diga a convencao,
> eu fixo uma, aplico, e ponho o comando no arquivo.

> **AUTHOR:**  310/271 no relatorio, eu não entendi porque há 3, mas o quantidade de plavras no resumo hoje são essas.

---

### ~~2.20 O Cap. 4 italiciza ingles corriqueiro 153 vezes, e este item DESAPARECEU do tracker sem decisao~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** Opcao 2 aplicada: `\textit` na prosa viva do Cap. 4 = **48** (eram 157 no fonte em `5c074a2a`). Os sobreviventes sao os 7 nomes de categoria, nomes de modelo e substantivos proprios.

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


> **ESTE ITEM FOI PERDIDO, nao resolvido.** Ele existiu ate `1ef83867` (2026-07-28) e saiu do arquivo
> naquele commit **sem ir para o `_history/_archive/PENDENCIAS_RESOLVIDOS.md` e sem uma decisao sua**. O titulo
> dizia explicitamente *"e uma decisao sua"*. Reencontrado em 2026-07-30 varrendo as 63 revisoes do
> tracker por titulo, nao por numero — porque os numeros foram reciclados em tres renumeracoes.

**Re-medido agora, na prosa viva (comentarios removidos), e os numeros continuam praticamente iguais aos de dois dias
atras:**

| capitulo   | `\emph`/`\textit`  |
|------------|--------------------|
| Cap. 1     | 6                  |
| Cap. 2     | 6                  |
| Cap. 3     | 23                 |
| **Cap. 4** | **153** (eram 155) |
| Cap. 5     | 10                 |
| Cap. 6     | 0                  |

Mais italicizados no Cap. 4: `embedding` 18, `baseline` 16, `encoders` 15, `encoder` 14,
`embeddings` 12, `check-ins` 7. **E inconsistente consigo mesmo** — a mesma palavra aparece nas duas formas: `encoder`
italico 14 / romano 8, `encoders` 15 / 7, `baseline` 16 / 4, `embedding` 18 / 1.

**A causa e legitima, a consequencia nao.** Isso vem do artigo em portugues, onde italicizar estrangeirismo e a pratica
correta. Num capitulo **em ingles** a mesma marcacao nao marca mais estrangeirismo: le-se como enfase numa palavra que
nao tem nenhuma, e o proprio capitulo se contradiz.

> **DECISAO SUA, e continua sendo. Tres caminhos:**
> 1. **Deixar como esta.** O Cap. 4 e capitulo de artigo publicado; a marcacao veio de la. Custo zero,
>    mas um leitor em ingles ve enfase onde nao ha.
> 2. **Remover o italico de vocabulario corrente** (embedding, baseline, encoder e plurais), mantendo
>    italico so em termo tecnico em primeiro uso. ~90 substituicoes, mecanicas, e eu registro como
>    partida de errata no Apendice B por ser capitulo publicado.
> 3. **Uniformizar sem remover:** escolher uma forma por palavra e aplicar. Resolve a contradicao
>    interna sem mudar a densidade de italico.
>
> Eu recomendaria a **2**, e nao aplico nada sem voce: e prosa de artigo publicado e o proprio item
> dizia que a decisao e sua. `WRITING_LAW` nao cobre italico de estrangeirismo em capitulo traduzido,
> entao nao ha regra para eu invocar.

> **AUTHOR:**  2.

---

### ~~2.23 Cinco itens RECOMMENDED das revisoes que eu nao apliquei~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** R-3, R-5 (a frase longa caiu para 17 palavras), R-6 (13 referencias ao apendice) e EX-6 aplicados. **EX-9 SUPERSEDIDO** pela sua propria revisao, por sua decisao de 2026-08-02: voce mandou nao aplicar e depois reescreveu as quatro frases na sua passada de leitura. O probe `A23-EX9` foi reapontado, porque vigiava `"Pareto front"` e passava enquanto a decisao era desfeita.

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


**(A) O que e.** Ficaram por decisao de escopo, nao por esquecimento. Cada um tem quote e pagina no relatorio citado.

| id   | onde     | o que                                                 | por que nao apliquei                        |
|------|----------|-------------------------------------------------------|---------------------------------------------|
| R-3  | p.26-27  | §2.5 nao retoma a pergunta que §2.3 deixa aberta      | mexe em prosa que nao mudou nesta rodada    |
| R-5  | p.23     | uma frase de 66 palavras com tres pontuacoes fortes   | reescrita de estilo, sua chamada            |
| R-6  | p.23     | so uma referencia no corpo aponta para o Apendice F   | pode ser deliberado                         |
| EX-6 | p.101    | uma comparacao entre datasets que o texto nao precisa | `40_readability` e `42_excellence` divergem |
| EX-9 | p.23, 99 | densidade de figuras de linguagem                     | OPTIONAL nos dois relatorios                |

**(B) O que ja foi feito.** Triados e medidos; nada aplicado.

**(C) O que eu preciso de voce.** Diga quais valem e eu aplico. Nenhum e um erro de fato.

> **AUTHOR:** Aplique o R-3,5,6 e o EX-6, seguindo a recomendação do 42_excellence, não aplique o EX-9.

---

### ~~2.25 O que sobrou da rodada 9c, e as duas coisas que dependem de voce~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** sua propria decisao: "Done!".

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


**(A) O que e.** As suas catorze decisoes de 2026-07-30 foram aplicadas e conferidas uma a uma no PDF renderizado. O
ledger completo, com a evidencia de cada linha, esta em `_history/_round9/47_applied_check.md`:
**28 linhas** (13 decisoes mais os 15 pontos numerados do apendice), das quais **25 aplicadas**, **2 bloqueadas** e **1
que nao pedia nada** (a sua 2.8, "nada aqui"). Vinte delas agora tem sonda em
`check_audit_claims.py`, validada por sabotagem, entao uma edicao futura que desfizer uma das suas mudancas quebra o
gate em vez de chegar na banca em silencio.

**(B) O que ficou bloqueado, e por que nao e escolha minha.**

1. **2.16, publicar os quatro artefatos divergentes.** Preparado, nao empurrado: o helper de credencial e interativo
   neste sandbox e um push nao pode ser feito daqui. Os comandos exatos estao no
   `_history/_round9/45_author_rulings.md`, no item 2.16. Nenhum push foi fabricado.
2. **2.18, o `refs/notes/commits` no `origin`.** A sua decisao foi "2+3"; uma das duas metades esta aplicada e a outra
   depende de uma operacao no remoto. Detalhe no mesmo relatorio.

**(C) O que eu preciso de voce.** Nada nas 25 aplicadas, a nao ser que discorde de alguma. Nas duas bloqueadas, uma
decisao sua sobre quando rodar os comandos.

> **DECISAO SUA:** Done!

---

### ~~2.26 A persona 15 rodou por ultimo, e o achado que vale mais que os quatro REQUIRED~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** R15-09 e R15-10 aplicados em 2026-08-02: "The figure shows two patterns." e "Answering that question needs the same diagnostic". `check_register` e `check_process_narration` em rc=0.

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


**(A) O que e.** Voce pediu a persona 15 no fim de tudo, com as instrucoes que voce mesmo reescreveu (`89b7eca1`). Ela
leu **873 sentencas em 12 unidades** nos PDFs renderizados e devolveu 4 REQUIRED, 4 RECOMMENDED e 2 OPTIONAL. Relatorio:
`_history/_round9/48_readability_final.md`.

**(B) O que foi aplicado, tudo conferido por mim antes.**

- **R15-01 estava indo para a banca.** `Appendix ??` renderizava na p. 11 do volume suplementar: um
  `\ref` para um rotulo que vive no volume PRINCIPAL. Referencia entre volumes nao resolve, porque os dois documentos
  tem `.aux` separados por construcao. O log de build carregava o aviso e ninguem lia.
- **R15-02:** o volume suplementar citava um titulo que nao e o titulo da dissertacao, a tres paginas da propria capa,
  que traz o certo. Agora aponta para a capa em vez de repetir a string.
- **R15-03:** `region head` era o ultimo do tipo (medido em toda a prosa viva: "region output" 7, "region head" 1). Mais
  o pronome relativo escrito.
- **R15-04:** a primeira frase com ideia do apendice empilhava duas oracoes reduzidas terminando em preposicao solta.
  Nao estava entre os seus quinze pontos e nao mudou desde a versao que voce leu, que e exatamente a classe que voce
  disse que passa pelas varreduras.
- **R15-06, o seu proprio banimento:** "It now covers" datava o documento contra uma versao que o leitor nunca viu.
  **R15-07:** o Abstract e o Resumo abriam com 24 palavras de protocolo antes do sujeito, na pagina mais lida; resultado
  primeiro agora, nos dois, com todo numero preservado. **R15-08:** virgula entre sujeito e verbo.

**(C) O que eu preciso de voce.** Nada. As duas OPTIONAL (R15-09, R15-10) ficaram sem aplicar e estao descritas no
relatorio; se quiser, aplico.

> **DECISAO SUA:** Aplique o R15-10 e o R15-09

---

### ~~5.6b A premissa da sua decisao 5.6 nao e o que os arquivos mostram — resolvi imprimindo AS DUAS datas~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, arquivado deste tracker.** A prosa carrega so as datas do banco, ['2009', '2010', '2011'], como voce mandou; os marcadores de sign-off que voce liberou sairam do LaTeX.

*Auditado item por item contra a arvore em `45c75611` + a arvore de trabalho, medindo o estado do documento em vez de ler o proprio cabecalho do item. O bloco original abaixo esta preservado verbatim, incluindo a sua decisao.*


**Medido em 2026-07-30, nos cinco parquets que este trabalho consome.** Sua decisao no 5.6 foi *"Busque pelo que o
artigo original cita e vamos usar isso em ambos. Inclusive ambos usaram o mesmo recorte nao houve diferenca."* A
primeira metade foi cumprida: o `cho2011gowalla` foi aberto em primeira mao (PDF dos proprios autores, Secao 2, p.2) e
ele diz **Fev 2009 a Out 2010**.

**A segunda metade nao se sustenta.** Os cinco estados usados nao param em Out 2010:

| estado     | primeiro check-in | ultimo check-in | n         |
|------------|-------------------|-----------------|-----------|
| Alabama    | 2009-03-18        | 2011-07-27      | 113.846   |
| Arizona    | 2009-03-26        | 2011-07-04      | 236.450   |
| Florida    | 2009-03-13        | 2011-08-11      | 1.407.034 |
| Texas      | 2009-01-21        | **2011-08-16**  | 4.089.892 |
| California | 2009-01-24        | 2011-08-14      | 3.171.380 |

Uniao: **2009-01-21 a 2011-08-16** — dez meses depois da janela que o artigo declara.

**Por que isso importa e nao e frescura.** A frase esta no Cap. 6 sob a limitacao *"Data vintage"*. Ali o leitor le a
data como **a safra dos dados que voce usou**, nao como uma nota sobre o que outro artigo coletou. Imprimir so Fev
2009–Out 2010 subestimaria o proprio corpus em dez meses.

**O que eu fiz.** A frase agora carrega as duas datas: o que os autores relatam, e o que a extracao daqui abrange, com a
medicao completa e o comando no comentario de proveniencia do
`6_conclusion.tex`. Nao e uma correcao da sua decisao — voce estava decidindo **qual fonte citar**, e essa parte esta
cumprida.

> **DECISAO SUA.** Se voce preferir imprimir **so** a janela do artigo, a clausula depois da virgula e
> a que sai, e eu removo. Marcado com `[NEEDS SIGN-OFF: PENDENCIAS_RESOLVIDOS 5.6 (arquivado 2026-07-30), round8]` no
> fonte.

> **AUTHOR:** Vamos usar só as datas que encontramos no database de 2009 a 2011, pode omitir que no artigo eles comentam
> que é de 2009 a 20010. O need sing-off assim como os demais já resolvidos que estão no latex pode ser removidos não
> precisam fica lá. Se quider documentar isso tem que ser em algum lugar do src_util.


---

## Arquivados em 2026-08-02 (segunda passagem: 2.21 e 2.24, e o §5 retirado)

### ~~2.21 O segundo ponto do seu orientador: como os termos entram~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02.** Voce identificou o termo: *"`license the verbs` em fundamentacao teorica. Foi o
unico termo que ele marcou e comnetou para ter cuidado com o termos."* Medido em todos os 54 `.tex` vivos:
**o termo ja nao estava no Cap. 2** — a sua propria revisao dissolveu aquela passagem. A metafora sobrevivia
em tres lugares na prosa viva (duas vezes em `apx_f_cosine.tex`, uma em `apx_c_ai_disclosure.tex`) mais a
glosa da §4 do `GLOSSARY`. Trocada por `supports` nos quatro. **Os usos em `apx_e_ethics.tex` ficaram**: ali
`license` e licenca de software de verdade (Apache 2.0), nao a metafora — nao sao desta classe.

*Bloco original preservado verbatim, incluindo a sua decisao.*


**O que e.** Ele escreveu *"soa um pouco estranho o jeito que alguns termos sao inseridos (marquei alguns la)"*. O
buraco concreto que o item registrava — o revisor de estilo nunca ter lido o
`articles/[mobiwac]/GLOSSARY.md`, que vence para o Cap. 5 — esta **fechado**: revisor re-rodado em 28/07, as tres
proibicoes da §3 ausentes, as 28 da §4 medidas (22 ausentes, 6 dentro da condicao, e **uma violacao real corrigida**:
`region head` -> `region output`).

**Nao medido, e nao vou dizer que esta:** §6, §7 e §8 do glossario sao julgamento de estilo, sem grep que decida.

> **DECISAO SUA, pequena:** ele marcou termos num PDF que **eu nao tenho**. Me passe as marcacoes e eu
> trato uma por uma.

*Medicao termo por termo: [`_history/_round8/29_pendencias_detail.md`](../_round8/29_pendencias_detail.md).*

> **AUTHOR:** `license the verbs` em fundamentação téorica. Foi o unico termo que ele marcou e comnetou para ter cuidado
> com o termos.

---

### ~~2.24 Um `towards` britanico em prosa publicada do CBIC, e a saida e uma linha de errata~~ — RESOLVIDO 2026-08-02

**RESOLVIDO em 2026-08-02, nas duas metades.**

**(1) O ponto e a aspa.** Sua decisao: *"Vamos deixar do lado de fora seguindo a norma: ABNT (NBR
10520:2023). Cocuemnte isso no WRITING_LAW.md."* Registrado na §1 do `WRITING_LAW`, com a razao de que a
norma de deposito vence a convencao americana da casa e citando o precedente que ja existia (legenda de
tabela acima, tambem ABNT contra o estilo americano). O gate 25 passou a cobrir a regra.
**Voce isentou a citacao de frase completa** — o ponto dela e do autor citado — e a isencao separou os
tres sitios com precisao: `errata_wording.tex` carrega uma frase completa (*"Also, it is important to
notice..."*) e **ficou**; os dois de `errata_scope.tex` eram **fragmentos** cujo ponto era da frase
hospedeira, e foram movidos para fora. As outras 14 ocorrencias ja estavam conformes.

*Duas falhas minhas ao construir esse gate, ambas do mesmo tipo:* escrevi o padrao **invertido** (casava a
forma correta e ignorava a errada, entao o gate ficava **verde** numa arvore com tres violacoes); e depois
coloquei a regra na familia de grafia, cujo loop le o texto **com as citacoes mascaradas**, de modo que uma
regra sobre a pontuacao da propria citacao nao podia disparar. Pego virando um sitio real para a forma
americana e vendo o gate calado. Corrigido, validado nos dois sentidos e fixado em self-test, positivo e
negativo.

**(2) O `towards`.** Sua decisao: **opcao (b), deixar como esta.** E prosa publicada do CBIC e a unica forma
britanica em toda aquela fonte. A entrada do `OPEN_REGISTER` do gate passa a ser **o registro permanente
dessa decisao**, com a instrucao explicita de nao "corrigir" numa varredura futura. Ela continua la porque e
auto-retirante: se a frase sair do capitulo, o gate **falha** e pede a remocao da entrada, entao a decisao
nao apodrece em isencao silenciosa.

*Bloco original preservado verbatim, incluindo a sua decisao.*


**O que e.** Sua queixa 8 do item 2.22 (o `needs saying plainly`) gerou a lei de registro e o gate 25
(`check_register.py`). Varridos os 54 `.tex` vivos mais o `references.bib`, **doze linhas de achado em onze sitios**
(uma frase pode disparar duas regras): **5** grafias britanicas, **1** construcao britanica (a sua) e **6** formas de
fraseado. **Seis eram nossas e foram corrigidas**; **cinco** estao no Apendice F e a outra esteira ja as fechou.
**Sobrou uma, e ela e sua**, porque esta em prosa publicada. (As cinco do apendice do cosseno estao contadas aqui como
"Apendice F", que era a letra quando esta varredura mediu; a outra esteira aplicou o seu ponto 0 e **reletrou para
Apendice D** no commit `4eea637a`. O arquivo continua `chapters/apx_f_cosine.tex` e o gate e ancorado no caminho, nao na
letra.)

**A conferencia fecha nos dois sentidos**, e as tres parcelas estao escritas como palavras de proposito:
seis linhas corrigidas nesta esteira, cinco fechadas pela esteira do apendice do cosseno e uma aberta para voce, que
somam as doze. Escrita com algarismos e um sinal de igual, esta frase ja se quebrou duas vezes num reflow, deixando o
`12.` no inicio de uma linha, onde o markdown o le como item de lista numerada e a aritmetica desaparece da pagina.

*(Este bloco dizia **nove ocorrencias** e "quatro/quatro/uma". Estava errado, e o erro foi pego por revisao, nao por
mim: eu somei categorias de cabeca em vez de contar as linhas que o instrumento imprime. Medido rodando o gate sobre a
arvore do `06529ed6` com o `OPEN_REGISTER` vazio, para que nada fique retido e todo achado imprima; o gate sai com
`rc=1` e conta seis achados de grafia ou construcao britanica mais seis de fraseado, doze linhas ao todo. O detalhamento
linha por linha, com o comando, esta na secao 1.3 do relatorio.)*

`chapters/3_cbic/conclusion.tex`, p. 43 do build de defesa:

> "The representation learned by the shared layers might have become biased **towards** the features
> required for the simpler, static classification task"

**Medido, nao suposto:** a frase e substring literal de
`articles/CBIC___MTL/sections/conclusion.tex:13`, e este `towards` e a **unica** forma britanica em toda a fonte
publicada do CBIC (zero `-our`, zero `-ise`, zero `whilst`); CoUrb-EN e MobiWac nao tem nenhuma.

**Por que nao apliquei.** Pela NORTH_STAR §5.7, mudar uma palavra de prosa publicada e decisao sua, e esta e questao de
vocabulario, nao de correcao. O gate mantem o achado **aberto por nome** e falha se a entrada ficar obsoleta, entao nao
se perde em nenhuma das duas saidas.

> **DECISAO SUA, e e uma linha:** (**a**) trocar por `toward` e acrescentar uma linha em
> `tables/cbic/errata_wording.tex`, que ja carrega **quatorze** linhas exatamente desta classe
> ("By leveraging shared information" -> "By using shared information"), todas sob a legenda *"claim
> strength unchanged or reduced, never raised"*; a troca nao muda alegacao nenhuma. (**b**) deixar
> como esta, e a entrada do registro aberto do gate passa a ser o registro permanente da decisao.

**Um segundo ponto, tambem seu, e eu deliberadamente NAO fiz gate dele.** O ponto final fica **fora**
da aspa de fechamento em **13 sitios** (`tables/cbic/errata.tex` 5, `tables/courb/errata.tex` 3,
`chapters/3_cbic/method.tex` 2, `tables/cbic/errata_wording.tex` 2, `chapters/apx_b_errata.tex` 1). O estilo americano
poe dentro. **Todos os 13 estao em tabelas de errata onde a string citada e a evidencia**, e mover um ponto para dentro
de uma citacao altera a citacao. E decisao sobre a convencao da errata, nao erro de grafia. Se quiser, e mecanico e faco
os 13 numa passagem.

*Forense: [`_history/_round9/44_register_law.md`](../_round9/44_register_law.md) (a varredura com contagem por arquivo, as regras, e
o transcrito de validacao do gate nos dois sentidos).*

> **AUTHOR:** Vamos deixar do lado de fora seguindo a norma: ABNT (NBR 10520:2023). Cocuemnte isso no
> WRITING_LAW.md.

---

## Encerrados na rodada de 2026-08-03 — o §6 inteiro (`CONSIDERATIONS.md`)

Os vinte e cinco itens abaixo saem do `PENDENCIAS.md` §6 porque **todos foram respondidos por ele**, a
maioria com a resposta escrita no proprio bloco. Cada um mantem o texto integral e ganha o motivo da saida
no topo, como manda o cabecalho do `PENDENCIAS.md`. **A numeracao NAO foi reaproveitada** e o §6 nao foi
renumerado: comentarios no fonte citam estes numeros, e um buraco e melhor que um ponteiro errado.
**Fica no `PENDENCIAS.md` apenas o §6.26**, cuja segunda metade continua viva (a renomeacao dos indices da
D13, AD-7, que entra no capitulo quando a D13 for tocada).

---

### ~~6.1 Onde eu discordo do revisor — tres itens, e a decisao e sua~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** as suas tres respostas estao no proprio bloco (voce respondeu item a item).

#### FAB-17 — the fourth-task paragraph is confusing and could go

**Citacao:** exata — `chapters/1_introduction.tex:61-66`. **Renderiza em:** 1_introduction.tex:61-64

**Minha leitura:** DISAGREE, and this is the one I would push back on. The paragraph he would delete is the
AVAL-signed-off task-pair acknowledgment (a) and the three-legged task-choice defense (b) recorded in NORTH_STAR 6 Ch.1
beat 4. It exists because a prior review round required the document to state plainly that the task pair EVOLVED and to
defend the task choice. Deleting it reopens both. If it is confusing, the fix is to split it into two shorter sentences,
not to remove it.

1. **Remover o paragrafo, como ele pede** — REABRE dois pontos com aval registrado (NORTH_STAR §6 Ch.1 beat 4 (a) e
   (b)): o reconhecimento de que o par de tarefas MUDOU, e a defesa da escolha das tarefas. Uma rodada anterior exigiu
   os dois
2. **Dividir em duas frases curtas e manter o conteudo** — atende a queixa real (confusao) sem reabrir o aval; ~30 min
3. **Levar a ele com o registro do aval na mao** — ele decide sabendo o que o paragrafo protege

> **DECISAO SUA:** Eu também discordo, se compravarmos que esse pragrafo está correto. Ele fala que uma quarta tarefa
> aprece no artigo ? Isso está errado, CBIC e COURB: poi category classification and next-category, já no mobiwac:
> next-region and next-category, ou seja são 3 tarefas a um todo. Além disso eu acho que a frase:
> `with the static classification of a place's category`, para explicar a tarefa de classificação de categoria de um poi
> desconhecido, não está bem explicada é esta confusa. Isso é outro ponto a tarefa no 2 primeiros artigos era
> classificação de categoria de um poi deconhecido, avalise se o restante do texto está tratando isso dessa forma.
> Também temos que avaliar se esse error de 4 tarefas não aparece em outros lugares.

#### FAB-27 — the table's chapter references are wrong

**Citacao:** exata — `tables/frame/lineage.tex:5-8 (caption) -> Table 2.1`. **Renderiza em:**
tables/frame/lineage.tex -> Table 2.1

**Minha leitura:** disagree as stated; a real problem underneath. Checked directly: ch:courb -> 4 and ch:mobiwac -> 5 in
build/main-aux, both resolve, nothing dangling. What is wrong is that ONE column mixes bracketed citations and chapter
pointers, so the chapter numbers read as mis-rendered citations. Also ST-MTLNet HAS a published record
(paiva2026stmtlnet, already in the bib and cited in Ch.4/Ch.5) and the table shows it only as 'Chapter 4'. Two fixes are
possible and they differ in cost.

1. **So dividir a coluna em "Reference" e "Where in this dissertation"** — resolve a ambiguidade real (a coluna
   mistura [41] com "Chapter 4"); ~1h com rebuild
2. **Dividir a coluna E citar o `paiva2026stmtlnet` na linha do ST-MTLNet** — a entrada JA existe no .bib e ja e citada
   nos Cap. 4 e 5; a tabela hoje mostra so "Chapter 4" para um artigo publicado com DOI
3. **Perguntar a ele primeiro** — as `\ref` estao corretas (`ch:courb`->4, `ch:mobiwac`->5, lidas do build); se ele viu
   `??` num PDF, era .aux velho, nao erro de fonte

> **DECISAO SUA:** Vamos deixar em como está, voce já corrigiu o que precisava. Algo que temos que tomar cuidado e que a
> tabela está passando da margem.

#### GER-02 — DGI and HGI are presented as counterpoints, and they are not

**Citacao:** parafrase (ele descreveu, nao citou). **Renderiza em:** 2_fundamentals.tex:143-165 + Table 2.1

**Minha leitura:** partially disagree, and the disagreement is mine to state, not to settle. The prose already says HGI
'builds directly on' DGI and 'extends' the objective, which is inheritance language, not contrast. I do not think the
paragraph sets them against each other. His reading has a real cause though: the lineage table lists them as adjacent
rows under 'What it added'. Also his framing 'HGI e uma aplicacao' would UNDER-credit Huang et al., and would sit badly
beside our claim that Check2HGI extends the same hierarchy.

1. **Uma clausula explicitando os papeis (DGI = o objetivo; HGI = o objetivo instanciado na hierarquia
   POI-regiao-cidade)** — atende a causa real da leitura dele sem mexer numa descricao correta; ~20 min
2. **Reescrever como ele sugere, chamando o HGI de "aplicacao"** — EU DISCORDO: sub-credita Huang et al., que contribuem
   um objetivo novo, e fica mal ao lado da nossa propria frase de que o Check2HGI *extends* a mesma hierarquia
3. **Nao mexer** — a prosa ja diz "builds directly on" e "extends"; mas dois leitores tropecaram

> **DECISAO SUA:** De fato isso já tá bem explicado no texto, então não vamos mexer. Algo que podemos melhorar e
> explicação do hgi e como ele
> funciona, vide que essa é uma das aboardagens mais importantes para as contribuições da dissertação.

---

### ~~6.2 Onde o pedido colide com uma regra de honestidade do proprio documento~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** voce respondeu os cinco pontos no proprio bloco.

#### FAB-09 — simplify the results description; keep it higher level

**Citacao:** ALTERADA — `content.tex`. **Renderiza em:** content.tex:91-94

**Minha leitura:** partly satisfied. The joint-best gloss he wanted simplified is GONE from the Resumo; the numbers (5,3
a 9,4) and the TOST clause remain. Cutting them further trades honesty rules (every number carries its convention)
against his readability ask.

1. **Cortar a faixa 5,3-9,4 e o TOST do Resumo, deixando "supera nas seis" e "equipara-se nas outras duas"** — atende o
   pedido; MAS o WRITING_LAW §3 exige que todo numero carregue convencao, e que "equipara-se" venha com o teste
2. **Manter os numeros e cortar so a glosa de joint-best** — ja feito: a glosa saiu na reescrita de 28/07
3. **Manter como esta** — contraria o pedido dele

> **DECISAO SUA:** Ele revisou uma versão antiga do Resumo, essa nova versão já cumpre bem o intuito final. Vamos manter
> em como esta.

#### FAB-22 — the result detail does not belong in the introduction

**Citacao:** exata — `chapters/1_introduction.tex:130-133`. **Renderiza em:** 1_introduction.tex:130-132

**Minha leitura:** his call: it collides with an honesty rule. He wants the result detail out of the introduction.
WRITING_LAW 3 requires every number to carry its reference point and convention, and the region verbs to be bound to
their tests. Dropping 'four of six ... TOST' from the intro removes exactly that binding, so the sentence must either
keep the test or stop making the comparative claim.

1. **Tirar "quatro dos seis ... TOST" da introducao** — atende; MAS remove exatamente a amarra verbo-teste que o
   WRITING_LAW §3 exige, e a frase continua afirmando comparacao
2. **Tirar a comparacao TODA da introducao e deixar so a pergunta** — coerente: sem afirmacao, sem teste
3. **Manter** — contraria o pedido

> **DECISAO SUA:** Eu acho que não precisamos tirar tudo, o ponto e o excesso de inforamção. Podemos comentar algo
> somente sobre o fatoq ue os experimento foram realizados em 5 estados do estados unidos e um dataset non-U.S para
> metritos de generalização. Também, podemos comentar que usamos métodos estatisticos para comprovar essa difernça.
> Enfim a ideia e ser mais deireto. Não remover tudo.

#### FAB-03 — put the open question in the present tense

**Citacao:** ALTERADA — `content.tex`. **Renderiza em:** content.tex:76

**Minha leitura:** agree on substance; the sentence changed. He asked for the present tense. The live wording is
'permanecia em aberto' (imperfect), not the 'era' he quoted. Present tense would read 'permanece em aberto'. It is a
claim-time question: the document elsewhere time-indexes CBIC/CoUrb conclusions, and the abstract saying 'permanece'
asserts the question is open TODAY, after the dissertation answered it.

1. **Presente: "permanece em aberto"** — uma palavra, nos dois idiomas; MAS afirma que a pergunta esta aberta HOJE,
   depois de a dissertacao responder
2. **Manter o imperfeito "permanecia"** — preserva a regra de indexacao temporal do WRITING_LAW §3; contraria o pedido
   dele
3. **Reformular: "era uma questao aberta no inicio desta pesquisa"** — explicita o ponto de referencia, atende o sentido
   dele sem a leitura de presente

> **DECISAO SUA:** Manter o imperfeito "permanecia"

#### FAB-18 — put the open question in the present tense

**Citacao:** exata — `1_introduction.tex:92`, `content.tex:156` (EN) e a contraparte PT em `content.tex:76`. **Renderiza
em:** 1_introduction.tex:92 + content.tex:156 (EN) + content.tex:76 (PT)

**Minha leitura:** agree on substance; same decision as FAB-03, not a separate one. He asks for the present tense here
and at FAB-03; it is one claim in three places (1_introduction.tex:92, content.tex:156 EN, content.tex:76 PT). I first
bucketed this as 'apply' and FAB-03 as 'decide', which cannot both be right: the same sentence cannot be mine to edit in
English and his to rule on in Portuguese, and the Resumo/Abstract pair must stay claim-for-claim identical (WRITING_LAW
6). The substantive question is the one FAB-03 carries: 'is/permanece' asserts the question is open TODAY, after this
dissertation answered it, which is what the time-indexing rule exists to prevent. Caught while applying it, not while
sorting.

1. **Presente nos tres sitios: 'is an open question' / 'permanece em aberto'** — atende ao pedido literal dele nos dois
   idiomas; MAS afirma que a pergunta esta aberta hoje, depois de o documento responde-la, que e exatamente o que a
   regra de indexacao temporal existe para evitar
2. **Reformular os tres para explicitar o ponto de referencia: 'was an open question at the start of this research' / '
   era uma questao aberta no inicio desta pesquisa'** — e o que eu recomendo: da a ele o efeito que ele quer (o texto le
   como se escrito no inicio) sem afirmar que continua aberta; ~15 min, tres sitios, e o par Resumo/Abstract continua
   identico
3. **Manter o passado nos tres** — preserva a regra; contraria o pedido explicito dele, duas vezes

> **DECISAO SUA:** No item FAB-03 eu optei por continuar no imperfeito. Assim para manter a concistencia acho que temos
> que ir com a escolha 2.

#### GER-11 — the task non-conflict finding needs stronger evidence, and generalizes into future work

**Citacao:** parafrase (ele descreveu, nao citou). **Renderiza em:** 6_conclusion.tex + Appendix F

**Minha leitura:** agree on both halves. The non-conflict evidence is thinner than the claim: one mean (+0.001), four
seeds, four Gowalla states of which GA is not one of the six datasets, taken during development on an earlier data
preparation, with no spread and no Istanbul. A mean cannot distinguish 'consistently orthogonal' from 'strongly
conflicting in both directions and cancelling'. Either strengthen it or downgrade the sentence.

1. **Recomputar o cosseno na configuracao reportada, nos seis conjuntos incluindo Istambul, com dispersao por
   conjunto** — transforma anedota em resultado, e o Germano pediu exatamente isso; custo de GPU, e o item 2.9 ja tem
   tres conjuntos parados
2. **Rebaixar a frase do Cap. 6 para "uma observacao de tempo de desenvolvimento, oferecida como consistente com a
   interpretacao e nao como evidencia dela"** — zero custo de compute, honesto, e e o que eu faria primeiro; a frase
   atual sustenta "essencialmente ortogonais" com UMA media, quatro sementes, quatro estados do Gowalla dos quais GA nao
   e um dos seis, sem dispersao e sem Istambul
3. **As duas: rebaixar agora, fortalecer se a GPU liberar** — protege a defesa e mantem a porta aberta

> **DECISAO SUA:** Já corrigimos isso na versão mais atual do texto, o appendix F está bem mais maduro e com os
> resultados mais consolidados. Acho que não precisamos atuar quanto a esse ponto.

---

### ~~6.3 Onde a passagem citada nao existe mais, e o pedido precisa de nova redacao~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** voce respondeu os tres pontos no proprio bloco.

#### FAB-02 — start a new sentence on the shared-history point

**Citacao:** DESAPARECIDA — `content.tex`. **Renderiza em:** content.tex:73-74

**Minha leitura:** his edit no longer applies as written. The clause he quoted is GONE: the Resumo was cut and rebuilt
on 2026-07-28. The live sentence is 'as duas tarefas leem o mesmo histórico, portanto um único modelo poderia
aprendê-las em conjunto'. His point (start a new sentence, foreground the data argument) can still be applied to the new
sentence, but it is a rewrite of text he has not read.

1. **Aplicar o espirito no texto NOVO: quebrar a frase do Resumo em duas, comecando a segunda em "Em termos de dados, as
   duas tarefas..."** — reescrita de uma frase que ele nao leu; o Resumo e o Abstract tem que mudar juntos ou se
   contradizem
2. **Nao aplicar e registrar que a passagem citada nao existe mais** — zero custo; ele pode repetir o ponto ao ler o
   build novo

> **DECISAO SUA:** Vamos descartar esse ponto, estamos achando um equilibro bom para o resumo.

#### FAB-07 — name the study instead of the stage of the research

**Citacao:** DESAPARECIDA — `content.tex`. **Renderiza em:** content.tex:82

**Minha leitura:** agree; his own note has a '??'. He wrote 'no primeiro estudo (??)', i.e. he was unsure. The quoted
phrase is GONE; the live text reads 'naquela configuração'. Whether to name the study or the configuration is a
claim-scope choice: 'no segundo estudo' is where the diagnosis was made, not the first.

1. **"no segundo estudo"** — nomeia o estudo, que e o que ele queria; e o SEGUNDO, nao o primeiro que ele chutou com "
   (??)"
2. **Manter "naquela configuracao"** — preserva o escopo exato (a conclusao vale para aquela configuracao, nao para o
   estudo todo)
3. **As duas: "no segundo estudo, naquela configuracao"** — mais longo, e o Resumo esta no limite de tamanho

> **DECISAO SUA:** Não precisa atuar

#### FAB-10 — the results sentence opens confusingly

**Citacao:** ALTERADA — `content.tex`. **Renderiza em:** content.tex:94

**Minha leitura:** agree on substance; sentence changed. 'e a condição é o achado' is gone; the live sentence is 'A
resposta é, portanto, condicional: se o aprendizado multitarefa ajuda depende...'. His proposed opener ('Como principais
resultados, identificamos que...') is a first-person results framing, a register choice for the PT Resumo.

1. **Adotar o abre dele: "Como principais resultados, identificamos que..."** — primeira pessoa do plural no Resumo; o
   resto do Resumo e impessoal
2. **Manter "A resposta e, portanto, condicional: ..."** — mantem o registro; contraria o pedido
3. **Meio: "Os resultados mostram que o ganho do aprendizado multitarefa depende de..."** — impessoal e direto

> **DECISAO SUA:** Vamos com a 3 opção algo como: "Os resultados mostram que o benefício do aprendizado multitarefa
> depende da representação de entrada e da topologia de compartilhamento entre as tarefas."

---

### ~~6.4 Ja satisfeitos — so falta voce confirmar~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** voce confirmou ("Perfeito, mantemos assim").

#### FAB-04 — do not mention the coletanea in the Resumo

**Citacao:** DESAPARECIDA — `content.tex`. **Renderiza em:** content.tex (absent)

**Minha leitura:** his edit is already satisfied. 'coletânea' occurs NOWHERE in the live Resumo or Abstract, and nowhere
in the live tree. Either an earlier round already applied this, or he read a build that predates the rebuild. Confirm he
is content.

1. **Confirmar como satisfeito** — zero; a palavra nao existe no fonte vivo
2. **Perguntar a ele se o build que leu era antigo** — um e-mail; evita ele repetir o ponto

> **DECISAO SUA:** Perfeito, mantemos assim!

#### FAB-05 — drop the negative-result / diagnosis / resolution clause

**Citacao:** DESAPARECIDA — `chapters/1_introduction.tex`. **Renderiza em:** content.tex (absent)

**Minha leitura:** already satisfied. Same as FAB-04: the 'na ordem em que aconteceram' clause is gone.

1. **Confirmar como satisfeito** — zero; a clausula nao existe mais

> **DECISAO SUA:** Perfeito, mantemos assim!

#### FAB-08 — drop the task-pair clause from the Resumo

**Citacao:** DESAPARECIDA — `content.tex`. **Renderiza em:** content.tex (absent)

**Minha leitura:** already satisfied. The task-pair clause is GONE from the Resumo. But note FAB-17 asks to delete the
SAME content from the introduction, where it is AVAL-signed-off. Deciding 08 and 17 together avoids removing it from
both places.

1. **Confirmar como satisfeito no Resumo** — zero
2. **Decidir junto com o FAB-17** — o mesmo conteudo esta na introducao COM aval registrado; decidir separado corre o
   risco de tirar dos dois lugares

> **DECISAO SUA:** Perfeito, mantemos assim! Mas vamos adicionar um comentario sobre o resumo, que uma informação está
> sendo omitida o fato de serem tarefas diferentes entre os dois primeiros e o ultimo artigo.

---

### ~~6.5 Detalhe de dados na introducao — ele quer fora, e ha um contraste em jogo~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** voce respondeu os dois pontos no proprio bloco.

#### FAB-14 — the seven classes belong to the data, not the introduction

**Citacao:** exata — `chapters/1_introduction.tex:52-54`. **Renderiza em:** 1_introduction.tex:52-53

**Minha leitura:** disagree, and it is his call. He says the 7 classes are a property of the data, not the problem. He
is right in principle. But the count is what makes the next-category output space concrete against next region's
hundreds-to-thousands, which is the contrast 1.2 is built on, and Appendix B's static-scope note depends on the taxonomy
being introduced. Cost of removing: the reader meets 'seven' first in 2.4.

1. **Tirar as sete classes da introducao** — atende; o leitor so encontra o numero em §2.4, e o contraste 7 vs milhares
   que §1.2 constroi perde um lado
2. **Manter** — contraria o pedido de um membro da banca
3. **Manter so o contraste sem o numero: "um punhado de classes contra milhares de regioes"** — preserva o contraste,
   tira o dado

> **DECISAO SUA:** Nesse caso eu concordo com ele, é podemos só remover a frase: ", one of seven top-level classes.",
> isso já resolveria.

#### FAB-15 — census tract and mahalle belong to the data, not the introduction

**Citacao:** exata — `chapters/1_introduction.tex:54-56`. **Renderiza em:** 1_introduction.tex:54

**Minha leitura:** disagree, same reason. Same class as FAB-14: census tract / mahalle is what makes 'region' concrete.
Removing it leaves 'the official geographic unit' undefined until 2.4.

1. **Tirar census tract / mahalle da introducao** — atende; "unidade geografica oficial" fica sem definicao ate §2.4
2. **Manter** — contraria o pedido
3. **Mover para uma nota de rode** — compromisso; o Viegas usa notas assim

> **DECISAO SUA:** Vamos com a opção 1.

---

### ~~6.6 Os itens grandes do Germano — custo real, retorno real~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** voce respondeu os cinco pontos no proprio bloco.

#### GER-08 — several concepts have no formal definition, starting with a check-in

**Citacao:** parafrase (ele descreveu, nao citou). **Renderiza em:** new 2.1 subsection

**Minha leitura:** strongly agree; it is a cross-chapter edit. The chapter defines a check-in in prose only and then
writes L_c2p over check-in and place embeddings with no notation for a check-in, a user, a place, a category, or a
region. His reason is the right one: the later chapters' equations need symbols with an origin. But notation must be
checked against Chapters 3-5 AS COMMITTED and every new symbol registered in the fail-closed GLOSSARY first, so this is
not a Chapter 2 edit.

1. **Adicionar o bloco de notacao (check-in, usuario, lugar, categoria, regiao, historico, as tres tarefas) como
   subsecao no fim de §2.1** — o item de maior retorno das duas revisoes: da simbolos as equacoes dos Cap. 3-5. MAS e
   edicao TRANSVERSAL: a notacao tem que ser conferida contra os Cap. 3-5 COMO ESTAO, e cada simbolo novo tem que entrar
   no GLOSSARY (fail-closed) ANTES de aparecer. Estimo meio dia mais a sua aprovacao do registro
2. **Versao minima: definir formalmente so o check-in e as tres tarefas** — ~2h; atende o exemplo que ele deu e deixa o
   resto
3. **Nao fazer nesta rodada** — e o ponto mais forte da revisao do Germano e o precedente do proprio programa (a
   dissertacao dele) o cumpre

> **DECISAO SUA:** Opção 1

#### GER-09 — 2.3 needs MTL formalism, the balancer lineage, and a definition of loss conflict

**Citacao:** exata — `chapters/2_fundamentals.tex:383`. **Renderiza em:** 2_fundamentals.tex:383-508 -> 2.3

**Minha leitura:** strongly agree, and it is the largest item here. 2.3 defines MTL in one prose clause and never writes
the total loss; names eight balancers in eight sentences of identical shape with no taxonomy; credits almost no lineage;
and never defines what conflict IS, which is what PCGrad, CAGrad and Aligned-MTL all act on. That last gap is why
Chapter 6's +0.001 cosine lands with no definition behind it.

1. **Fazer os quatro: a equacao da perda total, agrupar os balanceadores por mecanismo (peso vs cirurgia de gradiente),
   creditar a linhagem, e definir conflito pelo cosseno** — o maior item de conteudo; ~1 dia. Define a quantidade que o
   +0,001 do Cap. 6 mede, que hoje nao tem definicao em lugar nenhum
2. **So a equacao da perda e a definicao de conflito** — ~3h; e o minimo que torna o numero do Cap. 6 legivel
3. **Nao fazer** — a pergunta de pesquisa da dissertacao e se MTL ajuda, e o capitulo nunca escreve o objetivo de MTL

> **DECISAO SUA:** Opção 1. Voce pode se aproveitar da explicação de cosseno do appendix F, apesar de estarmos fazendo
> essa nova parte não precisa remover nada do appendix F, caso fique repetitivo.

#### GER-10 — the fundamentals need a logical narrative built on formal definition blocks

**Citacao:** parafrase (ele descreveu, nao citou). **Renderiza em:** whole chapter

**Minha leitura:** agree, as a drafting principle. This is the synthesis of his other points, and the comparative
evidence agrees: our Ch.2 has 5 sections and ZERO subsections; the approved same-advisor precedent (Viegas) has 5
sections and 19 subsections at similar length. Adding two heading levels is what gives GER-08 and GER-09 somewhere to
go.

1. **Adicionar dois niveis de titulo em todo o capitulo** — a prosa quase nao muda e o capitulo fica navegavel; e onde o
   GER-08 e o GER-09 vao morar. Precedente: Viegas tem 5 secoes e 19 subsecoes com o mesmo tamanho; o nosso tem 5 e ZERO
2. **Subsecoes so em §2.2 e §2.3** — meia medida, cobre onde estao as duas lacunas
3. **Nao fazer** — o capitulo e uma referencia que o leitor consulta vindo do Cap. 5; sem titulos ele nao acha nada

> **DECISAO SUA:** Opção 1.

#### GER-03 — the HGI tuning sweep is thrown into the text with no connection to it

**Citacao:** exata — `chapters/2_fundamentals.tex:167-170`. **Renderiza em:** 2_fundamentals.tex:167-174 -> 2.2

**Minha leitura:** agree it does not belong; the gate constrains HOW. Strongly agree the four-point sweep is a methods
result in a fundamentals chapter, reported to four decimals under an averaging convention the chapter has not yet fixed.
BUT the sentence is probe NUM-4 in check_audit_claims.py, which requires 0.8186 to be PRESENT with its spreads and
averaging convention. Relocating is compatible with the probe if the probe moves with it; deleting the numbers is not.

1. **Mover o sweep para o Cap. 5 (metodo ou apendice) e mover o probe NUM-4 com ele, no MESMO commit** — atende ao
   ponto; o probe exige que 0.8186 esteja PRESENTE com dispersoes e convencao, e mudar de arquivo sem repontar o probe
   deixa o gate vermelho
2. **Manter uma frase conceitual sem numeros em §2.2 e o sweep no Cap. 5** — o que eu recomendo; resolve tambem
   o [VERIFY] da convencao de media, que hoje reporta quatro decimais sob uma convencao que o capitulo ainda nao fixou
3. **Manter onde esta e so resolver o [VERIFY]** — mais barato; o defeito de fluxo que ele apontou continua

> **DECISAO SUA:** Aqui temos alguns problemas, vamos aos fatos. A parte que está com problema hoje é a: "The baseline
> was also tuned rather than taken as published: the cross-region edge weight of their Equation 2, set to 0.4 for the
> dense Chinese cities they study, was raised to 0.7 for the sparser United States state datasets used here. The sweep
> that fixed that value ran on Alabama over four settings of the weight, 0.4, 0.5, 0.6, and 0.7, each measured over five
> folds with a budget of 50 epochs, and the category F1 rose monotonically across them, from $0.7388 \pm 0.0205$ at the
> published setting to $0.8186 \pm 0.0123$ at the adopted one, on a zero-to-one scale, with the spread taken across the
> five folds."
> O ponto e que ela parece sem nexo, para quem está lendo rapido ou desatendo, não entende que estamos discutindo sobre
> o fato que os hyperparmsteeros usado pelo hgi em nosso artigo foi retirado do artigo base que se baseava em uma cidade
> chinesa. Esse é o primeiro ponto essa frase está confusa sem nexo, sengundo ponto ela está "overwhelming", ou seja,
> ela está com execesso de informação, podemos simplificar bem isso e caso o leitor uqe se interesee acesso o artigo
> deles para saber mais. Por fim um outro ponto, é quanto ao fato disso não pertencer a fundamentação téorica, é sim a
> métodologia. Eu proponho melhorar esse texto e deixar isso em um appendice.

#### GER-04 — the static-vector paragraph reads like introduction prose, and it matters

**Citacao:** exata — `chapters/2_fundamentals.tex:192-193`. **Renderiza em:** 2_fundamentals.tex:192-199

**Minha leitura:** agree it reads as introduction; he also says keep it. He called it well written and important, and
only observed it reads like introduction prose. There is no defect to fix here, only a placement question, and it is 108
chars from the NUM-4 probe string.

1. **Nao mexer** — ele mesmo disse que esta bem escrito e que e importante; nao ha defeito a corrigir
2. **Mover para o inicio de §2.2 como paragrafo de abertura** — atende a impressao de "texto de introducao"; mexe num
   paragrafo a 108 caracteres do probe NUM-4

> **DECISAO SUA:** Eu acredito que tenhamos que deixar ele onde está, na introdução já comentamos sobre o ponto de a
> literatura usar em sua maioria poi embedding ao inves de checking embedding, caso não comentamos isso bem lá, porfavor
> melhore o texto da introdução. Mas, quanto aqui eu acredito que temos que sim, manter esse paragrafo onde ele está ele
> server de cola e ponte falarmos sobre outros tipos de embedding, estes que serão usados no checking embedding. E aqui
> abrimos outra ponta no paragrafo: "Beforethatstep,severalgeneralencoderssupplythecontextastaticplacevectoromits.",
> precisamos melhorar sua conexão com o paragrafo anterior falando sobre esse ponto que o checkin embdding precisa de
> embedding temporais e locacionais e onde entra o conteduo do resto do paragrafo; valide essa minha ideaia.

---

### ~~6.7 Bloqueado numa verificacao que falhou~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** voce respondeu no proprio bloco.

#### FAB-28 — there is more MTL-for-POI work than the two papers cited

**Citacao:** exata — `chapters/2_fundamentals.tex:454`. **Renderiza em:** 2_fundamentals.tex:454 -> 2.3

**Minha leitura:** agree on substance; verification FAILED on the decisive paper. He is right that the coverage is thin,
and the real exposure is that 2.3 claims NO multi-task model predicts next region as a co-equal end target while
wang2025hamtl (hierarchy-aware MTL for user LOCATION prediction, J. Supercomputing 81 (11):1196, 2025) sits uncited in
the same bibliography. Whether the claim survives turns on whether that paper treats a region-like unit as an END
TARGET, and I could NOT establish it: OpenAlex has no abstract, Crossref has no abstract, the configured Springer key
returns 401 on meta/v2, metadata and meta/v1, the paper is closed access (Unpaywall oa_status=closed), and the landing
page 303-redirects to an authentication gate. Semantic Scholar offers only a MACHINE-GENERATED tldr, which
AGENT_GUARDRAILS R5 forbids as a source. Four of the five other candidates ARE verified and citable (see the ledger);
this one is not, and it is the one the novelty sentence depends on.

1. **Voce (ou a biblioteca da UFV) abre o `wang2025hamtl` e me passa o resumo** — desbloqueia; e o unico caminho
   admissivel sob o §1
2. **Citar os quatro verificados (`Zhang2020`, `Halder2022`, `Xu2023` como MTL, `Halder2021` por atributo) e NAO citar o
   `wang2025hamtl`** — amplia a cobertura sem apoiar alegacao em titulo; a frase de novidade continua exposta a quem
   achar o artigo
3. **Enfraquecer a frase de novidade para "entre os trabalhos revisados aqui"** — honesto e barato; abre mao de uma
   alegacao que pode muito bem sobreviver

> **DECISAO SUA:** Vamos então avaliar o wang2025hamtl, adicione no caminho:
> articles/dissertacao/science/articles/wang2025hamtl.pdf. Apos ler ele avalie quais adicionar na dissertação se todos
> forme interessante, adicionamos todos.

---

### ~~6.8 A sua propria pergunta~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** voce respondeu ("Vamos com a opcao 1").

#### AUT-01 — does the MTL fundamentals need Pareto optimality

**Citacao:** -. **Renderiza em:** 2_fundamentals.tex 2.3

**Minha leitura:** agree it needs a brief treatment. The author's own added question: does the MTL fundamentals need
Pareto optimality. Since 2.3 names gradient-surgery balancers, and MGDA/CAGrad/Nash-MTL are all argued in terms of
Pareto-stationary points, the concept is already implicit. Note 'Pareto-stationary point' is ALREADY in the prose and is
PENDENCIAS_RESOLVIDOS 2.12 (arquivado 2026-08-02) (unregistered in the fail-closed GLOSSARY), so this item and 2.12 are the same decision.

1. **Um paragrafo breve em §2.3: o problema multitarefa e multi-objetivo, os balanceadores de cirurgia de gradiente sao
   argumentados em termos de estacionariedade de Pareto, e por isso o MGDA/CAGrad/Nash-MTL existem** — atende sua
   intuicao e da espinha ao paragrafo dos balanceadores; ~1h. Note que `Pareto-stationary point` JA esta na prosa e e o
   item 2.12 (nao registrado no GLOSSARY), entao este item e o 2.12 sao a MESMA decisao
2. **So registrar `Pareto` no GLOSSARY e nao expandir** — fecha o 2.12 sem crescer o capitulo
3. **Nao tratar** — o capitulo nomeia balanceadores cuja justificativa e Pareto e nunca diz isso

> **DECISAO SUA:** Vamos com a opção 1. Aqui vale notar que em uma ultima interação, realizamos o item 2.12, então
> avalie como está e se julgar necesssario voce adiciona mais contexto embasado com referencias.

---

### ~~6.9 Edicao concorrente durante esta rodada — RESOLVIDA pela propria esteira, e registrada~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** resolvido pela propria esteira; nada dependia de voce.

**O que aconteceu.** Enquanto eu media, **outra esteira** alterou arquivos que eu nao toquei:
`GLOSSARY.md` (02:11 e 02:30, os quatro registros de Pareto, que fecham a **2.12** pela opcao (a)),
`src/chapters/2_fundamentals.tex` (02:23, +106 linhas em §2.3: a equacao da perda total mais o tratamento de Pareto),
`check_audit_claims.py` (02:38, cinco probes dela sobre a minha mudanca de segunda raiz) e `_history/_round6/VERIFY_LIST.md` (03:
01).

**Duas falhas de gate que eu vi eram dela, e as duas ja estao fechadas — por ela, nao por mim.**
Registrado porque eu quase abri uma decisao sua sobre a primeira:

| o que falhou                                                | causa                                                                                                                                                                   | estado agora                                                          |
|-------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| `check_verify_list`: `EXPECT: contains=Pareto-stationary 0` | o registro do termo tornou a anotacao falsa                                                                                                                             | corrigida para `2` no mesmo commit do registro, que e o caminho da V6 |
| `check_verify_list`: `CD-FAIL` num bloco de build           | um bloco cercado em `VERIFY_LIST.md:326` sem sufixo `cd src` para o extrator remover, entao o gate **rodava um build de verdade** (108 s medidos) e nunca via `REACHED` | o bloco foi tirado da cerca em 03:01; `make check` volta a 2,4 s      |

**Consequencia metodologica, e essa vale mais que os dois defeitos.** Eu li os dois como vermelhos meus, e um deles eu
ja tinha escrito aqui como uma decisao sua com tres opcoes. Numa arvore com duas esteiras, **um gate vermelho nao e
evidencia de nada ate voce reconferir de quem e o arquivo e qual e o mtime dele** — o meu primeiro diagnostico foi de um
arquivo lido no meio da escrita de outra pessoa.

**Um item meu mudou de balde por causa disso, e nao foi por edicao concorrente:** o **FAB-18** virou decisao sua (§6.2),
porque ele pede o presente na mesma frase que o FAB-03, e eu tinha posto um em cada balde. Achei ao aplicar, nao ao
classificar.

**Tres coordenadas minhas andaram +106 linhas** por causa da edicao em §2.3, e foram reconferidas linha a linha, nao
deslocadas por aritmetica: FAB-28 (454 -> 560), FAB-29 (513 -> 619), FAB-30 (515-516 ->
621-622 e 670 -> 776).

**E um defeito que eu encontrei e corrigi, este nao concorrente:** o §4 item 5 deste arquivo mandava voce rodar
`make final` (alvo renomeado para `academico` em 2026-07-29) e prometia **108/105/109**
paginas. A arvore da **102/99/103**. O `sync_page_counts.py` varria so `CLAUDE.md`, `PLAN.md` e
`codex_reviewer.md`, e por isso o numero envelheceu sem gate — **este arquivo entrou na varredura em 2026-07-30**,
depois de a minha propria correcao aqui ficar obsoleta por uma pagina em menos de uma hora (a outra esteira somou uma
pagina ao §2.3 entre uma medicao e a seguinte).

> **DECISAO SUA:** nada aqui. Fica como registro.

---

### ~~6.10 Tres bloqueadores das personas de revisao — todos conferidos por mim no fonte~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** voce respondeu os tres bloqueadores no proprio bloco.

As quatro personas de fato (04 concordancia, 05 citacoes, 06 numeros, 07 alegacoes/honestidade)
rodaram contra o build `03b53d16`. Relatorios em `_history/_round9/reviews/`, resumo em
`_history/_round9/37_reviewer_gate_round9.md`. **Tres bloqueadores.** Reconferi os tres abrindo o fonte, porque auto-relato de
persona nao e evidencia (L6). Os tres sao decisao sua: dois sao alegacoes de conteudo e o terceiro tem duas saidas de
custo diferente.

#### BLQ-1 — o Apendice F diz que o compartilhamento duro "nao custa nada", e chama de duro a topologia errada

**Onde:** `chapters/apx_f_cosine.tex`:290, renderiza na p. 101 do build de defesa. **Texto:** "That is why hard sharing
costs nothing in this architecture, and why Chapter~\ref{ch:mobiwac} finds no balancer improving on a fixed loss
weighting".

**Dois defeitos numa clausula, os dois confirmados no fonte:**

1. A afirmacao de custo e **irrestrita**, e o proprio documento a desmente:
   `5_mobiwac/06_results.tex`:145-146 registra o ganho de regiao indo "from $-0.41$ at the smallest count to $+2.20$ at
   the largest". Existe celula negativa, e o Cap. 5 a chama de deficit pequeno mas estatisticamente significativo.
2. A arquitetura do Cap. 5 **nao e compartilhamento duro** pela definicao do proprio Cap. 2:
   `5_mobiwac/01_introduction.tex` a descreve como "a shared trunk (a cross-attention stack where the two tasks exchange
   semantic context) and a private spatial path for the region task".

1. **Trocar pela afirmacao licenciada, que o Cap. 5 ja usa: "sharing stopped hurting" (p. 80), nomeando a topologia como
   tronco de atencao cruzada** — corrige os dois defeitos numa frase, nao perde o argumento (o ponto do apendice e a
   ortogonalidade, nao o custo), ~10 min
2. **So restringir o custo ("costs nothing on the category task", ou "at four of the six datasets")**
   — mantem a palavra "custo", mas continua chamando a topologia de compartilhamento duro
3. **Deixar como esta** — a frase e uma generalizacao irrestrita contra uma celula negativa medida no mesmo documento; e
   o tipo de frase que uma banca localiza

> **DECISAO SUA:** Já fizemos algumas correções no appendix F, mas se esse ainda continuar com esses erros logicos,
> podemos seguir com a opção 1.

#### BLQ-2 — a resposta consolidada usa "everywhere" nu e colapsa a particao da regiao

**Onde:** `chapters/6_conclusion.tex`:106, renderiza na p. 79. E a frase mais citavel da dissertacao. **Texto:**
"outperforms the dedicated models on the category task everywhere and outperforms or matches them on the region task."

**Confirmado contra a lei, que aqui e explicita.** `WRITING_LAW.md`:83 diz, literalmente, que a afirmacao de escala fica
escopada aos cinco estados e **bare "everywhere" never**; a linha 75 proibe
"outperforms region everywhere" por nome. E "outperforms or matches" joga fora a particao quatro-de-seis / TOST que a
redacao protegida exige — particao que **este mesmo capitulo enuncia corretamente na pagina anterior**.

1. **Reescrever com a particao explicita: supera nas seis para categoria; para regiao, supera em quatro dos seis e nao e
   inferior (TOST, +/-2 pp) nos outros dois** — e a redacao protegida, ja usada duas vezes no mesmo capitulo, ~15 min
2. **Manter "everywhere" so para categoria (onde e verdade nas seis) e abrir a particao so na regiao**
   — mais curto, mas "everywhere" nu esta proibido pela linha 83 sem excecao por tarefa
3. **Deixar como esta** — contradiz a lei que voce mesmo escreveu, na frase que mais vai ser lida

> **DECISAO SUA:**  Eu acho que isso já foi mudado no texto, mas se caso se manter mantenha everywhere para o categoria
> e especifique onde for preciso para o next-region.

#### BLQ-3 — dois fatores de escala calculados na prosa, sem ledger e sem script

**Onde:** `chapters/apx_f_cosine.tex`:317-319, p. 101. **Texto:** "this axis spans a factor of thirty-six in volume and
one of sixteen in the size of the region label set".

**Os numeros estao CERTOS** — 4.089.892 / 113.846 = 35,92 e 8.501 / 520 = 16,35, e os quatro extremos sao rastreaveis em
`datasets.tex`. O achado nao e erro de conta: e que os dois fatores sao **derivados na prosa**, e N2/N3 mandam citar,
nunca calcular. Nada os regenera quando um dataset muda.

1. **Enunciar os quatro extremos (que ja sao rastreaveis) e cortar as razoes** — o leitor faz a divisao se quiser; some
   a alegacao nao rastreavel, ~5 min
2. **Manter as razoes e registra-las no ledger do apendice com o comando que as produz** — preserva a frase como esta,
   custa uma linha de ledger e um probe
3. **Deixar como esta** — dois numeros no volume construido sem origem registrada

> **DECISAO SUA:** Pode remover, e pare ser sincero e uma leitura rapida eu nem entendi o que esses numeros siginificam,
> então fará até melhor para leitura.

---

### ~~6.11 Segunda onda de personas — um bloqueador confirmado, um rebaixado por mim~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** voce respondeu ("Vamos de 1", "Vamos de A").

Cinco personas que voce pediu (15 legibilidade, 16 credibilidade-IA, 17 excelencia, 11 POI/mobilidade, 10 MTL) contra o
build `901a0408`. Relatorios em `_history/_round9/reviews/`, resumo em
`_history/_round9/38_reviewer_wave2_round9.md`. Reconferi no fonte tudo que entrou aqui.

#### BLQ-4 — o Apendice F descreve um experimento que nunca foi feito

**Onde:** `chapters/apx_f_cosine.tex`:83, renderiza na p. 97 do build de defesa. **Texto:** "That is why replacing the
sharing scheme changed so little in the first study, and why changing the representation changed so much in the second
and third."

**Confirmado, e o proprio documento diz o contrario em tres lugares.** O Cap. 3 construiu **uma**
arquitetura (`3_cbic/method.tex`:69, "built upon a hard parameter-sharing scheme") e lista as alternativas como trabalho
futuro (`3_cbic/conclusion.tex`:23, "We plan to explore alternative parameter-sharing mechanisms, such as **soft
sharing (e.g., Cross-Stitch Networks) or Mixture-of-Experts (MoE) models**"). Os resultados dele comparam MTL contra os
modelos de tarefa unica, contra MHA+PE e contra o HMRM — nunca dois esquemas de compartilhamento. E o
`1_introduction.tex`:133-135 atribui a troca da topologia de compartilhamento ao **terceiro** estudo.

**O mesmo apendice acerta duas paginas depois**, em :294-299: o nulo do primeiro estudo *foi lido*
como evidencia sobre compartilhamento na epoca, e o limite estava em outro lugar. Ou seja, a frase certa ja existe no
mesmo arquivo.

1. **Reescrever a frase de :83 na forma que :294-299 ja usa — o nulo do primeiro estudo foi interpretado como limite do
   compartilhamento, e a medicao mostra que nao era** — corrige a afirmacao sem perder o argumento do apendice, ~10 min
2. **Cortar a clausula "replacing the sharing scheme" e ficar so com a metade da representacao** — mais curto; perde a
   ponte para o arco dos tres estudos
3. **Deixar como esta** — um leitor da p. 97 e informado de um experimento que nao aconteceu; e do tipo que a banca
   pergunta

> **DECISAO SUA:** Vamos de A.

#### BLQ-5 — a persona de MTL abriu um bloqueador no PCGrad, e eu o REBAIXEI; a decisao final e sua

**Onde:** `chapters/2_fundamentals.tex`:442-445. **Texto:** "PCGrad guarantees that one projected update leaves the
multi-task loss no higher than the unmodified gradient would ... and it makes no Pareto claim at all
\cite{yu2020pcgrad}."

**O que ela alegou:** que a p. 5 do CAGrad atribui convergencia a um ponto de Pareto arbitrario a *propria analise* do
PCGrad, o que contradiria o "no Pareto claim at all".

**Por que eu rebaixei.** Abri os dois registros nesta sessao. O arXiv:2001.06782 (PCGrad, NeurIPS

2020) nao tem 'Pareto' nem frase de convergencia no resumo, e a extracao do proprio repo achou **zero**
      'Pareto' em 27 paginas com o instrumento validado no mesmo texto. O resumo do arXiv:2110.14048 (CAGrad)
      diz que os metodos anteriores "lack convergence guarantee and/or could converge to any Pareto-stationary point".
      **A clausula do capitulo esta citada a `yu2020pcgrad` e fala do que aquele artigo afirma**; a frase do CAGrad e um
      terceiro caracterizando a familia. As duas coisas convivem.

**O que sobra, e por isso o item existe:** se a p. 5 do CAGrad de fato atribui o resultado a analise do PCGrad, um
leitor que conhece o CAGrad vai achar "no Pareto claim at all" mais categorico do que a literatura em volta sustenta.
**Eu nao consegui ler a p. 5** — so o resumo era alcancavel sem o PDF — e por isso rebaixei em vez de descartar, e digo
qual metade nao conferi.

1. **Suavizar para "and makes no Pareto claim of its own"** — mantem a verdade sobre a fonte citada e remove o absoluto
   que incomoda quem conhece o CAGrad, ~5 min
2. **Abrir a p. 5 do CAGrad e decidir com ela na mao** — o certo se voce tem acesso; e um paragrafo
3. **Deixar como esta** — a frase e exata sobre a fonte que cita, e a persona nao a refutou

> **DECISAO SUA:** Vamos de 1.

#### Sem decisao sua, so registro: o que as duas personas de dominio confirmaram

A de POI/mobilidade nao achou bloqueador: a distincao proxima categoria / proxima regiao / proximo lugar se sustenta em
tudo que ela leu, o argumento nivel-de-check-in contra nivel-de-lugar esta correto como afirmacao de modelagem de
mobilidade e ancorado no CTLE e nao no seu proprio resultado, e as divulgacoes de protocolo do Cap. 5 sao **mais fortes
que a norma dessa literatura**. Os quatro should-fix dela sao todos a mesma classe: **lugar, nao verdade** — defesas que
o Cap. 5 carrega e o Cap. 2 nao (construcao de janela, transdutividade, justificativa da unidade regional, a intuicao de
revisita). A de MTL verificou **seis das sete clausulas de garantia** do bloco de Pareto de hoje contra cinco PDFs de
origem, e retirou duas conclusoes proprias depois de abrir as paginas que as refutavam. A de excelencia deu **VERY GOOD
forte** com caminho barato para outstanding, e registrou que o resultado nulo publicado e **inequivocamente um ativo**
como esta apresentado.

---

### ~~6.12 Rodada 10 — as suas 28 decisoes, auditadas contra o texto VIVO antes de qualquer acao~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** as 28 decisoes foram auditadas e aplicadas; os itens 1 e 2 do "que espera VOCE" foram MEDIDOS como ja resolvidos nesta rodada (as duas linhas de registro existem no GLOSSARY, e a rodada 11 separou a definicao dupla), e os itens 3 e 4 sao divulgacoes honestas e nao pedidos.

Baseline `dda8978e`; entregue em `984c70be`, `aaf4e7eb`, `5415d86d`, `d7e8c598`. Auditoria completa em
`_history/_round10/30_r10_audit.md`; relatorios dos itens grandes em `_history/_round10/28_hamtl.md` e
`_history/_round10/29_ch2_definitions.md`.

**Voce avisou que o texto tinha mudado, e o aviso foi a coisa mais util desta rodada.** Entre os itens
serem escritos e as suas decisoes chegarem, **60 commits** entraram na arvore. **Nove das 28 decisoes
pedem texto que nao existe mais** e foram fechadas como ja-feitas, nao aplicadas: FAB-10, FAB-14,
FAB-17, GER-03, GER-11, BLQ-1, BLQ-2 (no Cap. 6), BLQ-4, BLQ-5. O GER-03 e o caso mais claro: a sua
decisao apontava tres defeitos (sem nexo, "overwhelming", pertence a metodologia) e os tres estao
resolvidos por sua propria mao, com a varredura agora em `apx_g_hgi_tuning.tex` fechando num aviso de
escopo de que ela **nao** e evidencia sobre HGI contra Check2HGI.

**Quatro edicoes aplicadas, cada uma conferida no PDF renderizado nos dois sentidos:**

| item | o que faltava de verdade |
|---|---|
| BLQ-2 | UM site sobrevivia, em `1_introduction.tex`:289-292, e um grep por linha nao o via porque a frase quebra em tres linhas. Agora espelha o Cap. 6: categoria nos seis, regiao em quatro dos seis, TOST nos outros dois |
| BLQ-3 | os dois fatores derivados sairam do Apendice F; as quatro contagens de ponta ficam, cada uma rastreavel a tabela do §D.1 |
| FAB-08 | comentario registrando o que o Resumo omite: que **o par de tarefas muda** entre os estudos, que o corte foi deliberado na rodada 6, e onde o leitor recebe a informacao |
| FAB-22 | faltava a clausula que carrega o seu argumento: **Istanbul esta ali porque nao e dataset dos Estados Unidos**. Sem isso, Istanbul le como um sexto dataset e nao como evidencia de generalizacao |

**FAB-28 esta resolvido, e era o bloqueador da rodada 9.** Voce colocou o PDF em disco e ele foi lido
inteiro. A frase de ausencia do Cap. 2 **sobrevive sem mudanca**, por tres motivos independentes na
fonte: o HAMTL chama a predicao de localizacao de tarefa **principal** e a de categoria de **auxiliar**
(p. 2), logo as duas cabecas nao sao co-iguais; ele nao nomeia nenhuma unidade tipo regiao em 28 paginas
(uma varredura completa por region/grid/district/zone/administrative devolve **um** acerto, dentro do
titulo da referencia [40], Tobler 1970, p. 27); e ele nao reporta nenhuma metrica do lado da categoria.
**O que estava errado era a NOSSA descricao dele**, que nomeava o componente errado e escondia a
assimetria principal/auxiliar. Corrigida para as palavras dos proprios autores. Uma referencia entrou
(`wang2024iemtlf`, o trabalho anterior do mesmo grupo) com `[VERIFY]` no bib, porque so o titulo foi
verificavel.

**Uma constatacao honesta que o item nao previa:** o HAMTL **nao** abre para uma literatura grande de
MTL-para-POI nao citada. A propria secao de MTL dele quase nao cita mobilidade, e as dez referencias de
MTL em cascata sao imagem medica, PLN e recomendacao multi-comportamento. Nao foram abertas nem
propostas, e estao nomeadas como nao-alcancadas. Se voce quiser amplitude de MTL geral em vez de
MTL-para-POI, esse e o conjunto, e vale um item proprio.

**GER-04: voce pediu para eu validar a sua ideia, e ela esta certa e ja implementada** por voce. A frase
que voce citou nao existe mais. O §2.2 agora le: limitacao (um vetor fixo por lugar, logo uma manha de
quarta e um sabado a noite tem entradas identicas) -> "A per-visit representation needs temporal and
spatial context in addition to the identity of the visited POI" -> o inventario de encoders -> o nivel
de check-in que os consome. E exatamente a sua proposta. A metade da introducao tambem nao precisa de
nada: `1_introduction.tex`:125-131 ja carrega o argumento.

**GER-08 / GER-09 / GER-10 / AUT-01 sairam como um unico trabalho**, porque os quatro reestruturam o
mesmo arquivo. Onze definicoes numeradas e referenciaveis (2.1 check-in ate 2.11 conflito de gradiente,
esta com a formula do cosseno), com nove referencias cruzadas alem dos onze blocos, que e o que faz da
coisa a narrativa que o GER-10 pede em vez de um deposito de definicoes. **Zero crescimento de pagina**,
e o modo importa: as definicoes custaram uma pagina, o `make check` ficou vermelho com quatro contagens
obsoletas, e em vez de rodar `sync_page_counts --write` para o gate concordar com um documento mais
longo, o texto foi compactado ate a contagem voltar a 106 e o gate ficar verde sozinho. Nenhuma probe
foi enfraquecida. O AUT-01 foi avaliado como **ja suficiente** e nada foi acrescentado, o que a sua
decisao autorizava ("se julgar necessario").

#### O que espera VOCE, e nao e trabalho que eu poderia ter feito

1. **Duas linhas de registro no GLOSSARY**, propostas e nao usadas como termo novo: `soft parameter
   sharing` (compartilhamento flexivel de parametros) e `negative transfer` (transferencia negativa).
   As duas expressoes **ja estavam na prosa viva** antes desta sessao e o §6 registra so `hard parameter
   sharing`, entao converter prosa em blocos de definicao nao ampliou a regra fail-closed. Mas as linhas
   deviam existir, e linhas de registro sao suas.
2. **A Definicao 2.7 junta dois conceitos** (representacao em nivel de lugar e em nivel de check-in) sob
   um mesmo cabecalho, para segurar as 106 paginas. Separar custa um numero de definicao e cerca de
   quatro linhas, que teriam de ser recuperadas em outro ponto do §2.2.
3. **Nove atribuicoes de linhagem, das quais eu reconferi cinco** nos registros de origem (Shikun Liu /
   DWA, Bo Liu / CAGrad, Bo Liu / FAMO, Zhao Chen / GradNorm, Aviv Navon / Nash-MTL, todas confirmadas).
   As outras quatro repousam na verificacao do agente, sem passe de critico. Digo em vez de omitir.
4. **FAB-27, a margem: medida e nao reproduz.** Zero `Overfull \hbox` nos quatro builds; extracao de
   tinta pagina por pagina nas 106 paginas contra o bloco de texto real (455,24pt, perguntado ao TeX)
   poe **toda** pagina 0,5 mm **dentro** do bloco, a mais apertada em 1,99 cm contra a regra de 2 cm. A
   sua observacao era verdadeira e ja foi corrigida (o commit `6d780b58` se chama "fix the p.96
   overflow"). Nao ha o que mexer, e se voce ainda ve a tabela passando, me diga em qual pagina do PDF.

---

### ~~6.13 Rodada 12 — dois defeitos que VOCE achou nas definicoes, e duas linhas de registro que eu nao posso escrever~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** AD-5 fechada por voce e as duas linhas aplicadas por mim sob a sua autorizacao de 2026-08-03.

**Voce encontrou o que o item 7 (passe critico nas definicoes) existia para encontrar**, antes do passe
rodar. Os dois sao lacunas de formalizacao, nao afirmacoes erradas, e os dois ficam exatamente nos pontos
onde o capitulo carrega o argumento.

**Defeito 1 — a Definicao 2.8 nao tinha simbolo.** A 2.7 da o vetor de nivel de lugar como
$\mathbf{e}_p$ e a 2.8 dizia apenas "um vetor para cada check-in". O contraste lugar-versus-check-in e o
pivo da dissertacao inteira, e so um dos lados podia ser escrito. Corrigido para $\mathbf{e}_{x_i}$.
Medido antes de cunhar: `\mathbf{e}_{x_i}`, `\mathbf{e}_{x}`, `\mathbf{e}_i`, `\mathbf{z}_i` e
`\mathbf{z}_{x_i}` aparecem ZERO vezes na arvore viva, entao nada foi sobrecarregado; os unicos
subscritos de $\mathbf{e}$ em uso eram $p$ e os genericos $1$/$2$/$+$/$-$ das equacoes do
discriminador. O simbolo espelha o $\mathbf{e}_p$ e muda so o que o subscrito indexa, que E a distincao
sendo definida. Probe `R12-eqxi`.

**Defeito 2 — a Definicao 2.6 era a unica tarefa em prosa pura.** A 2.3, a 2.4 e a 2.5 dao uma funcao
($g_{\mathrm{cat}}(\mathbf{e}_p) \to c_p$, $f_{\mathrm{cat}}(H_i) \to c_i$,
$f_{\mathrm{reg}}(H_i) \to r_i$) e o next place nao dava. Isso fazia a tarefa excluida parecer um tipo
DIFERENTE de objeto justamente onde a funcao do capitulo e manter as tres formalmente distintas.
Corrigido para $f_{\mathrm{place}}(H_i) \to p_i$, e nomear a funcao AFIA a declaracao de escopo em vez
de enfraquece-la: a exclusao passa a incidir sobre um objeto definido. A frase agora diz que nenhum
capitulo reporta resultado para $f_{\mathrm{place}}$. Probes `R12-fplace` e `R12-fplace2`.

> **DECISAO SUA — duas linhas do GLOSSARY §1.1, que e sua e nao minha.** Eu usei os dois simbolos na
> prosa do Capitulo 2 porque eles instanciam objetos ja registrados ($x_i$, $H_i$, $p_i$, $\mathcal{P}$),
> mas a TABELA DE NOTACAO e um registro, e linha de registro e sua. As duas propostas:
>
> | Simbolo | Definicao proposta | Nota |
> |---|---|---|
> | $\mathbf{e}_{x_i}$ | A representacao aprendida do check-in $x_i$. | Entrada de nivel de check-in; e o "per-visit Check2HGI vector" que a linha do $\mathbf{e}_p$ ja menciona sem nomear. |
> | $f_{\mathrm{place}}(H_i)$ | Preditor sequencial cujo alvo e o proximo POI $p_i$. | Nomeado apenas para delimitar escopo; nenhum capitulo reporta resultado para ele. |
>
> 1. **Registrar as duas** — fecha a lacuna que a propria linha do $\mathbf{e}_p$ aponta ("distinct from
>    a per-visit Check2HGI vector", sem simbolo).
> 2. **Registrar so o $\mathbf{e}_{x_i}$** — o $f_{\mathrm{place}}$ existe para ser excluido, e voce pode
>    preferir nao registrar notacao de uma tarefa que a dissertacao nao executa.
> 3. **Nenhuma das duas, e eu retiro os simbolos da prosa** — volta ao estado anterior, com os dois
>    defeitos que voce achou de volta junto.
>
> **RESPONDIDA — AUTORIZADAS, e agora APLICADAS.** Ele fechou a **AD-5** em 2026-08-03 (§6.16) autorizando as
> duas linhas, e em 2026-08-03 mandou que **eu** as colasse em vez de colar ele mesmo (§6.26, opcao 3). As duas
> estao na tabela §1.1 do `GLOSSARY.md` desde este commit, e o comentario do `2_fundamentals.tex` que afirmava
> o contrario foi corrigido no mesmo commit. Residuo de formatacao; **nao gaste decisao aqui.**

---

### ~~6.14 Rodada 12 — as suas quatro descobertas nas definicoes, resolvidas em projeto, e duas decisoes que sobraram~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** as quatro descobertas foram respondidas no §6.15 e no §6.22.

**Voce achou um defeito estrutural, e ele mede como real.** O grafo de dependencias das doze definicoes
tem **exatamente uma** violacao da ordem de leitura: a **2.3** consome $\mathbf{e}_p$, que a **2.7**
introduz 318 linhas depois. Todas as outras consumacoes sao para tras e legais. Medido, nao estimado
(`_history/_round12/46`).

**A sua pergunta sobre a literatura tem resposta, e voce estava certo.** Quatro fontes abertas nesta
sessao, cada uma citada do proprio texto (`_history/_round12/48`): CSLSL (Def 1 registro = tupla, Def 2 trajetoria =
sequencia de REGISTROS), CTLE ("a trajectory consisting of sequential visiting records", com o embedding
como uma FUNCAO $z(l)$), HAMTL (Def 1 ponto, Def 2 trajetoria de pontos) e **o seu proprio MobiWac**
(`03_problem.tex`: "Given a user's time-ordered check-in history"). **Quatro de quatro definem a sequencia
sobre observacoes cruas e introduzem a representacao depois, como um mapa.** O caso decisivo e o CTLE:
um artigo cuja contribuicao E o embedding e que ainda assim separa as duas camadas.

**O QUE ISSO MUDOU NO PROJETO.** A correcao da sua descoberta 2 NAO e redefinir $H_i$ sobre embeddings. O
$H_i$ continua sequencia de check-ins e entra um **mapa de representacao nomeado** $\rho(x_i)\in\mathbb{R}^d$,
estendido a historias, antes das tarefas. O argumento que sustenta isso nao e "a area faz assim": e que a
sua tese central e que a REPRESENTACAO domina, e isso so e enunciavel se a tarefa for o MESMO OBJETO nos
tres estudos enquanto a representacao varia. Definir a historia sobre embeddings faria a definicao da
tarefa mudar de capitulo para capitulo e destruiria o ponto de referencia fixo contra o qual a tese e
medida. As tres alternativas rejeitadas estao argumentadas em `_history/_round12/47`.

**Sobre o $\mathbf{e}_{p_i}$: voce estava meio certo, e a metade importa.** O $\mathbf{e}_p$ **fica** na
tarefa estatica, porque ela e quantificada sobre POIs e nao existe indice de check-in ali; renomear
faria uma tarefa estatica parecer sequencial. O que uma POSICAO de historia carrega e $\mathbf{e}_{p_j}$,
a composicao de $j\mapsto p_j$ com $p\mapsto\mathbf{e}_p$, e o projeto tira essa composicao da prosa e a
poe numa equacao. A sua descoberta 4 se dissolve nessa fatoracao: a equacao
$f_{\mathrm{place}}(H_i)\longrightarrow p_i$ esta correta como esta.

**Um defeito que nenhum de nos dois listou:** $c_p$ aparece LIVRE na Definicao 2.3. Medido: ocorre uma
unica vez na prosa viva, dentro daquela definicao, sem introducao previa; e a linha do
$g_{\mathrm{cat}}$ no GLOSSARY §1.1 ja o usa, ou seja, o registro antecipava a ligacao que faltava.

**Nenhum probe quebra.** Os 21 probes que pinam este capitulo continuam verdes e as tres cadeias pinadas
(`R12-eqxi`, `R12-fplace`, `R12-fplace2`) foram carregadas caractere por caractere no projeto. Verificado
por mim, nao aceito do relatorio.

> **DECISAO SUA 1 — doze definicoes ou treze.** O mapa $\rho$ pode entrar como uma **definicao numerada**
> (fica 2.1-2.13, e o mapa ganha o mesmo peso visual das outras) ou como uma **equacao em display** na
> prosa que antecede as tarefas (fica em doze, e o mapa aparece como notacao). As duas formas estao
> especificadas em `_history/_round12/47` §3. Nao ha diferenca matematica; a diferenca e o quanto voce quer que a
> fatoracao "mesma tarefa, representacao variavel" salte aos olhos de quem le, dado que ela e a forma
> logica da sua tese.
>
> **RESPONDIDA — TREZE.** Palavras dele em 2026-08-03: "Vamos de treze" (§6.15, decisao 1). O $\rho$ e hoje a
> **Definicao 2.5** do capitulo, aplicada nesta rodada. Residuo de formatacao; **nao gaste decisao aqui.**

> **DECISAO SUA 2 — como chamar a entrada do Capitulo 4.** O projeto descreve a entrada dos Capitulos 3 e
> 4 como de nivel de lugar, e para o Capitulo 4 isso e impreciso. Medido em
> `4_courb/methodology.tex:153`: o componente temporal "represents the timestamp of each check-in", e
> `:144` diz que ele mapeia "the temporal values of each check-in (hour of day and day of week)". Ou seja
> a concatenacao do Capitulo 4 tem um canal que varia POR VISITA, mesmo com o canal categorico
> (HGI) sendo por lugar. Tres saidas:
> 1. **Chamar o Capitulo 4 de hibrido** — dois canais por lugar mais um por visita. Mais preciso, e
>    enfraquece um pouco a linha narrativa "lugar -> check-in" que o Capitulo 5 fecha.
> 2. **Manter "nivel de lugar" com uma ressalva de uma frase** nomeando o canal temporal como a excecao.
>    Preserva a narrativa e nao esconde o fato.
> 3. **Manter como esta** — o vetor ainda e indexado pelo lugar visitado no Capitulo 4, e o canal temporal
>    e uma feature dele. Defensavel, mas um leitor atento do `methodology.tex` pode perguntar.
> O Capitulo 4 e versao de registro e nao muda; a decisao e sobre como o Capitulo 2 o descreve.
>
> **RESPONDIDA — FORMA NEUTRA (a AD-2 fechou na opcao B).** §6.22: o nivel do canal temporal do Cap. 4 **nao**
> e registrado como errata, o Cap. 2 usa "a vector that is a function of the visited POI", e as duas redacoes
> erradas seguem proibidas. Aplicado ao `.tex` no passo 5 desta rodada (`R12-s5neutral`), e o assunto esta
> encerrado como **LO-12** no `LEFT_OUT.md`. Residuo de formatacao; **nao gaste decisao aqui.**

**PASSE DE VALIDACAO ADVERSARIAL — cinco defeitos, todos de redacao, nenhum estrutural.** Um segundo
agente fable-5 reconstruiu o grafo de dependencias por conta propria e enumerou os 21 probes contra o
texto PROPOSTO. **Estrutura aprovada; zero probes quebram.** Mas achou tres coisas que teriam entrado
erradas, e eu conferi as tres no fonte:

- **F-1, e e a que importa.** O projeto dizia que a instanciacao do Capitulo 5 e $\rho(x_i)=\mathbf{e}_{x_i}$.
  `5_mobiwac/04_method.tex:27` diz outra coisa: "the category task reads the window of per-visit vectors
  (the semantic stream); the region task reads the same window of visits, **each visit now represented by
  the trained vector of its region node** from the same graph (the spatial stream)". Sao DUAS correntes,
  nao uma. Aplicado como estava, o Capitulo 2 descreveria errado justamente o estudo em que o arco se
  resolve. A conclusao estrutural nao muda: $H_i$ cru mais um $\rho$ nomeado continua valendo, e o $\rho$
  simplesmente tem duas instanciacoes ali.
- **F-2.** "every predictive model in this dissertation reads $\rho(H_i)$" e falso para a tarefa estatica:
  `2_fundamentals.tex:116-124` mostra $g_{\mathrm{cat}}(\mathbf{e}_p)\to c_p$, sem historia nenhuma. E a
  tarefa estatica e exatamente a que o `apx_b_static_scope` existe para manter separada.
- **F-4, que fecha um item aberto do proprio projeto.** Ele anotava que "os estudos" preenchem janelas
  curtas com zeros. `5_mobiwac/05_setup.tex:28`: "we keep only the full-length window ending there and
  **drop these padded duplicates**". O Capitulo 5 descarta, nao preenche.
- **F-3** (o PAR de tarefas muda no Capitulo 5, entao a frase correta e "hold the task definitions fixed")
  e **F-5** ($d$ ja esta em uso vivo nos capitulos publicados como dimensao e como distancia $d_{ij}$,
  entao a linha de registro precisa de nota de escopo em vez de alegar notacao livre).

**Plano de edicao em 8 passos** escrito em `_history/_round12/49`, com os passos 3-5 obrigatoriamente no mesmo
commit, os comandos que encontram cada referencia cruzada, e o aviso de validar cada probe por sabotagem
lendo o resultado ANTES de restaurar.

> **DECISAO SUA 3 — como o Capitulo 2 enuncia a entrada de duas correntes do Capitulo 5** (nova, vem do
> F-1). Duas saidas:
> 1. **Nomear as duas correntes na propria observacao** — precisa, e antecipa no Capitulo 2 um detalhe de
>    arquitetura que o Capitulo 5 explica.
> 2. **Dizer so que o Capitulo 5 instancia no nivel de check-in e remeter as correntes ao Capitulo 5** —
>    mais leve, e deixa a observacao incompleta para quem le so o Capitulo 2.
>
> **RESPONDIDA — NOMEAR AS DUAS.** §6.15, decisao 2, pelo "respectivamente" dele. O comentario de fatoracao da
> §2.1 nomeia hoje a corrente semantica e a espacial, aplicado nesta rodada (`R12-s3scope` pina o escopo).
> Residuo de formatacao; **nao gaste decisao aqui.**

---

### ~~6.15 Rodada 12 — as suas tres respostas, e a decisao 2 volta com a pergunta consertada~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** as tres respostas aplicadas; a decisao 2 fechada no §6.22.

**Decisao 1 — TREZE. FECHADA.** "Vamos de treze." O $\rho$ entra como definicao numerada e o capitulo
passa a 2.1-2.13. Consequencia mecanica conferida, nao assumida: a renumeracao desloca tudo depois do
$\rho$, entao cada `\ref{def:fund:*}` sera reconferido na aplicacao; e o probe `R11-def27` pina
`\label{def:fund:checkinlevel}`, que e um LABEL e nao um numero, logo a renumeracao nao pode quebra-lo
(verificado contra a tupla de probes carregada, nao contra a minha memoria dela).

**Decisao 3 — NOMEAR AS DUAS CORRENTES. FECHADA.** Voce confirmou o defeito F-1 e deu o mecanismo: "o
HGI produz dois embeddings finais um de regiao e outro de checking, e usamos essas duas entradas,
respectivamentte, next-region e next-category". O "respectivamente" e o que decide a favor de nomear as
duas em vez de remeter ao Capitulo 5, e a observacao de fatoracao no `fundamentals/DEFINITIONS.md` ja diz
exatamente isso, com a citacao de `5_mobiwac/04_method.tex:27`.

**Decisao 2 — REABERTA, porque a minha pergunta estava mal posta e o codigo mostra isso.** Voce pediu o
estudo no codigo e em `docs/`, e ele **inverte a premissa**. Nao ha transformacao de nivel de check-in
para nivel de POI no pipeline do Time2Vec: nao existe `groupby`, media, nem reducao por POI em lugar
nenhum. O que existe e uma **recusa**:

- `src/data/inputs/builders.py:40` poe `TIME2VEC` em `_CHECKIN_LEVEL_ENGINES`;
- `builders.py:191-192`, o construtor da entrada da tarefa de categoria, **levanta erro** nesses engines:
  "Rejects check-in-level engines (Time2Vec, Check2HGI) -- category task requires one embedding per POI";
- `research/embeddings/time2vec/README.md:66-69` diz o mesmo e aponta aquele arquivo como o lugar da
  recusa, e declara a saida como `N_checkins x (6 metadata + 64 dims)`;
- `docs/context/EMBEDDINGS.md:83` "Type: Check-in-level (one embedding per visit event)", e :103-104 diz
  que a janela do next vira "a true spatio-temporal trajectory, **not just a POI sequence**".

**E a tensao esta DENTRO do capitulo publicado, nao so entre a prosa e o codigo.** O `methodology.tex:93`
diz que "each POI is represented by the embedding resulting from the concatenation of the three
components, $\mathbf{E}_{cat}=[\mathbf{E}_{HGI}\|\mathbf{E}_{loc}\|\mathbf{E}_{time}]$ ... forming pairs
$(\mathbf{E}_{cat},c)$ where $c$ is the real category of the POI" — o que exige um valor de
$\mathbf{E}_{time}$ por POI. O `:153` diz que $\mathbf{E}_{time}$ "represents the timestamp of each
check-in" — um valor por CHECK-IN. **As duas frases nao podem ser ambas verdadeiras como estao escritas.**

**O que eu NAO posso resolver, e por que.** Nao consigo estabelecer o que a RODADA PUBLICADA do CoUrb
fez. O capitulo e versao de registro de experimentos anteriores; o codigo em disco e o de hoje. Tres
possibilidades ficam abertas e so voce fecha, porque distinguir precisa dos artefatos da rodada e nao da
arvore de fontes:
1. a rodada publicada agregava o $\mathbf{E}_{time}$ para nivel de POI, e esse passo foi removido depois;
2. a tarefa de categoria da rodada publicada rodou SEM o canal temporal, e o `:93` superdeclara a entrada;
3. a rodada publicada antecede a guarda e alimentou a tarefa de categoria com vetores de nivel de
   check-in, o que faria os numeros publicados de categoria descreverem uma entrada diferente da que o
   `:93` afirma.

Se a resposta for (2) ou (3), e materia de errata sob o `NORTH_STAR` §5.7, e o apendice de errata **nao**
carrega isso hoje (conferido: ele trata do lead da tabela de categoria e de um re-typeset tipografico
desta mesma passagem em `:311-318`, e nada sobre o nivel do canal temporal). **O Capitulo 4 nao foi
editado**, e nem sera por mim: e versao de registro.

**Consequencia para o Capitulo 2, que era o motivo da decisao.** A minha opcao 3 estava ERRADA, nao certa:
`EMBEDDINGS.md:103-104` diz que a janela do next explicitamente nao e uma sequencia de POIs. E eu **nao
posso** escrever que o canal temporal e agregado ao lugar, que e o texto que a sua premissa produziria —
e a unica afirmacao que o codigo refuta. O que o Capitulo 2 pode dizer, e continuar verdadeiro sob as
tres possibilidades, e que o Capitulo 4 troca o vetor monolitico por uma representacao DECOMPOSTA cujos
componentes sao aprendidos por encoders separados, sem afirmar um nivel unico para o resultado.

> **DECISAO SUA — qual das tres possibilidades vale, e o que fazer com o `:93`.** As opcoes nao sao
> simetricas em custo:
> 1. **Voce confirma (1), que houve agregacao na rodada publicada.** Entao o `:93` esta certo, o `:153`
>    esta incompleto, e o Capitulo 2 pode dizer "nivel de lugar" nomeando a agregacao. Precisa do
>    artefato ou do commit que a fazia.
> 2. **Voce confirma (2), a categoria rodou sem o canal temporal.** Entao o `:93` superdeclara e vira
>    linha de errata; os numeros publicados continuam validos, so a descricao da entrada muda.
> 3. **Voce confirma (3).** Custo maior: os numeros de categoria descrevem uma entrada diferente da
>    declarada, e a errata tem de dizer isso.
> 4. **Deixar em aberto com um `[VERIFY]` no Capitulo 4** e o Capitulo 2 usando a redacao neutra
>    ("representacao decomposta", sem nivel). Nao resolve, mas nao arrisca uma afirmacao falsa, e mantem
>    o Capitulo 2 destravado enquanto voce busca o artefato.
>
> **RESPONDIDA — OPCAO B, e a pergunta deixou de ter resposta obtivel.** §6.22: ele nao tem o artefato, entao a
> AD-2 fica em `[VERIFY]` e o assunto esta **encerrado** como **LO-12**. Vale registrar que a minha propria
> resposta anterior a esta pergunta foi **RETRATADA** (§6.21): ela repousava num elo entre dois arquivos que eu
> nunca verifiquei. Residuo de formatacao; **nao gaste decisao aqui.**

---

### ~~6.16 Rodada 12 — AD-5 e AD-6 fechadas, e o AD-4 virou uma questao maior do que a que eu fiz~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** AD-5 e AD-6 fechadas; o AD-4 resolvido no §6.24 (opcao (a)).

**AD-5 — FECHADA.** As duas linhas de registro do §6.13 estao autorizadas: $\mathbf{e}_{x_i}$ e
$f_{\mathrm{place}}(H_i)$. E com treze definicoes a linha do $\rho$ deixa de ser opcional e passa a ser
**necessaria**, porque o $\rho$ agora e um objeto numerado do capitulo e nao mais notacao de prosa.

**AD-6 — FECHADA: afiar.** A frase e `2_fundamentals.tex:85`, dentro da D2: "A target label is withheld
from it when one of the sequential tasks is trained." Antes de reescrever, medi o que ela precisa dizer, e
ha um ponto que muda o objetivo do conserto:

- **Qual rotulo depende da tarefa**, e isso e a razao de ela estar vaga. A Definicao 2.1 da
  $x_i=(u,p_i,t_i,c_i,r_i)$, entao o alvo e $c_i$ para next-category e $r_i$ para next-region. Uma frase
  so nao pode fixar um campo, e afiar sem partir em duas exige nomear o alvo **como funcao da tarefa**.
- **O que e retido nao e um campo da HISTORIA.** O $H_i=(x_{i-\ell},\ldots,x_{i-1})$ ja **exclui** o
  $x_i$ por construcao, e e no $x_i$ que o alvo vive. Os elementos da historia mantem categoria e regiao.
- **E aqui esta o defeito real da frase atual:** como esta escrita, ela convida a leitura oposta, de que
  as categorias sao apagadas da historia, o que seria uma descricao FALSA dos dados. O proprio MobiWac diz
  o contrario em `5_mobiwac/05_setup.tex:76`: "a per-visit vector legitimately carries more than the
  previous category, including the place, its neighborhood, and the hour of the visit". Ou seja, afiar
  nao e cosmetico: e trocar uma frase que pode ser lida errado por uma que diz de onde o alvo sai e o que
  **permanece** disponivel.

---

**AD-4 — a sua resposta e maior do que a minha pergunta, e o seu argumento e melhor do que o do projeto.**

Eu perguntei so o **titulo** de uma subsubsecao dentro da §2.1. Voce respondeu propondo **inverter a
ordem**: representacao primeiro, com a definicao formal ali, e depois as tarefas que se pode treinar com
essas representacoes. E voce mesmo pos a ressalva: "a narrativa tem que esta acima desse problema, temos
que ter muito cuidade".

**O argumento e melhor.** O projeto move duas definicoes para DENTRO da secao de tarefas para tirar a
dependencia para frente. Voce a elimina na RAIZ: se a representacao vem primeiro, nada precisa se mover,
porque as tarefas passam a consumir objetos que o leitor ja tem. E a ordem de leitura passa a espelhar a
propria tese, que e a de que a representacao e o fator dominante.

Como voce pediu cuidado, o custo, medido:

| custo | o que e | tamanho |
|---|---|---|
| referencias cruzadas | so **tres** referencias vivas aos dois labels, **todas dentro do proprio `2_fundamentals.tex`** (`sec:fund:tasks` x1, `sec:fund:repr` x2). Nada fora do capitulo aponta para eles. | pequeno |
| prosa que fica FALSA | `:14-20`, a abertura do capitulo, enuncia a ordem em prosa com os refs ("It **first** distinguishes the POI prediction tasks... It **then** traces mobility representations"); e `:27`, a abertura da §2.1, e a **justificativa explicita** da ordem atual ("This section defines the prediction targets **before** reviewing the methods used for them"). Essa segunda nao fica so obsoleta: fica uma afirmacao falsa sobre a estrutura do proprio capitulo. | duas reescritas |
| **estrutura do capitulo** | a ordem 2.1-2.5 esta **fixada no mapa do capitulo**, `NORTH_STAR.md:73-80`, e o escopo do projeto diz para nao inventar secoes. Inverter 2.1 e 2.2 **edita o mapa**, e e outra ordem de magnitude em relacao a nomear uma subsubsecao. | **e a razao de a decisao ser sua** |
| gates | **nenhum.** Medi todos os `check_*.py` e o `check.sh`: os quatro arquivos que mencionam "2.1" falam de itens do PENDENCIAS ou de fixtures de teste, nao do capitulo; e o `R11-fab15` pina uma frase da INTRODUCAO, nao a ordem. | zero |
| efeito colateral | `fundamentals/` tem diretorios `2.1_poi_prediction_tasks` e `2.2_representations_for_mobility`. A pasta e provenance congelada e os nomes registram como o capitulo **foi** construido, entao nao e erro, mas passa a descrever outra ordem. | anotar |

> **DECISAO SUA — e eu separei em duas porque sao decisoes diferentes de tamanhos diferentes.**
>
> **(a) O AD-4 como eu perguntei.** Uma subsubsecao dentro da §2.1 com o titulo que voce der, a ordem das
> secoes intacta, e o plano de 8 passos vale como esta. Resolve a dependencia para frente e nao toca o
> mapa. Custo: as duas definicoes de representacao passam a viver na secao de tarefas, que e exatamente o
> arranjo que o seu argumento diz ser menos natural.
>
> **(b) A inversao 2.1 <-> 2.2 que voce propos.** Item NOVO, maior, e uma mudanca de estrutura de
> capitulo. Ganha a ordem de leitura que espelha a tese e nada precisa se mover para dentro de secao
> alheia. Custo: reescrever `:14-20`, reescrever `:27`, e uma decisao sua sobre alterar o mapa do
> `NORTH_STAR`. As tres referencias cruzadas sao triviais.
>
> Se escolher (b), eu **nao** executo junto com o resto do round sem essa linha explicita: e mudanca de
> estrutura, e o plano de 8 passos foi escrito para (a).
>
> **RESPONDIDA — OPCAO (a), E A INVERSAO ESTA ENCERRADA.** §6.24, decisao dele de 2026-08-03: "MANTER A ORDEM.
> Opcao (a) do _history/_round12/53 — 2.1 tarefas, 2.2 representacoes. A inversao esta encerrada, nao suspensa." O
> redesenho foi aplicado ao capitulo nesta rodada. Residuo de formatacao; **nao gaste decisao aqui.**

**Fora de escopo, e eu tinha listado indevidamente:** o `src_utils/_history/NEEDS_SIGN_OFF.md` (56 marcadores). Voce
foi explicito de que este round e sobre as definitions. Retirado daqui; segue em aberto no lugar dele.

**AD-2 continua pre-requisito e nao paralela.** Voce pediu o estudo antes da resposta concreta, e ele esta
feito: `_history/_round12/50_courb_temporal_level_investigation.md`. O resultado inverte a premissa (nao existe
agregacao; o construtor da tarefa de categoria **recusa** o canal temporal) e deixa tres possibilidades
que so os artefatos da rodada publicada distinguem. O §6.15 as lista com o custo de cada uma.

---

### ~~6.17 Rodada 12 — AD-4 fechada sob condicao, e um erro meu de relato que voce pegou~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** AD-4 fechada e o titulo escolhido por voce no §6.24, ja aplicado.

**PRIMEIRO, O MEU ERRO, porque voce o pegou e eu nao.** Foi relatado a voce que o
`fundamentals/DEFINITIONS.md` nunca chegou a ser escrito, porque o kernel reiniciou duas vezes durante a
aplicacao das seis correcoes. Voce respondeu: "Voce esta equivocado: articles/dissertacao/fundamentals/
DEFINITIONS.md, acredito ser esse arquivo." **Voce estava certo.** Conferido em disco e no git: 43.509
bytes, 560 linhas, commitado e limpo (`6e43663b`, depois `ae843c78`), com as seis correcoes presentes na
copia commitada — `with TWO` (F-1) x1, `the trained vector of its region node` x2, `SEQUENTIAL tasks` x2,
`hold the task DEFINITIONS fixed` x3, `Chapter 5 DROPS the padded windows` x1, `the letter $d$ is NOT
unclaimed` x1. O relato descrevia o estado de ANTES da escrita e nao foi reconferido depois dela. A licao e
a mesma que o `_history/_round9/34` ja carrega em outras formas: **um estado que eu observei uma vez nao e um estado
que eu observo agora**, e "o kernel reiniciou" descreve o meu processo, nao o disco.

**AD-4 — FECHADA SOB CONDICAO, e a condicao pode cancelar a subsecao.** Suas palavras: "vamos de `Cheking
and place representation`, but as I said we need to create a better plan for it, maybe with this
inveration we even need this new section."

O titulo fica **"Check-in and place representation"**. Voce escreveu "Cheking"; o `GLOSSARY` registra
**check-in** (14 ocorrencias, "never 'event'") e `checking` aparece **zero** vezes, entao a grafia canonica
e essa. **Um ponto de registro que eu prefiro te mostrar a substituir em silencio:** `place embedding`
esta registrado e `place representation` **nao** esta (zero ocorrencias). A segunda metade do seu titulo e
portanto uma variante nao registrada de um termo que existe. Tres saidas:
1. **Manter "Check-in and place representation"** e registrar `place representation` no §1.1 — a linha e
   sua, e o termo passa a ser canonico. Le melhor e e o que voce pediu.
2. **"Place embedding and check-in-level representation"** — as duas metades ja registradas, e sao
   literalmente os titulos das duas definicoes que a subsecao hospedaria. Mais longo, e e exatamente a
   cabeca dupla que a rodada 11 **separou** por juntar dois conceitos sob um nome.
3. **Manter o titulo e nao registrar nada** — funciona na pratica, mas deixa a regra fail-closed esticada,
   que e o mesmo estado que produziu a divida do `soft parameter sharing` e do `negative transfer`.

> **RESPONDIDA — "Check-in and place embedding", escolha dele, ja aplicada.** §6.24. Ele nomeou o titulo
> explicitamente depois que a revogacao de `place representation` invalidou o que ele havia dado antes, e o KC-1
> se fechou na forma que ele mesmo definiu. Esta no `2_fundamentals.tex` e o `R12-s3head` dispara se derivar
> para o termo revogado. Residuo de formatacao; **nao gaste decisao aqui.**

**Mas a sua propria condicao e a parte que manda:** "maybe with this inversion we even need this new
section". Se a §2.2 vier primeiro, as definicoes de representacao **ja estao na secao certa** e um
compartimento dentro da secao de tarefas fica sem funcao. Entao o titulo e uma resposta **condicional** e
nao uma autorizacao para criar a subsecao. Nao criei nada.

**AD-5 e AD-6 — fechadas, registradas no §6.16.** Com treze definicoes a linha do $\rho$ passa de opcional
a **necessaria**.

**AD-2 — continua aberta, e o estudo que voce pediu esta feito** (`_history/_round12/50`). Ele **inverte a
premissa**: nao existe agregacao de check-in para POI no pipeline, e o construtor da entrada da tarefa de
categoria **recusa** o canal temporal (`builders.py:191-192`). O `§6.15` lista as tres possibilidades que
sobram, com o custo de cada, e todas as tres precisam dos artefatos da rodada publicada — nao da arvore de
fontes — para serem distinguidas.

**O ITEM MAIOR CONTINUA SEM DECISAO: a inversao §2.1 <-> §2.2.** Nao e o AD-4 e nao deve ser fechada como
se fosse. O custo esta medido no `§6.16` e agora tambem no `fundamentals/DEFINITIONS.md` §11: tres
referencias cruzadas (todas dentro do capitulo), duas passagens de prosa que ficam **falsas** (`:14-20` e
`:27`), o mapa fixado do capitulo em `NORTH_STAR.md:73-80`, e **zero** gates. E a consequencia que importa
para o cronograma: **o plano de 8 passos foi escrito para a outra forma e nao sobrevive a inversao.** Ele
tem de ser refeito ANTES de qualquer edicao, nao ajustado depois.

Sua ordem de trabalho esta registrada e sera respeitada: "depois dessas definicoes podemos aplicado."
Nenhuma edicao no `.tex` foi feita.

---

### ~~6.18 Rodada 12 — a AD-2 esta RESPONDIDA pelo codigo original, e a resposta e uma quarta possibilidade~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** a AD-2 foi RETRATADA no §6.21 e encerrada no §6.22 como LO-12.

Voce disse: "Calma analise o codigo original do chap. 4: /Users/vitor/Desktop/mestrado/temp/tarik-new,
antes de decidirmos." **Era exatamente a fonte que faltava**, e ela fecha o que o `_history/_round12/50` dizia que
so os artefatos da rodada publicada poderiam fechar. **Nenhuma das tres possibilidades que eu listei era a
certa.**

**1. O embedding temporal e por CHECK-IN, e a prova esta nos outputs guardados do proprio notebook, nao na
leitura da intencao do codigo.** `Time_Encoder.ipynb`, California:

| celula | output guardado | o que significa |
|---|---|---|
| 2 | `N checkins (antes de filtrar): 2535573` | a entrada e a tabela de check-ins |
| 3 | `(2535573, 2)` | duas features por check-in (`t_hour = hora/24`, `t_dow = dia/7`) |
| 13 | `time_embeds_sin shape: (2535573, 64)` | **uma linha de 64 dimensoes por check-in** |

Como as features sao hora e dia da semana **por check-in**, duas visitas ao mesmo POI em horarios
diferentes produzem vetores **diferentes**. A celula 14 monta o frame indexado por `placeid` e grava num
caminho cujo nome ja diz o nivel, `time_encoder_embeddings_sin_CHECKIN_{estado}.csv`; a 15 copia para
`data/output/{estado}/time_embedding_novo.csv`, que e o que o ETL le.

**2. E a entrada da tarefa de categoria reduz de check-in para POI DESCARTANDO LINHAS, nao agregando.**
`PoiMtlNet_Novo/src/etl/create_inputs_hgi.py:437`, literal:

    time_df = time_emb[["placeid"] + num_cols_time].drop_duplicates("placeid")

Com uma linha por check-in indexada por `placeid`, o `drop_duplicates("placeid")` **mantem a primeira
ocorrencia de cada POI e joga as outras visitas fora.** Os tres componentes sao then unidos por `placeid`
(:441-443) e a categoria anexada por `placeid` (:448), o que produz os pares $(\mathbf{E}_{cat}, c)$ do
`methodology.tex:93`. O default do `process_state` e `cat_embeddings=("poi","loc","time")`, entao o canal
temporal **esta** na entrada da categoria.

**A RESPONSTA, e por que ela nao estava entre as tres.** Existe uma reducao de check-in para POI, e ela e
`drop_duplicates`, **nao uma agregacao**. O seu instinto de que algo converte o nivel estava certo; a
operacao nao e media nem pooling, ela **seleciona uma visita arbitraria por POI**. Ou seja: o canal
temporal que chega a tarefa de categoria carrega o timestamp de **uma** visita, nao um resumo das visitas
daquele POI, e a variacao que o encoder foi construido para capturar e descartada nessa tarefa.

| possibilidade que eu havia listado | veredito |
|---|---|
| (1) agregacao removida depois | **a mais proxima, e errada na palavra que importa.** A reducao existe e **continua** no codigo original. Nao e agregacao. |
| (2) a categoria rodou sem o canal temporal | **refutada.** O `cat_embeddings` inclui `time` por default. |
| (3) vetores de nivel check-in na tarefa de categoria | **refutada para a categoria.** Sao reduzidos a um por `placeid` antes. |

**O QUE ISSO DIZ SOBRE O `:93` E O `:153`, e a conclusao e mais branda do que eu temia.** As duas frases
sao **individualmente corretas**: o `:153` esta certo de que o encoder produz um vetor por check-in, e o
`:93` esta certo de que um vetor de 192 dimensoes em nivel de POI e pareado com a categoria do POI. **O que
o texto publicado nunca enuncia e o passo entre as duas**, e esse passo perde informacao de um jeito que um
leitor gostaria de saber: uma visita por POI sobrevive e as demais sao descartadas.

Isso e **lacuna de descricao, nao numero errado** — os pares com que a tarefa de categoria treinou sao
exatamente os que o `:93` descreve. Se o capitulo deve registrar o passo de selecao e materia de **errata**
sob o `NORTH_STAR` §5.7, e o `apx_b_errata.tex` nao a carrega hoje. **O Capitulo 4 nao foi editado.**

> **DECISAO SUA — o que fazer com a lacuna:**
> 1. **Linha de errata** registrando que o canal temporal e reduzido a uma visita por POI por selecao da
>    primeira ocorrencia. Custo: uma linha na tabela de errata do Cap. 4. Ganho: a descricao passa a
>    corresponder ao que rodou, e ninguem reproduzindo o trabalho se surpreende.
> 2. **Nao registrar**, tratando como detalhe de implementacao. Nenhum numero muda e o `:93` continua
>    verdadeiro. Risco: um leitor atento que rode o codigo encontra o `drop_duplicates` e conclui que o
>    texto o omitiu.
> 3. **Registrar so no Capitulo 2**, na frase que descreve a entrada do Cap. 4, sem tocar a errata.
>
> **RESPONDIDA — OPCAO 2, NAO REGISTRAR.** Ele decidiu em 2026-08-03; a resposta esta no **§6.20, item 3**,
> e o encerramento definitivo no **§6.22** (a AD-2 fechou como `[VERIFY]` e o assunto virou o `LO-12` do
> `LEFT_OUT.md`). Este `______` era **residuo de formatacao**: o menu ficou aberto depois de a decisao ter
> sido tomada em outra secao. **Nao gaste decisao dele aqui.** O que ficou aplicado no capitulo: a forma
> neutra ("a vector that is a function of the visited POI"), com as duas redacoes erradas seguindo
> proibidas — aplicado ao `.tex` no passo 5 desta rodada, probe `R12-s5neutral`.

**O que o Capitulo 2 pode dizer agora, e ja esta corrigido no `fundamentals/DEFINITIONS.md` §3:** a
instanciacao do Cap. 4 dizia "de uma funcao do POI visitado e, no Cap. 4, do timestamp da visita". Isso
agora esta provado **impreciso**: o timestamp e de **uma visita selecionada**, nao da visita naquela
posicao da janela. As duas redacoes erradas estao nomeadas no arquivo: "do timestamp da visita" e
"agregado".

---

### ~~6.19 Um item que nunca chegou a voce: a sobrecarga de indices na D13 (AD-7)~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** AD-7 respondida (opcao 1, renomear); a renomeacao esta registrada no desenho.

Estava no §9 do `DEFINITIONS.md` como item 4 e nunca virou decisao. Na definicao de conflito de gradiente,
o $\mathbf{g}_i$, o $\mathbf{g}_j$ e o $\varphi_{ij}$ indexam **tarefas**; em todo o resto do capitulo o
indice $i$ indexa **check-ins** ($x_i$, $H_i$, $\mathbf{e}_{x_i}$). Conferido no bloco vivo.

Um leitor que acompanha os indices ao longo do capitulo tropeca nisso. **Escopo do probe, dito com
precisao em vez de superdimensionado:** o `R10-cosine` pina a string `def:fund:conflict`, que e o **label**,
entao uma renomeacao de indices nao o quebraria; o que uma renomeacao arrisca e a prosa ao redor e o
apendice que aponta de volta para essa definicao.

> **DECISAO SUA:**
> 1. **Renomear os indices da D13** para algo como $a$ e $b$ (tarefas), deixando o $i$ livre para
>    check-ins em todo o capitulo. Custo: a equacao `eq:fund:cosine`, a prosa ao redor, e conferir o
>    apendice que referencia a definicao.
> 2. **Deixar como esta e adicionar meia frase** dizendo que ali os indices sao de tarefa. Custo minimo,
>    resolve para o leitor atento, mantem a notacao da fonte (`yu2020pcgrad` usa $i$ e $j$ para tarefas).
> 3. **Nao fazer nada.** E convencao da literatura e ninguem reclamou.
>
> **RESPONDIDA — OPCAO 1, RENOMEAR.** Ele decidiu em 2026-08-03; a resposta esta no **§6.20, item 2**
> (AD-7). Este `______` era **residuo de formatacao**, como o do §6.18. **Nao gaste decisao dele aqui.**
> Estado do trabalho: a renomeacao esta registrada no `fundamentals/DEFINITIONS.md` (a D13 passa a usar
> $\mathbf{g}_a$, $\mathbf{g}_b$ e $\varphi_{ab}$) e **ainda nao esta no capitulo** — ela entra quando a D13
> for tocada, porque editar o `.tex` antes disso dessincronizaria o desenho e o capitulo. Os dois probes
> daquela definicao (`R9-conflict`, `R10-cosine`) foram testados contra o texto real e sobrevivem a
> renomeacao.

---

### ~~6.20 Rodada 12 — as suas quatro decisoes, e o que cada uma NAO autoriza~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** as quatro decisoes aplicadas; o item 4 depois revogado por voce no §6.22.

**ITEM 1 — A INVERSAO §2.1 <-> §2.2: voce autorizou o ESTUDO, nao a mudanca.** "Use um fable 5 para
explorar e validar a inversao, vale ler o articles/dissertacao/fundamentals, onde planejamos o fundamentos
no principio." Um agente `claude-fable-5` esta rodando com esse escopo e com escrita limitada a **um**
arquivo novo (`_history/_round12/52_inversion_study.md`); ele nao pode tocar `.tex`, `GLOSSARY`, `NORTH_STAR` nem
este arquivo.

**A sua escolha de fonte foi boa e vale dizer por que.** A pasta `fundamentals/` e o registro **congelado**
de como o Cap. 2 foi planejado, e os diretorios dela sao literalmente `2.1_poi_prediction_tasks`,
`2.2_representations_for_mobility`, e assim por diante — ou seja, ela carrega o raciocinio original da ordem
que a inversao quer trocar. **Uma medicao previa, que o agente vai confirmar ou refutar:** varri a pasta por
palavras de ordem ("order", "before review", "first distinguish", "sequence") e **nenhum arquivo argumenta a
ordem**. O `fundamentals.tex` apenas monta 2.1 a 2.5 na sequencia. Se isso se confirmar, o achado e que a
ordem foi **herdada do escopo do projeto e nunca defendida**, o que enfraquece o argumento de tradicao
contra a inversao. Nao vou tratar isso como fechado antes do relatorio.

**ITEM 2 — AD-7, OPCAO 1: RENOMEAR OS INDICES DA D13.** Feito **no desenho**, nao no capitulo. O
$\mathbf{g}_i,\mathbf{g}_j,\varphi_{ij}$ passam a $\mathbf{g}_a,\mathbf{g}_b,\varphi_{ab}$, liberando o $i$
para check-ins em todo o capitulo.

Duas medicoes que corrigem o que eu havia dito antes:
- **O escopo e menor do que a minha nota de custo sugeria.** Os simbolos aparecem em **seis linhas vivas**,
  todas dentro do bloco da D13 (`2_fundamentals.tex:888-895`), e **em nenhum outro lugar da arvore**. O
  apendice do cosseno menciona o conceito num comentario e nunca o label nem os simbolos, entao a minha
  frase de que a renomeacao "exige conferir o apendice" era mais larga do que a evidencia.
- **Os dois probes sobrevivem, testado e nao raciocinado.** Apliquei a renomeacao ao texto real do capitulo
  e rodei os padroes: o `R9-conflict` casa `cosine between their gradients` (prosa, sem simbolos) e o
  `R10-cosine` casa o label `def:fund:conflict`. Ambos valem antes e depois.

**Por que no desenho e nao no capitulo agora:** o §5 do `DEFINITIONS.md` especifica a D13 e o redesenho
ainda esta pendente. Editar o capitulo hoje poria o capitulo e o desenho fora de sincronia justamente na
janela em que o redesenho espera decisao. Entra junto com o redesenho.

**ITEM 3 — ERRATA DO AD-2, OPCAO 2: NAO REGISTRAR.** A reducao check-in para POI por
`drop_duplicates("placeid")` fica como detalhe de implementacao. Nenhum numero muda, o
`methodology.tex:93` continua verdadeiro, o `apx_b_errata.tex` nao recebe linha, e o Capitulo 4 segue
intocado como versao de registro.

> **UM PONTO QUE A SUA DECISAO NAO COBRE, e que eu registrei no desenho para quem for aplicar:**
> "nao registrar" e **silencio**, nao licenca para escrever a coisa errada. A instanciacao do Cap. 4 no
> `DEFINITIONS.md` §3 dizia "uma funcao do POI visitado e, no Cap. 4, do timestamp da visita", e isso esta
> **provado impreciso**: o timestamp e de **uma visita selecionada** (a primeira por `placeid`), nao da
> visita naquela posicao da janela. Sob a opcao 2 o Cap. 2 escreve a forma **neutra** — "uma funcao do POI
> visitado", sem qualificacao temporal — e as duas redacoes erradas continuam **proibidas**: "do timestamp
> da visita" (falsa) e "agregado" (a operacao seleciona, nao combina). Os probes `R12-dropdup`,
> `R12-shape`, `R12-notwrong` e `R12-notagg2` guardam isso.

**ITEM 4 — `place representation` ENTRA NO REGISTRO.** Linha adicionada ao `GLOSSARY.md` §6 ao lado de
`place embedding`. Com isso o titulo do AD-4 fica **"Check-in and place representation"** com as duas
metades registradas (a grafia canonica e `check-in`; `checking` nao existe no registro).

**Mas registrei com uma nota de escopo, porque duas linhas quase sinonimas colidem com o §5 do
`WRITING_LAW`** ("One name per concept for the whole document; synonym-cycling is both imprecise and an AI
tell"). A nota admite `place representation` em **titulos e cabecalhos**, onde faz paralelo com
`check-in-level representation`, e mantem `place embedding` como o nome canonico **na prosa corrida**. Sem
isso, a linha nova licenciaria exatamente a rotacao que a lei proibe. Se voce preferir sem a nota, e uma
linha sua.

**E isto nao cria a subsubsecao.** O AD-4 segue **condicional**: "maybe with this inversion we even need
this new section". O item 1 acima e o que decide se ela existe.

**AINDA DEVIDO A VOCE, e eu nao pedi antes:** a linha de registro do $\rho$ (que virou **necessaria** quando
voce escolheu treze definicoes) e a nota de escopo do $d$ (o $d$ nao esta livre: $d_{ij}$ e distancia
geodesica no Cap. 3 e $d_{\mathrm{shared}}$ e largura de tronco no Cap. 5). Ambas sao linhas do `GLOSSARY`
§1.1, e a tabela e sua.

**Nenhum `.tex` foi editado.** A sua ordem segue valendo: "depois dessas definicoes podemos aplicado", e o
plano de 8 passos do `_history/_round12/49` continua sem valer enquanto a inversao nao for decidida.

---

### ~~6.21 Rodada 12 — RETRATACAO: a AD-2 nao esta respondida, e eu a fechei sobre um elo que nao verifiquei~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** voce escolheu a opcao 2 (fica em [VERIFY]); encerrada como LO-12.

**Retiro a resposta que dei ao §6.18.** Um revisor achou o defeito e ele e real. A conclusao dependia de dois
arquivos serem o mesmo arquivo, e eu nunca conferi isso.

| o que | onde | nome e formato |
|---|---|---|
| o que o ETL LE | `PoiMtlNet_Novo/src/etl/create_inputs_hgi.py:415` | `{OUTPUT_DIR}/{state}/time_embedding.**parquet**` |
| o que o notebook ESCREVE | `Time_Encoder.ipynb`, celula 15 | `.../{estado}/time_embedding_**novo**.**csv**` |
| o que outras duas linhas do notebook citam | `Time_Encoder.ipynb:1714,:1741` | `.../alabama/time_embedding.**csv**` |

Eu escrevi "which is what the ETL reads" e segui em frente. **Sao tres nomes e dois formatos.**

**E a lacuna e maior do que o nome do arquivo.** Remedido depois do achado: **nada naquele repositorio
escreve o `time_embedding.parquet`** (procurei em todo `.py` sob `PoiMtlNet_Novo/`; a unica ocorrencia e a
leitura na :415), **nao existe conversao csv para parquet** em `src/etl/` nem em `pipelines/`, o arquivo
**nao esta em disco**, e o proprio `CLAUDE.md:91` daquele repositorio descreve este ETL lendo um `.csv`,
discordando do proprio codigo. **Quem produz a tabela que o ETL consome esta fora daquele repositorio, e a
granularidade dela e desconhecida para mim.**

**O que isso derruba, dito por inteiro e nao minimizado.** Se o `time_embedding.parquet` ja for de nivel de
POI, o `drop_duplicates("placeid")` e um dedup inofensivo e **nao existe passo de selecao nenhum**. Cai com
o elo: a moldura da "quarta possibilidade", o "mantem a primeira visita e descarta as outras", e toda a
analise de que o `methodology.tex:93` e o `:153` sao individualmente corretos com um passo perdido entre
eles, que era a base do argumento de lacuna de descricao e de errata.

**O que continua valendo, medido e intacto:** o encoder emite **uma linha por check-in** (celula 13, output
guardado `(2535573, 64)`, contra 2.535.573 check-ins da celula 2, com features hora e dia por check-in na
celula 3); o dedup por `placeid` esta no caminho da tarefa de categoria (`:437`); e o canal temporal esta
naquela entrada (`cat_embeddings` inclui `time`). O ETL portanto **espera** uma tabela que precisa reduzir
por `placeid` — o que e **sugestivo** e nao prova: um dedup defensivo contra uma tabela de POI com linhas
repetidas e igualmente compativel com o codigo.

**O QUE FECHA A AD-2 E UM ARTEFATO SO:** o `data/output/{state}/time_embedding.parquet` da rodada do CoUrb,
ou o que o produziu. Um `len(df)` contra a contagem de POIs e de check-ins daquele estado decide:
`N_checkins` linhas e o passo de selecao e real; `N_pois` linhas e o dedup nao faz nada e a descricao
publicada nao tem lacuna. Marcado como `[VERIFY]` no `_history/_round12/50`.

> **DECISAO SUA — nada precisa mudar no texto, mas voce pode fechar isto se tiver o artefato:**
> 1. **Voce localiza o `time_embedding.parquet` daquela rodada** (ou o notebook/script que o gerou) e eu
>    meco a granularidade. Fecha a AD-2 de vez.
> 2. **Deixar em `[VERIFY]`.** Custo zero para o texto: a sua propria decisao de nao registrar mantem o
>    Cap. 2 na forma neutra, e agora com razao mais forte — nao "existe um passo que escolhemos nao
>    mencionar", e sim "o nivel nao esta estabelecido, entao o capitulo nao afirma nada sobre ele".
>
> **RESPONDIDA — OPCAO 2, FICA EM `[VERIFY]`.** Palavras dele em 2026-08-03: "Vamos de B, e matamos esse
> assunto... eu nao tenho o `time_embedding.parquet`." Encerrada como **LO-12** no `LEFT_OUT.md`, com a razao
> mais forte que o §6.21 ja registra: nao e "existe um passo que escolhemos nao mencionar", e sim "o nivel nao
> esta estabelecido, entao o capitulo nao afirma nada sobre ele". Residuo de formatacao; **nao gaste decisao
> aqui.**

**O erro, nomeado, porque e o segundo da mesma familia neste projeto.** Os dois extremos eram reais e
verificados por mim (a forma `(2535573, 64)` e o dedup na `:437`). Tendo verificado os dois, tratei o
caminho entre eles como verificado tambem. **Uma corrente nao esta verificada quando os elos dela estao.** E
a mesma forma do postmortem fabricado que o `_history/_round9/34` registra: la eu inventei tres mecanismos para
explicar uma falha real, aqui inventei uma ligacao para juntar dois fatos reais. Nas duas vezes as
observacoes eram boas e a **relacao** foi suprida pela expectativa. O teste que faltava era um `grep` pelo
escritor daquele nome de arquivo.

**Nenhum texto do capitulo esta errado**, e um probe que pinava a conclusao retratada (`R12-notwrong`) ficou
vermelho quando eu corrigi o registro — um probe sobre uma conclusao retratada e pior que probe nenhum,
porque briga com a correcao. Substituido por probes sobre a **retratacao** (`R12-retract`, `R12-retract2`,
`R12-verify`).

---

### ~~6.22 Rodada 12 — AD-2 encerrada como `[VERIFY]`, e o `place representation` sai do registro~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** as tres decisoes aplicadas.

**ITEM 1 — AD-2, OPCAO B: FICA EM `[VERIFY]` E O ASSUNTO ESTA ENCERRADO.** "Vamos de B, e matamos esse
assunto... eu nao tenho o `time_embedding.parquet`." Registrado como **LO-12** no `LEFT_OUT.md`, e o Cap. 2
segue na forma neutra ("a vector that is a function of the visited POI"), com "do timestamp da visita" e
"agregado" ainda proibidas. A retratacao do §6.21 e o **estado final** desta decisao, nao uma pendencia.

**E EU NAO RODEI A REGENERACAO, embora voce tenha autorizado** ("se quiser rodar para saber o resultado e
documentar, pode"). A razao e exatamente o defeito que acabei de retratar: regenerar o embedding a partir dos
check-ins mediria o **codigo de hoje**, nao a rodada publicada, e produziria um numero com cara de resposta
para uma pergunta sobre outro objeto. Seria fabricar o mesmo tipo de evidencia que eu retirei, um passo mais
adiante. Alem disso nada naquele repositorio escreve o parquet, entao nao existe pipeline para re-rodar: eu
inventaria um e reportaria o comportamento dele como historia.

**O que eu MEDI, e esta no LO-12 como condicional explicito:** quantas visitas por POI o dedup descartaria
**se** a tabela fosse de nivel de check-in. Dos `checkins_by_state`: Alabama 113.846 check-ins / 11.848 POIs
= 9,61x; Arizona 11,44x; Georgia 13,57x; Florida 18,38x; Texas 4.089.892 / 160.938 = 25,41x. **Isso
quantifica uma hipotese, nao um fato** — e a entrada diz isso com essas palavras. As contagens de check-in
conferem com as que a dissertacao ja publica para Alabama e Texas, o que serve de conferencia cruzada.

**Uma nota de admissibilidade que vale registrar.** A regra do proprio `LEFT_OUT.md` (l. 9-13) exige que o
achado esteja **estabelecido**, e a minha primeira formulacao ("o canal temporal e reduzido a uma visita por
POI") **nao esta** — e a alegacao que retratei. Uma entrada assim importaria a alegacao retratada para o
registro, que e o pior lugar possivel para ela. Entao o **assunto** da LO-12 e a **tensao nao resolvida**
entre o `:93` e o `:153`, que **esta** estabelecida, e nao um passo de selecao. A distincao e o que faz a
entrada passar a propria regra do arquivo.

**Uma pista adjacente que NAO decide, registrada para ninguem promove-la a prova.** O
`apx_b_errata.tex:190-191` diz, recuperado do codigo liberado, "that the sample unit of the category task is
the place, so no place spans two folds". Conferido: e a errata do **Artigo 1** (CBIC), cujo estudo usa o
embedding de grafo e nao o encoder temporal, e "uma linha por place na amostragem" e compativel **tanto** com
o dedup produzindo isso **quanto** com a tabela ja vir POI-level. E a mesma ambiguidade, nao a resolucao
dela.

---

**ITEM 2 — `place representation` SAI DO REGISTRO. SO `place embedding`.** "vamos usar so place embedding
para evitar conflitos e interpretacoes dubias." Feito: a linha e a nota de escopo sairam do `GLOSSARY.md` §6,
e a tabela PT voltou a ser contigua (a linha nova a partia em duas).

**E o probe saiu no MESMO commit.** O `R12-placerep` pinava justamente aquela nota de escopo, entao ficaria
vermelho **por uma decisao sua** — que e o defeito do `R12-notwrong`: um gate brigando com a correcao em vez
de protege-la. Removido, com o motivo no lugar dele. **Nao pus substituto, e vale dizer por que:** banir o
termo da arvore falharia sozinho, porque este arquivo, o `check_audit_claims.py` e os registros da rodada 12
discutem o termo pelo nome ao registrar a decisao, e um probe de ausencia dispararia no **registro da
decisao**. E ao escrever isso eu afirmei que existia um `check_glossary_terms` cuidando disso: **nao existe**.
Os checkers sao os catorze `check_*.py` do `src_utils/`, e so este e o `check_verify_list.py` leem o
`GLOSSARY`. Entao a verdade e que revogar a linha deixa o termo **sem gate**, e isso esta escrito no arquivo
como lacuna conhecida em vez de coberta em outro lugar.

**O TITULO DO AD-4 VOLTOU A FICAR ABERTO, e eu nao vou gastar uma decisao sua nele agora.** Voce deu
"Check-in and place representation"; com o termo fora do registro, a segunda metade deixa de ser admissivel
pela regra fail-closed. Mas o AD-4 e **condicional** de qualquer modo: se a inversao §2.1 <-> §2.2 avancar, a
subsubsecao pode nao existir e o titulo fica irrelevante. Os candidatos, para quando forem necessarios, estao
na linha do AD-4 no `DEFINITIONS.md` §10: (a) "Check-in and place embedding", as duas metades registradas mas
nao a sua redacao; (b) "Place embedding and check-in-level representation", literalmente os titulos das duas
definicoes, mas e a cabeca dupla que a rodada 11 separou de proposito. **Nada foi criado.**

**ITEM 3 — a inversao espera voce.** O estudo do agente esta rodando com escrita limitada a
`_history/_round12/52_inversion_study.md`, apontado para o `fundamentals/` como voce pediu. Nao ha nada seu pendente
nisso ate o relatorio existir.

**CONTINUAM DEVIDAS, e voce nao as tratou nesta rodada:** as duas linhas do `GLOSSARY` §1.1 — a do $\rho$
(que virou **necessaria** quando voce escolheu treze definicoes, porque o $\rho$ passou a ser objeto numerado
do capitulo) e a nota de escopo do $d$ (o $d$ nao esta livre: $d_{ij}$ e distancia geodesica no Cap. 3 e
$d_{\mathrm{shared}}$ e largura de tronco no Cap. 5). Estao no §6.20.

---

### ~~6.23 `make extra` esta VERMELHO, e nao e o documento — e o `sed` do proprio script de build~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** voce escolheu a opcao 2; LC_ALL=C aplicado e o extra passou a rc=0.

**Eu reportei "all four builds rc=0" nos commits `d36da8c5` e `e1fd3619` e isso estava ERRADO.** O
`extra` retorna 2. Descobri porque a ferramenta de shell comecou a devolver saida vazia com rc nao-zero,
me obrigou a rodar tudo por outro caminho, e ai o `extra` apareceu vermelho. **As duas ferramentas
estavam degradadas ao mesmo tempo**, que e exatamente quando um auto-relato vale menos.

**NAO E CULPA DAS MINHAS EDICOES — mas a primeira evidencia que eu dei disso estava ERRADA e um revisor
pegou.** Eu escrevi que o `git diff 1117b3f9..HEAD -- src/` listava "nenhum arquivo". Aquele comando rodou com
o `cwd` na pasta `dissertacao/` e um pathspec comecando por `articles/dissertacao/`, entao ele procurou em
`articles/dissertacao/articles/dissertacao/`, que nao existe. **Um resultado vazio de um caminho inexistente
nao mede nada**, e eu apresentei isso como "medido e nao suposto".

**REMEDIDO da raiz do repositorio, e o numero muda:** os dois commits **tocam sim** um arquivo sob `src/` —
o `src/dissertacao.pdf`, em ambos. **A conclusao sobrevive, por evidencia diferente:** o `dissertacao.pdf` e
uma **saida** de build, copiada pelo `Makefile:36` (`cp build/main.pdf dissertacao.pdf`), e nao entra em
compilacao nenhuma; e **nenhum `.tex` foi alterado pelos dois commits** — a lista completa e
`DEFINITIONS.md`, `dissertacao.pdf`, `LEFT_OUT.md`, `PENDENCIAS.md`, `_history/_round12/50`, `_history/_round9/34` e
`check_audit_claims.py`. Nada que o `main_extra` inclua.

**A CAUSA, passo a passo:**
1. `make extra` -> rc=2, **mas o PDF sai**: 26 paginas, 0 erros de TeX.
2. `pdflatex` sozinho -> rc=0. `bibtex` sozinho -> rc=0.
3. `bash -x` no `latexbuild.sh`: o script chega em `PAGES=$(sed ...)` e o **`PAGES` sai vazio**, entao
   entra no ramo "NO PAGE COUNT ... the build did not finish" e sai com erro.
4. Mas o log **tem** a linha: `Output written on ... (26 pages, 200259 bytes).`, uma ocorrencia.
5. Rodando o mesmo `sed` na mao: **`sed: RE error: illegal byte sequence`**. Com `LC_ALL=C` ele imprime
   `26` normalmente.
6. O log **nao e UTF-8 valido**: o byte 61294 e um `\xea` Latin-1 dentro da hifenizacao de
   "In-te-li-g\xean-cia Com-pu-ta-ci-o-nal", de uma entrada da bibliografia do CBIC que so aparece no
   apendice do `extra`.

Ou seja: o TeX escreve no log uma palavra portuguesa hifenizada com um byte Latin-1, e o **`sed` do BSD
(macOS) recusa o arquivo inteiro num locale UTF-8** — o GNU `sed` nao faria isso. O build **funcionou**;
o que falhou foi a extracao da contagem de paginas, e o script honestamente reporta a propria falha.

**O `extra` e o unico alvo cujo log carrega esse byte**, que e por que os outros tres passam.

> **DECISAO SUA — a correcao e de uma linha, mas o arquivo e compartilhado:**
> 1. **`LC_ALL=C` na linha do `PAGES`** (`src_utils/latexbuild.sh:49`). E o minimo, resolve a causa, e o
>    `LC_ALL=C` e a forma padrao de dizer "trate como bytes". Risco: nenhum que eu veja; a regex e ASCII.
> 2. **`LC_ALL=C` na linha do `PAGES` e tambem no `grep` do `ERRS`** (linhas 49-50), por simetria. **Eu
>    levantei a suspeita de que o `grep` estivesse silenciosamente devolvendo 0 e FUI CONFERIR: nao esta.**
>    O `grep -c '^! '` devolve `0` tanto no locale UTF-8 quanto sob `LC_ALL=C` naquele mesmo log, entao a
>    contagem `tex_errors=0` do `extra` e verdadeira. Esta opcao e higiene, nao correcao de defeito.
> 3. **Nao mexer** e aceitar o `extra` vermelho ate a proxima rodada.
>
> **RESPONDIDA — OPCAO 2, APLICADA.** §6.25: `LC_ALL=C` nas duas linhas do `latexbuild.sh`, e o `extra` passou
> a rc=0. O comentario no script diz o que ele pediu que dissesse: a `:PAGES` e **correcao de defeito real** e a
> `:ERRS` e **higiene e simetria**, nao conserto de bug — porque a medicao mostrou que aquele `grep` devolve 0
> nos dois locales. Residuo de formatacao; **nao gaste decisao aqui.**

**Por que eu nao apliquei sozinho:** o `latexbuild.sh` e compartilhado com o agente paralelo, o cabecalho
dele documenta tres propriedades que foram aprendidas quebrando o arquivo, e a opcao 2 muda o
comportamento de uma checagem de erros. Isso e chamada sua, nao limpeza de fim de rodada minha.

**Uma suspeita que eu levantei e depois DERRUBEI com um comando, em vez de deixar no ar:** achei que o
`grep -c '^! '` pudesse estar falhando pelo mesmo byte e devolvendo `0` sem significado. Testei nos dois
locales contra aquele log e ele devolve `0` nos dois. Entao o `tex_errors=0` do `extra` vale, e o unico
defeito real e a contagem de paginas.

---

### ~~6.24 A comparacao das duas opcoes — o estudo novo RECOMENDA MANTER A ORDEM, ao contrario do `_history/_round12/52`~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** voce decidiu MANTER A ORDEM (opcao (a)); a inversao esta encerrada e o redesenho aplicado.

O relatorio esta em `_history/_round12/53_order_comparison.md`. **Nada foi decidido nem editado**, e a sua suspensao da
inversao continua valendo.

**A RECOMENDACAO: OPCAO (a) — MANTER `2.1` tarefas, `2.2` representacoes**, e aplicar o redesenho pelo plano do
`_history/_round12/49`. E o oposto do que o `52` recomendou, com praticamente a mesma base de evidencia; a divergencia
esta no criterio que **voce** definiu.

**COMO ELE RESOLVEU O ARGUMENTO DO ESPELHO, que era a sua preocupacao.** Os dois espelhos sao fieis a tese: o
tasks-first espelha o **DESENHO** do argumento (fixe a referencia, varie a alavanca) e o representations-first
espelha a **RESPOSTA** (a alavanca e que importava). O desempate dele nao e a tese, e o **leitor**, com dois
argumentos:
1. **O espelho-da-resposta so paga a quem ja tem a resposta.** A elegancia de "representacoes primeiro, porque
   as representacoes dominaram" e legivel para quem relê ou para voce, que conhece o arco. Um membro de banca
   em primeira leitura ainda nao tem a tese como conviccao; para esse leitor as tarefas sao o enquadramento que
   torna cada definicao posterior inteligivel. **O espelho-do-desenho e andaime para a primeira leitura; o
   espelho-da-resposta e recompensa para a segunda** — e a regra G3 do proprio projeto faz da primeira leitura
   a que governa.
2. **A invariante e o que os tres artigos compartilham, e o Cap. 2 e onde o leitor adquire o quadro
   compartilhado.** O que e constante nos tres e a definicao das tarefas; o que varia e o $\rho$. Um capitulo de
   fundamentos ordenado invariante-primeiro entrega o quadro fixo uma vez e deixa cada capitulo de artigo variar
   a alavanca contra ele.

**E ELE DESMONTOU O ROTULO "ja esta validada" — que era meu, e estava frouxo.** Eu conferi separadamente e
confirmo: **o rotulo e do `52`, nao do `49`.** Um `grep` por "validated" no `49` da **zero** ocorrencias dessa
alegacao. O que o `49` tem e uma **validacao adversarial (Parte A)** das propriedades internas do desenho —
ordem de dependencia, boa formacao, colisoes de notacao, sobrevivencia de probes — e isso e diferente de dizer
que a **opcao** esta validada. O estudo aponta tres qualificadores, e o primeiro e o que importa: **o AD-4, que
e o sign-off na forma da §2.1 e no titulo da subsubsecao, esta ABERTO.** Nas palavras dele, a opcao esta
"mechanically checked and narratively unsigned" — o **AD-4 e o custo narrativo da opcao (a) em forma de
decisao**.

**CINCO PONTOS EM QUE ELE DISCORDA DO `52`**, e eu destaco os dois que me parecem mais fortes:
- **O `52` resolveu o espelho por deferencia, nao por argumento.** Ele concedeu que a escolha era autoral e
  entao a resolveu com "o julgamento do autor ja se inclina para o espelho-da-resposta". **A sua suspensao
  provou essa leitura errada**, e tratar um entusiasmo inicial como veredicto e exatamente o padrao de
  sycophancy que o `AGENT_GUARDRAILS` §7 nomeia.
- **O `52` precificou so um lado.** Mediu a (b) meticulosamente e cotou a (a) como zero, "o fallback". Os
  custos narrativos da (a) nao aparecem lá, e nem as economias dela (nenhuma edicao do mapa, nenhuma ponte
  nova, nenhum rastreador reancorado, nenhum toque na introducao). **Uma comparacao nao se ganha medindo um
  competidor.**
- E o achado historico negativo do `52` **dissolve so o argumento de tradicao**, que ninguem precisava fazer.
  As razoes de presente para tasks-first (a forma dos artigos, o trabalho do leitor, o gate de primeira
  leitura) nao dependem de intencao registrada.

**AS CONDICOES QUE ELE POE NA OPCAO (a)**, e a primeira e desenhada para o seu proprio criterio: **KC-1 — o
AD-4 e resolvido PRIMEIRO**, com voce vendo a forma redigida da §2.1 e nomeando a cabeca. **Se voce rejeitar a
forma ao ler, essa rejeicao e o sinal para reabrir a (b)**, porque o AD-4 e o custo narrativo da (a) tornado
visivel. Depois: uma frase de abertura ligando as representacoes aos alvos; o ajuste da frase de escopo em
`:27-28` no mesmo commit; e as coordenadas rederivadas contra a arvore viva na aplicacao.

**O QUE EU CONFERI, porque auto-relato nao e evidencia:**
- **Coordenadas:** o `GLOSSARY.md:45` (linha do $\rho$), o `DEFINITIONS.md:590` (linha do AD-4), o `:576`, o
  `PENDENCIAS.md:1484`, e o `2_fundamentals.tex:27`, `:68`, `:76` — **todas leem como ele diz**.
- **A contagem de definicoes:** rodei o `grep` dele e as **doze** definicoes estao exatamente nas linhas que
  ele lista, o `wc -l` da **1527** como ele diz (o meu 1528 anterior era erro meu, de contar uma quebra final),
  e as tres ocorrencias de "rho" sao mesmo substrings de "neighborhood"/"node2vec".
- **Ele releu a arvore DEPOIS do meu commit do §6.25:** cota as linhas do `GLOSSARY` como "already paid", o que
  esta certo — elas servem as duas opcoes.
- **Duas derivas pequenas, e as duas sao MINHAS, nao erros dele:** o "ja esta validada" que ele cita no
  `PENDENCIAS:1633` esta hoje na `:1663` (o meu §6.25 empurrou), e o `wc` mudou pelo mesmo motivo.
- **Um numero dele esta desatualizado por minha causa:** ele fala de **21** probes no capitulo; hoje sao **22**,
  porque eu adicionei o `R12-placeterm` nesta rodada. **A alegacao de fundo continua verdadeira, e eu a testei
  em vez de aceitar:** nenhum dos 22 casa com prosa que enuncia a ordem, entao **nenhum probe restringe a
  ordem das secoes**.
- **Wall-clock — CORRIGIDO, e eu tinha escrito o oposto do verdadeiro.** Eu publiquei "2.236 s, 7 por cento
  DENTRO, o primeiro estudo a fechar no prazo". **Os 2.236 s nao sao medicao do estudo: e o instante em que a
  MINHA janela de coleta fechou**, com o relatorio dele ainda em `running` e todos os campos vazios. Li um
  timeout como um termino. **O que esta medido, e a minha propria correcao anterior AINDA
  ESTAVA BAIXA: a vida do processo filho foi de 4.185 s, ou seja 74 por cento ACIMA do checkpoint de 2.400 s**
  (`created_at` 1785790156537, `updated_at` 1785794341322, da tabela `frames`). Eu havia escrito "3.201 s, 33
  por cento", que era so a idade dele no instante em que eu olhei — **outra leitura de instrumento tomada por
  medicao do processo**. E ele **terminou por conta propria**: o registro diz `completed`, entao o meu
  `stop_child` chegou depois de ele ja ter fechado, e nao interrompeu trabalho. **Ele estourou, como todas as ondas deste
  projeto.** Duas coisas atenuam e nenhuma apaga: o arquivo entregue ja estava **completo em disco** quando eu
  o li (34.525 bytes, todas as secoes), entao o excesso foi depois da escrita e nao trabalho perdido; e o
  auto-relato dele (~1.787 s) esta **subestimado em pelo menos 1.414 s** contra o momento em que eu o parei —
  que e exatamente por que ele mesmo disse que a minha medicao governa, e por que auto-relato de prazo nao
  vale neste projeto.

> **DECISAO SUA — e as duas opcoes estao agora precificadas dos dois lados:**
> 1. **Opcao (a), manter a ordem**, com o KC-1 primeiro: voce le a forma redigida da §2.1 e nomeia a cabeca,
>    e uma rejeicao sua ali reabre a (b). E a recomendacao do estudo novo.
> 2. **Opcao (b), inverter**, com as cinco condicoes do `52`. Se voce escolher esta, **duas perguntas suas
>    voltam**: a ordem da sintese da §2.5 e a edicao do `NORTH_STAR.md:73-80`.
> 3. **Ler os dois relatorios antes de decidir** — o `52` defende a (b), o `53` defende a (a), e eles
>    discordam por escrito e nao por omissao.
>
> **DECIDIDO POR ELE EM 2026-08-03: OPCAO 1 — MANTER A ORDEM.** Palavras dele: "DECIDI: MANTER A ORDEM.
> Opcao (a) do _history/_round12/53 — 2.1 tarefas, 2.2 representacoes. A inversao esta encerrada, nao suspensa."
> **A inversao esta ENCERRADA**, e com ela saem da fila duas perguntas que so existiam sob ela: a ordem da
> sintese da §2.5 e a edicao do `NORTH_STAR.md:73-80`. O `NORTH_STAR` fica **intacto**.

**O REDESENHO FOI APLICADO AO CAPITULO NESTA RODADA.** Ele autorizou junto com a decisao, e o KC-1 foi
satisfeito da forma que ele mesmo definiu: **o titulo da subsubsecao e escolha dele**, dada explicitamente
("Check-in and place embedding"), e eu **nao a inferi de nenhuma frase anterior**. O que entrou, dos sete
passos vivos do `_history/_round12/49` Parte B:

| Passo | O que mudou no `2_fundamentals.tex` | Probe |
|---|---|---|
| 1 | A prosa de notacao passa a **vincular** o $c_p$ e o $r_p$ | `R12-s1bind` |
| 2 | A D1 passa a **tipar** $c_i=c_{p_i}$ e $r_i=r_{p_i}$ | `R12-s2type` |
| 3 | Nova subsubsecao **"Check-in and place embedding"** na §2.1, com as duas definicoes movidas verbatim, a D5 (mapa de representacao) como **definicao numerada**, e o comentario de fatoracao corrigido (F-1/F-2/F-3) | `R12-s3head`, `R12-s3map`, `R12-s3scope` |
| 4 | As duas definicoes **saem** da §2.2; a prosa que as usa fica, agora com referencias para tras | `R12-s4moved` |
| 5 | A §2.2 passa a dizer a forma **neutra** da entrada do Cap. 4 (AD-2 opcao 2) | `R12-s5neutral` |
| 6 | **Ja estava feito** nesta rodada (as linhas do `GLOSSARY` §1.1) | `R12-dscope`, `R12-rho` |
| 8 | Varredura de referencias cruzadas e gates | (abaixo) |

**CONFERIDO NO PDF RENDERIZADO e nao no fonte**, que e a sua regra: a pagina 19 do build de defesa mostra a
subsubsecao, e as definicoes renumeraram sozinhas na ordem certa — **2.3 Place embedding, 2.4
Check-in-level representation, 2.5 Representation map**, todas ANTES das tarefas (2.6 a 2.9). A frase pinada
da 2.4 esta la **caractere por caractere**. Zero rotulos multiplamente definidos, zero erros de TeX, zero
referencias `def:fund:` fora do capitulo, zero "Definition 2.N" literal em prosa viva. **O capitulo cresceu
uma pagina** (104 -> 105 defesa, 101 -> 102 academico, 105 -> 106 ppgc) e as contagens registradas foram
sincronizadas.

**DOIS DEFEITOS QUE APARECERAM NO CAMINHO, os dois meus:**
1. **O gate de registro deu falso positivo em `elementwise`.** A palavra entra com o passo 3 e o
   `check_register.py` a leu como grafia britanica em `-ise`, deixando o `make check` vermelho sobre prosa
   americana correta. **Nao e o mesmo que a familia `-ise`**: o sufixo `-wise` significa "a maneira de" e
   nao tem relacao etimologica com o par `-ise`/`-ize`. Corrigido **por regra e nao por lista** — o proprio
   cabecalho daquele modulo avisa que uma lista escrita a mao so pega as palavras que o autor pensou, e o
   `wise`, o `likewise` e o `otherwise` estavam listados um a um, enquanto `pairwise` e qualquer outro
   composto teriam falhado igual. Conferido que nenhuma grafia britanica real deixou de ser pega. Probe
   `R12-wise`.
2. **Eu escrevi "(measured: ...)" num comentario sem ter medido.** Um revisor pegou: a celula do `grep`
   havia falhado com saida vazia e eu escrevi a alegacao de todo modo. **Medido agora, e o resultado e mais
   forte do que o que eu tinha alegado:** o `c_p\in\mathcal{C}` e o `r_p\in\mathcal{R}` tinham **zero**
   ocorrencias vivas na arvore, mas o `c_p` **cru** ja aparecia uma vez, no `:119` — e ali ele e
   **consumido** pela equacao do classificador estatico. O simbolo estava **em uso e sem definicao**, que e
   um defeito mais nitido do que "o simbolo nao existia". O comentario agora diz isso.

> **NADA ESPERA VOCE NESTE ITEM.** A decisao esta tomada e aplicada. O que continua seu esta no §6.26.

---

### ~~6.25 O `extra` esta VERDE, e as duas linhas do `GLOSSARY` §1.1 entraram~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** registro do que foi feito; nada dependia de voce.

**ITEM 1 — `LC_ALL=C` nas duas linhas, opcao 2. FEITO, e o `extra` passou a rc=0.** Os quatro alvos agora
saem `104/101/105/26` paginas com `tex_errors=0` em todos, e o `make check` e o `make selftest` em rc=0 —
**seis comandos verdes, lidos um por um**. Era a primeira vez nesta rodada que o `extra` fechava.

**O comentario diz exatamente o que voce pediu, e diz a diferenca entre as duas linhas:**
- a `:PAGES` **e correcao de defeito real** — o `sed` do BSD abortava o arquivo inteiro por causa do byte
  Latin-1 na hifenizacao de "In-te-li-g^en-cia Com-pu-ta-ci-o-nal", entao o `PAGES` saia vazio e o script
  reportava "the build did not finish" sobre um build que tinha produzido um PDF correto de 26 paginas;
- a `:ERRS` **e higiene e simetria, NAO conserto de bug**, e o comentario registra a medicao que estabelece
  isso: o `grep -c '^! '` devolve `0` **nos dois locales** naquele log, entao o `tex_errors=0` do `extra`
  **e verdadeiro**. Esta escrito no arquivo com essas palavras para ninguem depois ler a `:ERRS` como reparo
  de um defeito que nunca existiu.

Dois probes guardam a distincao (`R12-locale`, `R12-locale2`), porque confundir as duas linhas e exatamente
o que voce pediu para evitar. Reli o arquivo do disco imediatamente antes de editar e usei caminhos
explicitos no commit.

---

**ITEM 2 — as duas linhas do `GLOSSARY` §1.1: ENTRARAM.**

A do **$\rho$** registra o mapa de representacao e, no campo de notas, a razao pela qual ele importa: os
modelos das tarefas **sequenciais** leem $\rho(H_i)$ e nao o $H_i$, a tarefa estatica le $\mathbf{e}_p$
direto, e **os tres estudos mantem as definicoes de tarefa fixas e variam o $\rho$** — que e o que torna a
alegacao central do trabalho enunciavel.

A do **$d$** entrou **com a nota de escopo**, e aqui **corrigi um detalhe da sua propria nota**: voce escreveu
que o $d_{\mathrm{shared}}$ e largura de tronco **no Cap. 5**. **Medido: ele nao aparece no Cap. 5.** As tres
ocorrencias vivas estao nos **Caps. 3 e 4** (`3_cbic/method.tex:78`, `4_courb/methodology.tex:25` e `:258`,
com $256$ onde o valor e dado). O $d_{ij}$ (distancia geodesica no peso da aresta de Delaunay,
`3_cbic/method.tex:23`) tem quatro ocorrencias, tambem nos Caps. 3 e 4. A linha registra os capitulos
**medidos**, nao os da nota, e diz que nenhum dos dois subscritos e instancia da linha nova.

---

**ITEM 3 — a inversao: o estudo comparativo esta rodando, e eu NAO toquei em nenhum `.tex` de ordem.** A sua
suspensao esta respeitada: nada de inverter, nada de editar o `NORTH_STAR.md:73-80`, e o plano de oito passos
do `_history/_round12/49` continua parado. O resultado vai para o **§6.24**, como voce pediu.

**E uma coisa que eu conferi antes de comecar, porque a sua nota dizia o contrario:** os tres itens que voce
listou como "no disco, sem commit" (a correcao do primeiro `[VERIFY]` do `_history/_round12/52`, a nota de wall-clock, e
o probe `R12-studyfix`) **ja estavam commitados**, no `5446ffb3`. A arvore estava limpa. **Mas o seu ponto sobre
o `R12-studyfix` estava certo e importava:** aquele probe nunca havia disparado, porque a frase-alvo quebra
linha no fonte e a minha perna procurou a forma sem quebra. **Validei agora contra a forma envolvida**, testando
o padrao atraves do `strip_text` como voce disse: ele dispara quando a frase de correcao sai, e fica silencioso
sob uma edicao vizinha nao relacionada. Agora carrega informacao.

---

### ~~6.26 Os dois itens que voce mandou MEDIR: um esta fechado ha uma rodada, o outro espera a sua mao~~ — RESOLVIDO 2026-08-03

**Motivo da saida:** as duas metades fecharam. A primeira (as duas linhas do `GLOSSARY` §1.1) foi aplicada
por mim sob a autorizacao explicita dele de 2026-08-03, com o comentario do `2_fundamentals.tex` corrigido no
mesmo commit; a segunda (a renomeacao dos indices da D13, AD-7) **nao se perde ao sair daqui**, porque ela
esta integralmente registrada no `fundamentals/DEFINITIONS.md` — a D13 ja aparece la com
$\mathbf{g}_a$, $\mathbf{g}_b$ e $\varphi_{ab}$, e com o paragrafo que explica por que $a$ e $b$ em vez de
$i$ e $j$. Era o unico motivo de este bloco continuar vivo, e o desenho e o lugar certo dele: a renomeacao
entra no capitulo quando a D13 for tocada.

**Voce pediu medicao antes de tratar como aberto ou fechado, e os dois resultados sao diferentes.**

**BLQ-1 — o "hard sharing" no Apendice F: JA ESTA FECHADO, na rodada 9.** A clausula foi **deletada** e o
registro da delecao esta no proprio arquivo (`apx_f_cosine.tex:458-470`). Ela dizia "That is why hard sharing
costs nothing in this architecture, and why Chapter 5 finds no balancer improving on a fixed loss weighting".
**As quatro ocorrencias de "hard sharing" que ainda aparecem naquele arquivo sao COMENTARIOS**, e eu conferi
uma por uma: as `:124`, `:458`, `:462` e `:467` todas comecam com `%`. Nenhuma e prosa viva.

E a medicao que sustentou a delecao continua valendo: o Cap. 5 descreve a topologia como **cross-attention**
com caminho espacial privado (`5_mobiwac/04_method.tex:27-31`, prosa viva: "Both pass through private
per-task encoders (a small input network per task, with no shared weights) into the shared trunk, a
cross-attention stack of two blocks" e "the region output also keeps a private spatial path"), enquanto o
Cap. 2 define hard parameter sharing como um tronco comum que se divide nas cabecas de saida. **Sao
opostos**, exatamente como voce disse. O Apendice F hoje descreve a topologia certa: fala de
"cross-attention trunk" em prosa viva (`:150`, `:476`, `:573`).

> **NADA ESPERA VOCE AQUI.** O item esta fechado e este paragrafo e o registro da medicao.

---

**AS DUAS LINHAS DO §6.13 — NAO ESTAO NO `GLOSSARY`, e a sua mao e que as escreve.** Medido: nem o
$\mathbf{e}_{x_i}$ nem o $f_{\mathrm{place}}(H_i)$ aparecem na tabela §1.1. E os dois **estao em uso vivo no
capitulo**: o $\mathbf{e}_{x_i}$ na Definicao 2.4 e o $f_{\mathrm{place}}(H_i)$ na Definicao 2.9. Pela regra
fail-closed do registro, sao dois simbolos usados e nao registrados.

**Eu as escrevi e depois as REVERTI, no meio desta rodada.** O motivo esta no proprio capitulo: o comentario
que eu mesmo carreguei junto com a Definicao 2.4 diz, verbatim, "A registry row for $\mathbf{e}_{x_i}$ is
PROPOSED to the author and is not written by an agent; the notation table is his". Voce autorizou as duas no
§6.20 (a AD-5 fechou), mas voce tambem mandou, nesta rodada, **medir e nao aplicar**. Entao elas ficam aqui,
prontas, e nao no arquivo.

**As duas linhas, para voce colar na §1.1 se aprovar a redacao:**

```
| $\mathbf{e}_{x_i}$ | The learned representation of check-in $x_i$. | The check-in-level counterpart of $\mathbf{e}_p$: same shape, and the subscript is the point, since it indexes a visit rather than a place. Two visits to one POI may carry different vectors. |
| $f_{\mathrm{place}}(H_i)$ | Next-place prediction: maps a check-in history to the next visited POI. | Registered so the excluded task is formally distinct rather than the only one described in prose. **This dissertation does not predict next place;** the row names what is out of scope. |
```

> **DECISAO SUA:**
> 1. **Colar as duas como estao.** Fecha a lacuna fail-closed dos dois simbolos.
> 2. **Colar com a sua redacao.** Diga a redacao e eu aplico.
> 3. **Eu aplico as duas**, se voce preferir abrir excecao a regra de que a tabela e sua. Nesse caso diga,
>    porque o comentario do capitulo afirma o contrario e eu teria de corrigi-lo no mesmo commit.
>
> **RESPONDIDA — OPCAO 3: ele mandou que EU colasse.** Palavras dele em 2026-08-03: "Sobre a pendencia do
> glossary, eu autorizo voce a colar elas no glossary." Feito neste commit, com a consequencia que a propria
> opcao 3 previa: o comentario do `2_fundamentals.tex` que dizia que a tabela e escrita pelo autor e nao por um
> agente foi corrigido no **mesmo commit**, citando a frase antiga como superada em vez de apaga-la. A regra
> geral continua valendo — a tabela e dele e um agente propoe linhas; esta foi uma excecao autorizada.

---

**AINDA SEU, e nao e desta lista:** a renomeacao dos indices da D13 (AD-7, respondida, opcao 1) esta
registrada no desenho e **entra no capitulo quando a D13 for tocada** — ela nao entrou nesta rodada porque
nada mais na D13 mudou e editar so os indices dessincronizaria o desenho do capitulo por meia rodada.

---

---

## A SECAO §6 DO `PENDENCIAS.md` FOI ENCERRADA E REMOVIDA — 2026-08-03

O cabecalho dela era, verbatim:

> `## §6 · As decisoes que sairam do `CONSIDERATIONS.md` (round 9)`

Ela entrou em 2026-07-30 substituindo o §2.8 e carregou vinte e seis itens. **Todos os vinte e seis foram
respondidos por ele e estao arquivados acima**, cada um com o motivo da saida no topo do bloco. Com o §6.26
fechado, a secao deixou de pedir qualquer coisa, e a pedido dele a `h3` e o proprio cabecalho `## §6` sairam
do arquivo vivo — a mesma trajetoria do §2.8, que deixou de ser um pedido de decisao e virou registro.

**A numeracao 6.1 a 6.26 nao foi reaproveitada nem reordenada.** Comentarios no fonte citam estes numeros, e
as dezenove citacoes que apontavam para o `PENDENCIAS.md` §6 foram repontadas para este arquivo na forma
`PENDENCIAS_RESOLVIDOS <n>.<m> (arquivado 2026-08-03)`, que e a forma que o `check_tracker_refs.py` reconhece
como historica. O gate ficou verde depois disso, e antes de apagar cada bloco eu confeti que ele havia
CHEGADO aqui, cabecalho **e** corpo: tres itens desta lista se perderam no passado exatamente por apagar
antes de conferir.

---

### ~~§5 · Retirado~~ — SECAO REMOVIDA 2026-08-03

**A secao ponteiro em si foi removida do `PENDENCIAS.md` em 2026-08-03**, a pedido do autor, depois de
reconfirmar que os onze itens que ela apontava (5.1 a 5.10 mais o 5.6b, todos abaixo) continuam
fechados. Re-medido nesta data: as cinco frases-teste do CODEX_AUDIT ainda reproduzem o resultado
original (quatro vazias, a quinta so em `tables/cbic/errata_wording.tex` como evidencia citada); os
treze probes `COD-`/`NUM-`/`R8-` do `check_audit_claims.py` seguem em `rc=0`; as duas datas do Gowalla
(2009-2011) conferem no `main.pdf` recompilado (105 pp, zero erros). Tres citacoes vivas que ainda
apontavam para `PENDENCIAS.md §5.x` foram repontadas para este arquivo:
`chapters/apx_c_ai_disclosure.tex`, `src_utils/codex_reviewer.md`, `src_utils/LEFT_OUT.md`.

O texto da secao removida, verbatim:

> ## §5 · Retirado
>
> Os onze itens levantados do `CODEX_AUDIT.md` quando ele foi arquivado (5.1 a 5.10 mais o 5.6b) estao
> **todos fechados** e vivem em [`_history/_archive/PENDENCIAS_RESOLVIDOS.md`](PENDENCIAS_RESOLVIDOS.md),
> cada um com a medicao que o fechou e a sua decisao verbatim. O `CODEX_AUDIT.md` inteiro esta em
> [`_history/_archive/CODEX_AUDIT.md`](CODEX_AUDIT.md).
>
> Re-medido em 2026-08-02, depois da fusao da sua arvore revisada, porque um arquivo fechado nao e um
> arquivo que continua verdadeiro. As conclusoes sobreviveram: o comando que o banner desta secao
> documentava ainda reproduz o que ele afirmava -- quatro das cinco frases retiradas vem vazias e a
> quinta aparece so em `tables/cbic/errata_wording.tex`, que e a tabela de errata, onde a redacao
> antiga esta como evidencia citada e nao como alegacao viva. Os treze probes `COD-`/`NUM-`/`R8-` do
> `check_audit_claims.py` seguem em `rc=0`, e o 5.6 (as duas datas do Gowalla) confere no render.
>
> Sete dos itens tem sonda no gate, que falha se a correcao sair do documento; dois nao tem, e a razao
> esta no banner do arquivo: o 5.6 foi verificado direto no render e o 5.10 e um registro de
> nao-pendencias, nao uma afirmacao do documento. O decimo (COD-018, credito por papel no CoUrb) foi
> retirado por voce, e o gate carrega a sua frase para que ninguem o "termine" por engano.

Os onze itens individuais (5.1-5.10, 5.6b) ja estavam arquivados abaixo antes desta remocao; nada
deles mudou aqui.

---

## §4 (os itens `AUT-`) — 26 DE 37 FECHADOS E REMOVIDOS DO `PENDENCIAS.md` — 2026-08-04

> **Rodada 13.** Voce leu os 37 pontos que havia escrito em `## §4 · Pensamentos e consideracoes do
> Autor`, respondeu 21 deles em `§4.1` com `> DECISSAO:`, e os 15 `[YOU APPLY]` vinham do plano de
> `§4.2`. Este bloco arquiva os **26 itens fechados**, cada um com o commit em que foi aplicado. Os
> **11 restantes continuam no `PENDENCIAS.md` §4**, e a razao de cada um esta listada no fim.
>
> **OITO itens fecharam SEM EDICAO ALGUMA, e isso e um resultado e nao uma omissao.** A frase aqui dizia
> "Quatro" e listava cinco IDs, enquanto a tabela abaixo marca oito linhas "(sem edicao)" -- corrigido em
> 2026-08-04, depois de um reviewer contar as linhas. Os oito sao AUT-06, AUT-11, AUT-13, AUT-15, AUT-17,
> AUT-28, AUT-33 e AUT-34, e eles fecham por duas razoes diferentes, o que e a distincao que a frase
> original tentava fazer e errou na conta. **Cinco por medicao:** AUT-06, AUT-13,
> AUT-15, AUT-17 e AUT-33 foram medidos contra o fonte vivo e ja estavam satisfeitos: a redacao que
> voce criticou tinha sido substituida por outra esteira antes de voce escrever, ou a clausula que
> faltava ja estava la. Em cada caso a citacao que prova esta no bloco. Outros tres (AUT-11, AUT-28,
> AUT-34) fecharam sem edicao porque **voce decidiu manter o texto como esta**.
>
> **Tres itens correcao de honestidade.** AUT-20 e AUT-23 corrigem uma afirmacao FALSA sobre o nosso
> proprio sistema: o Cap.2 dizia que as representacoes treinam "without category or region labels", e
> a categoria da visita atual **e** feature de entrada do no de check-in, alem de haver um termo de
> reconstrucao de categoria com peso 0.3 na configuracao que o estudo final treina. Trocado por uma
> afirmacao de **escopo**, que e mais estreita e verdadeira. AUT-03 restaura o hifen dentro de tres
> citacoes textuais que uma varredura da casa havia alterado, uma delas o titulo publicado do seu
> proprio artigo, impresso de dois jeitos no mesmo PDF.
>
> **Duas das suas premissas foram refutadas por medicao**, e as duas estao registradas no fonte para
> nao serem re-derivadas: o rotulo de regiao **nao** e feature do no, e latitude e longitude **nao**
> sao features do no (entram so na construcao do grafo, pela juncao poligonal). E a validacao que voce
> pediu sobre o Massive-STEPS voltou **REFUTADA**, o que mantem o AUT-35 aberto.
>
> **Todos os itens aplicados tem sonda no gate**, adicionada no mesmo commit da correcao e validada por
> sabotagem individual: `check_audit_claims.py` sai `rc=0` com **167 de 167 probes**. Uma sonda que eu
> escrevi foi **retirada** por ser inspecionavel: ela mirava texto dentro de um comentario `%`, que o
> gate remove por projeto, e esta em `NOT_CHECKABLE` **pelo nome**, com o comando de re-medicao.

| item | ruling | commit | o que ficou feito |
|---|---|---|---|
| **AUT-03** | A | `e92dfdcf` | tres citacoes textuais restauradas: o titulo publicado do CBIC, o titulo submetido do MobiWac, e a linha da tabela de errata. As tres contra a sua fonte de registro, aberta nesta sessao. |
| **AUT-04** | [YOU APPLY] | `6633e936` | a oracao das categorias semanticas agora conduz as duas tarefas em vez de pender do fim da frase anterior. |
| **AUT-05** | [YOU APPLY] | `6633e936` | as duas frases de "neighboring geospatial tasks" sairam do §1.1; o termo nunca era definido. |
| **AUT-06** | [YOU APPLY] (sem edicao) | `6633e936` | fechado como JA SATISFEITO: as duas tarefas sao nomeadas na mesma frase que diz "both tasks". |
| **AUT-07** | [YOU APPLY] | `6633e936` | `static place categories` -> `category classification`, o nome registrado no GLOSSARY §1. |
| **AUT-10** | [YOU APPLY] | `6633e936` | `hard parameter sharing` glosado no primeiro uso do Cap.1. |
| **AUT-11** | A (sem edicao) | `--` | voce manteve o objetivo 1 como esta. Nada aplicado, por decisao sua. |
| **AUT-12** | A | `e92dfdcf` | objetivo 4: `ch:conclusion` -> `ch:mobiwac`. Um token, invisivel a todos os gates porque o `\ref` errado RESOLVIA. |
| **AUT-13** | [YOU APPLY] (sem edicao) | `6633e936` | fechado como JA SATISFEITO por outra esteira: "the joint setting" virou "The joint model operates under...". |
| **AUT-15** | [YOU APPLY] (sem edicao) | `6633e936` | fechado como JA SATISFEITO: a frase viva ja carrega a clausula de escopo "at a coarse spatial resolution". |
| **AUT-16** | [YOU APPLY] | `6633e936` | `sequential` e `static` glosados no primeiro uso do Cap.1. |
| **AUT-17** | [YOU APPLY] (sem edicao) | `6633e936` | fechado como JA SATISFEITO pela rodada 12: os cinco simbolos estao ligados nas duas definicoes numeradas. |
| **AUT-18** | generico | `54cb689d` | os nomes das unidades sairam da definicao da tarefa e entraram na descricao dos dados. |
| **AUT-19** | [YOU APPLY] | `6633e936` | uma frase de entrada em §2.2.2 dizendo o que infomax E antes do que ele maximiza. |
| **AUT-20** | A | `4ee3265a` | a afirmacao de ausencia virou afirmacao de escopo. Cap.2 fica SILENCIOSO sobre o canal do grafo, por sua decisao. |
| **AUT-21** | i | `4ee3265a` | o mecanismo da tabela pre-treinada e NOMEADO, sem citacao nova. Citar o POI2Vec publicado seria misatribuicao. |
| **AUT-22** | [YOU APPLY] via GER-06 | `6633e936` | a frase do FiLM saiu de §2.2.3.1 e entrou em §2.3.1, ao lado da definicao de hard sharing. |
| **AUT-23** | passagem unica | `4ee3265a` | as tres afirmacoes de §2.2.3.2 corrigidas junto com AUT-20 e AUT-21, como voce pediu. |
| **AUT-24** | [YOU APPLY] | `6633e936` | a abertura de §2.2.4 nomeia o sujeito em vez de usar substantivo abstrato como agente. |
| **AUT-25** | hedge | `(pendente commit)` | o contraste das duas entradas entrou hedgeado; a medicao da correlacao esta em LEFT_OUT.md LO-13. |
| **AUT-27** | [YOU APPLY] | `6633e936` | $\mathcal{L}_k$ glosado; era o unico simbolo da equacao sem glosa. |
| **AUT-28** | C (sem edicao) | `--` | voce optou por nao afirmar nada sobre Pareto. Os quatro probes ficam intactos. |
| **AUT-30** | [YOU APPLY] | `6633e936` | OOD expandido no primeiro uso, a frase de equivalencia virou definicao direta, e o comentario falso de content.tex foi corrigido com a medicao. |
| **AUT-31** | OK | `54cb689d` | §2.4 dividida em "Preparation and data split" e "Comparison and statistical decisions". |
| **AUT-33** | [YOU APPLY] (sem edicao) | `6633e936` | fechado como JA SATISFEITO: o Cap.6 ja separa sinal de treino de arquitetura; varredura com zero defeitos. |
| **AUT-34** | manter (sem edicao) | `--` | voce manteve §6.1 como esta. |

### Os 11 que continuam no `PENDENCIAS.md` §4

| item | por que continua aberto |
|---|---|
| **AUT-02** | a margem de dois pontos no Resumo: ruling A recebido, edicao ainda nao aplicada |
| **AUT-08** | ruling A recebido (fallback do NORTH_STAR), edicao ainda nao aplicada |
| **AUT-09** | ruling recebido (combinar as duas redacoes), edicao ainda nao aplicada |
| **AUT-14** | ruling B: reescrever a secao de Contribuicoes inteira. Trabalho maior, nao iniciado |
| **AUT-26** | voce deixou aberto para consultar o orientador |
| **AUT-29** | ruling recebido (promover Gradient conflict + mudar o inicio de 2.3.2), nao aplicado |
| **AUT-32** | ruling B recebido, oracao ainda nao escrita |
| **AUT-35** | ruling A+B+comentar limitacao 6: a validacao do Massive-STEPS voltou REFUTADA, precisa da sua leitura |
| **AUT-36** | ruling recebido (proximo lugar via Check2HGI), nao aplicado |
| **AUT-37** | ruling OK: reordenar §6.2 em quatro movimentos. Trabalho maior, nao iniciado |
| **AUT-38** | vazio no fonte |

> **Forense completa da rodada**, com ledger de fontes e bandeiras `[VERIFY]` por item:
> `src_utils/_history/_round13/` — `60_terminology_audit.md`, `61_check2hgi_audit.md`, `62_literature_audit.md`,
> `63_conclusion_audit.md`, `70_massivesteps_validation.md`, `71_graphnode_features.md`,
> `72_leak_screening_search.md`, e o seu §4 original preservado byte por byte em `_aut_original.md`.
>
> **Os 26 blocos de auditoria completos**, com a evidencia que a tabela acima resume (DOIs
> verificados, `file:line` de cada defeito, os comandos de medicao, as sobreposicoes), estao em
> [`_history/_round13/_aut_closed_blocks.md`](../_round13/_aut_closed_blocks.md). Medido antes de escrever
> isto: sem esse arquivo, 32 numeros e 20 caminhos do texto removido nao apareciam em lugar nenhum.

---

### ~~2.30 Remocao das sentencas de primeira-autoria do Tarik e dos sete ponteiros \extravolume nos capitulos 3-5~~ — RESOLVIDO (este round)

**Feito, por instrucao do autor: nao mencionar a primeira-autoria de Tarik S. Paiva em prosa
(o regimento da PPGCC nao exige primeira autoria para um capitulo de coletanea), e remover toda
referencia de um capitulo do volume principal ao volume suplementar ("Appendix B/D of the
supplementary volume").**

**Item A — autoria.** Duas sentencas vivas no repositorio afirmavam "Tarik S. Paiva is the first
author" / "second author": a preface de `4_courb.tex` e o bullet do capitulo 4 na lista de
organizacao, `1_introduction.tex:316`. **As duas foram removidas nesta rodada**, mantendo a
contribuicao real do autor da dissertacao (baseline MTLnet, apresentador) sem a ranking de autoria.
Nota de correcao: uma versao anterior deste bloco afirmava que a sentenca de `4_courb.tex` "ja havia
sido removida fora desta sessao, antes de eu comecar". Isso estava ERRADO e contradizia o proprio
paragrafo de efeito colateral abaixo, que atribui a esta rodada o corte da ocorrencia de "MTLnet"
daquela mesma sentenca. A remocao foi feita aqui. **A entrada da bibliografia
(`references.bib`, `paiva2026stmtlnet`) foi deixada intacta por decisao explicita do autor** — e o
registro verdadeiro e verificado no Crossref da lista de autores do artigo publicado, nao uma
narrativa sobre quem escreveu o capitulo da dissertacao, e alterar essa entrada violaria o protocolo
de integridade de citacao (AGENT_GUARDRAILS R2).

**Item B — os sete ponteiros `\extravolume`.** Nenhum capitulo do volume principal deve apontar
para o volume suplementar. Os sete sitios vivos (`3_cbic.tex`, tres em `3_cbic/method.tex`,
`apx_a_contributions.tex`, `4_courb.tex`, `5_mobiwac.tex`, dois em `5_mobiwac/05_setup.tex`) foram
reescritos: onde o ponteiro carregava um fato que o leitor precisa (o achado de escopo do
static-task de `4_courb.tex`, a excecao do encoder relation-typed em `5_mobiwac/05_setup.tex`), o
fato foi dobrado in-line a partir do proprio Apendice B/D (`apx_b_static_scope.tex`,
`apx_d_ceiling.tex`); onde era um ponteiro puro sem conteudo autonomo, foi cortado. O Apendice B e
D em si **nao foram tocados** em `main_extra.tex` — so os ponteiros que apontavam PARA eles.

**Efeito colateral encontrado e corrigido.** Remover a sentenca de autoria em `4_courb.tex` cortou
uma ocorrencia incidental de "MTLnet" que a contagem de normalizacao do Apendice B dependia
(`apx_b_errata.tex`: "normalized to the second form at all 28 places ... 23 in prose"). Recontado
com o mesmo metodo da rodada 6: 27 no total, 22 em prosa. Corrigido em `apx_b_errata.tex` e na
anotacao `EXPECT` de `_history/_round6/VERIFY_LIST.md`.

**Sondas.** Dez sondas novas (`RTV-01`, `02`, `03`, `04`, `05`, `06`, `06b`, `07`, `08`, `08b`) em
`check_audit_claims.py`, cada uma validada
por sabotagem nas duas direcoes (reverter a edicao -> `NOT APPLIED`, `rc=1`; restaurar -> `holds`,
`rc=0`).

**Build.** Os quatro alvos (`defense` 116pp, `academico` 113pp, `ppgc` 117pp, `extra` 26pp) recompilam
limpos, `tex_errors=0` em todos. `make check` e `make selftest` saem `rc=0` (lido diretamente do
`$?`, nao inferido da saida impressa).

**Deixado ABERTO, por instrucao explicita do autor** ("Documente this in the pendencias.md and let
me decide in future"): o ponteiro `Appendix~\ref{apx:cosine}` dentro de `5_mobiwac/02_related.tex`
(um ponteiro de corpo de artigo para outra secao da dissertacao, ainda que o alvo esteja no mesmo
volume principal) e os seis ponteiros `Chapter~\ref{ch:...}` entre os corpos dos artigos dos
capitulos 3-5 apontando para capitulos irmaos. Registrado em `PENDENCIAS.md §2.31`.

---

## §4 (os itens `AUT-`) — A SEGUNDA ONDA: OS 9 QUE FALTAVAM, FECHADOS — 2026-08-04

> **Rodada 13, segunda onda.** Voce respondeu os 11 itens que a primeira onda deixou abertos, e 9 deles
> fecham aqui. Sobram **dois**, e nenhum dos dois espera trabalho meu: o AUT-26 espera o seu orientador
> e o AUT-38 esta vazio no fonte, com o ID reservado para nunca ser reciclado.
>
> **Duas das suas premissas foram REFUTADAS por medicao nesta onda, e as duas mudaram o texto que voce
> pediu.** No AUT-08, a forma comparativa ("na literatura essas duas tarefas tem mais forca") nao tem
> ancora aberta que a sustente e a contagem no OpenAlex aponta para o outro lado, entao entrou a
> **fallback ja sancionada** no `NORTH_STAR`; isso fecha em **negativo** a bandeira `[VERIFY]` que
> aquele beat havia deixado exatamente para essa frase. No AUT-35 (a), os check-ins de Istambul **nao
> sao de 2017-2018**: sao dois blocos, 2012-2013 e 2017-2018, sem nada entre eles, e **70,7% caem no
> bloco antigo** (327.242 de 462.615, medido, com o instrumento verificado antes contra o Gowalla). E
> "o conjunto mais moderno da literatura publica" tambem cai, no Yelp, cujos check-ins vao ate
> 2022-01-19. Voce leu a medicao e escolheu a forma de dois blocos.
>
> **Um defeito que eu encontrei e voce mandou corrigir:** a limitacao 6, "The task-pair confound",
> estava **comentada** na arvore de trabalho, viva no HEAD, sem comentario de proveniencia. A secao
> dizia "Six limitations" e renderizava cinco, e o §6.4 amarra itens de trabalho futuro a **numeros** de
> limitacao, entao perder o item repontava as tags seguintes. Restaurada por sua instrucao. Ela foi
> re-comentada uma segunda vez no meio da rodada e restaurada de novo; a segunda perda foi pega pelo
> probe `R13-lim6live`, que existe para isso.
>
> **Um erro de medicao meu, declarado para nao se repetir:** eu verifiquei as minhas proprias edicoes do
> Cap.6 com `grep -c`, que conta linhas **comentadas** como presentes, e li "cinco de seis sobrevivem"
> numa arvore onde tres estavam comentadas. O `AGENT_GUARDRAILS` §4b V4 existe por isso: greps neste
> fonte tiram os comentarios **primeiro**.
>
> **Todos os itens aplicados tem sonda no gate**, adicionada no mesmo commit da correcao e validada por
> sabotagem individual. `check_audit_claims.py` sai `rc=0` com **197 de 197 probes**, e nesta onda o
> `check.sh` tambem fecha em **rc=0**.

| item | ruling | commit | o que ficou feito |
|---|---|---|---|
| **AUT-02** | A | `--` | voce manteve a margem de dois pontos no Resumo. Sem edicao, por decisao sua. |
| **AUT-08** | Opção 1/A | `b8fdbd12` | a perna comparativa saiu; entrou a fallback sancionada do NORTH_STAR §6 Cap.1 beat 4 (b). Fecha em NEGATIVO a bandeira [VERIFY] que aquele beat deixou para esta frase. |
| **AUT-09** | combinar as duas | `b8fdbd12` | a frase do arco foi reconstruida das duas versoes: o sujeito nomeado da anterior, sem a metafora de trilha que a guarda F4 proibe. |
| **AUT-14** | só as decisoes | `b8fdbd12` | os seus quatro candidatos entraram cada um na forca que a evidencia sustenta; tres contribuicoes nao declaradas entraram com escopo. Voce dispensou a parte mecanica (Cap.4 e ST-MTLNet) e a sua razao esta no fonte. |
| **AUT-29** | concordo + mudar o inicio | `f9885763` | "Gradient conflict" promovida a subsecao irma e colocada antes; §2.3.3 reaberta no problema em vez da formalizacao. Renderiza 2.3.1..2.3.5. |
| **AUT-32** | Opção B | `b8fdbd12` | uma oracao registra a tarefa estatica como historia dos dois primeiros estudos, sem alargar a pergunta de pesquisa. |
| **AUT-35** | A+B+comentar a 6 | `b8fdbd12` | (a) a sua premissa foi REFUTADA e voce escolheu a forma de dois blocos; (b) a transdutividade cita os dois polos antes da frase; (c) a limitacao explica por que a ablacao nao e limpa, marcada como inferencia. |
| **AUT-36** | até quatro frases | `b8fdbd12` | tres itens novos, todos amarrados a limitacoes EXISTENTES; o quarto foi descartado para nao quebrar a regra 1:1. O item do proximo lugar entrou como voce fez questao, no condicional. |
| **AUT-37** | OK | `a47691f8` | §6.2 reordenada em quatro movimentos, com o movimento "o que erramos" que faltava. 24 numerais antes, 24 depois. |

### Os 2 que continuam no `PENDENCIAS.md` §4

| item | por que continua aberto |
|---|---|
| **AUT-26** | voce deixou aberto para consultar o orientador |
| **AUT-38** | vazio no fonte; a sua decisao foi "NADA A FAZER", e o ID fica reservado para nunca ser reciclado |

> **Os 9 blocos de auditoria completos**, com a evidencia que a tabela acima resume, estao em
> [`_history/_round13/_aut_closed_blocks_wave2.md`](../_round13/_aut_closed_blocks_wave2.md). A forense da onda
> esta em `_history/_round13/70_massivesteps_validation.md` (a validacao refutada), `71_graphnode_features.md` e
> `72_leak_screening_search.md`.
