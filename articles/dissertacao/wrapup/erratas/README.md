# erratas

Erratas escritas **depois** de o texto ser concluido e enviado. Nada aqui entra em nenhum build.

Cada errata e um `.tex` autocontido, escrito na forma em que entraria no documento, com um
cabecalho de comentario que diz o que ela corrige, onde a frase original vive, e como cada numero
foi verificado. Quando o deposito final for montado, cada arquivo tem um destino declarado no
proprio cabecalho.

| arquivo | corrige | estado |
|---|---|---|
| `errata_Q13_concatenation_scope.tex` | a frase do Cap. 5, p. 79, que afirma uma separacao que o artigo submetido recusa sobre os mesmos numeros | **valores aplicados ao fonte a 2026-10-01** (commit `e6ac03c0`): o `06_results.tex` imprime os ganhos pareados da Q13, +1,73 / +1,70 / +1,02, no lugar de +2,0 / +1,7 / +0,8, e a linha da B.5 declara-o. A inversao mais forte que este `.tex` redige continua fora: o autor recusou-a a 2026-09-02 (`articles/[mobiwac]/ERRATA.md`, seccao do camera-ready, "Recusado"). Ate 2026-10-02 esta celula dizia "escrita; so fecha com um estudo na representacao final" |
| `errata_Q14_capacity_region.tex` | a lista de limites do Cap. 5, que perdeu o confundimento de capacidade no eixo de regiao | escrita, e ja traz a medicao que o artigo declarava faltar |
| `errata_resumo_escopo_categoria.tex` | o Resumo em portugues, que dizia que o modelo conjunto superou os dedicados na proxima categoria "em todos os conjuntos" quando o resultado entregue e superioridade em UM conjunto | escrita e **ja aplicada ao fonte** (2026-08-21, decisao do autor). O PDF entregue foi congelado como `src/banca.pdf`; a correcao entra no `src/dissertacao.pdf`, o build corrente |
| `RESPOSTAS_ORAIS.md` | a frase a ser dita em pe para cada uma, mais Q15 (a de Q14 corrigida a 2026-10-02 para os numeros de 2026-09-02) | — |
| `VERIFICACAO.md` | cada numero das erratas contra o artefato de origem | — |

## Correcoes aplicadas sem linha impressa

Correcoes ao texto que o autor decidiu registar **so aqui**, sem linha no Apendice B de nenhum
volume. Ficam neste ficheiro porque um leitor que compare o capitulo com o artigo publicado vai
encontrar a diferenca e tem de poder saber porque ela existe.

### TME descrito de duas maneiras incompativeis no mesmo capitulo (2026-09-02)

`3_cbic/basis.tex` descrevia o mesmo modelo de duas formas, com cerca de quarenta linhas de
intervalo:

- `:22`, e a descricao que fica: *"the Tree-guided Multitask Embedding (TME) model, which aims to
  improve the semantic annotation of POIs using a hierarchical structure of categories and
  mobility-based representation learning"*
- a frase corrigida, que dizia: *"Some models, such as TME, address category annotation using
  **graph-based encoders** but treat prediction and classification separately"*

A segunda agrupava o TME com trabalhos de grafos. Nem a primeira nem o Cap. 2 o fazem
(`2_fundamentals.tex`: *"TME instead applies tree-guided multitask embedding to static semantic POI
annotation"*). Duas descricoes em tres concordam, e a que destoa e a que atribui o encoder.

**A correccao e de consistencia interna e nao afirma nada sobre o artigo do Xu et al.** A frase
passou a usar as palavras que o proprio capitulo ja usa para o mesmo modelo, mantendo as duas
afirmacoes que continuavam sustentadas: que o TME trata anotacao de categoria, e que separa
predicao de classificacao. A frase enumerava so o TME, portanto nao havia outro modelo a que o
"graph-based encoders" pudesse ligar-se correctamente; reordenar nao era saida.

⚠ **O QUE NAO FOI VERIFICADO, e porque isto importa.** Numa versao anterior desta analise eu
afirmei, aqui e ao autor, que o TME e fatorizacao de matriz PMI e nao tem encoder de grafo nenhum.
**Nao ha fonte para isso nesta arvore**: nao existe PDF do artigo, a entrada bib e a do artigo CBIC
doador carregada verbatim, e a auditoria de literatura do round 13 cita `Xu2023` sem descrever o
encoder dele. Era inferencia minha apresentada como facto. Por isso a correccao **nao caracteriza a
arquitectura do TME** — corrigir uma afirmacao nao sustentada com outra afirmacao nao sustentada
seria trocar um erro por outro. Se alguem vier a ler o artigo e quiser dizer o que o TME e, ai sim,
com a fonte a frente.

Decisao do autor, 2026-09-02: registo interno, sem linha impressa.

## Q24 nao gerou errata

Eu havia registrado como defeito o fato de o volume principal nao apontar para o material
extra. Nao e defeito: o texto depositado cita apenas o proprio texto e o repositorio, sem
referencias externas, e isso e a politica do documento. O material extra foi escrito como apoio
a defesa e agora vive em `../material_extra/`.

## Material extra

`material_apx_static_scope.tex` veio de `src_fix/chapters/`, onde existia sem ser incluido em
nenhum build. Ele esta aqui porque **parte dele serve a argumentacao oral** e nada dele esta nos
dois volumes: documenta um canal de autovazamento medido no embedding do Cap. 3, com peso medio de
0,10 contra 0,39 da propria categoria, e uma sonda caindo de 0,46 para 0,30 macro-F1 contra piso de
0,07.

Duas ressalvas antes de usar qualquer numero dele: a medicao e sobre a **preparacao anterior** da
representacao, e o proprio arquivo carrega um pedido de aval do autor que nunca foi respondido.
Nenhum arguidor faz essa pergunta sem o repositorio, mas com o repositorio ela e a unica coisa que
os dois documentos nao antecipam.

## Q15 nao gerou errata

A linha de errata do suplemento que descreve um quarto fundamento de integridade, com sonda linear
em Florida, descreve uma auditoria sobre construcoes anteriores da representacao, e a propria linha
declara esse limite. A correcao e retirar a linha, nao adicionar o fundamento ao texto. Detalhe em
`RESPOSTAS_ORAIS.md`.
