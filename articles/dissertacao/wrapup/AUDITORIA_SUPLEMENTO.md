# O volume suplementar: auditoria de conteudo

Pergunta do autor, 2026-08-14: trazer o material do `main_extra.tex` para a `wrapup`, avaliando o
que ainda e valido e arquivando o que nao e.

## A ressalva que muda a resposta

**O suplemento e um volume entregue, nao material solto.** Ele se declara na propria capa
*"Supplementary Material to the dissertation ... published beside it rather than inside it"*, tem
capa, sumario e cinco apendices. Move-lo para a `wrapup` desmontaria um dos dois volumes que a banca
recebeu.

**Uma correcao ao que eu havia escrito aqui.** A primeira versao deste documento afirmava que a
§1.5 do volume principal anuncia o suplemento. **Nao anuncia.** Medido: zero referencias vivas ao
suplemento em qualquer arquivo incluido no volume principal, e a §1.5 e a secao de organizacao da
dissertacao, que descreve os capitulos e nao menciona o volume companheiro. O apontamento existe na
direcao inversa: o suplemento carrega uma tabela de rotulos congelados que aponta para a §1.5.

Isso enfraquece um dos argumentos, mas nao a conclusao. O que sustenta a decisao de nao mover e o
que o proprio volume declara de si na capa e no capitulo de abertura, mais o fato de ter sido
entregue junto. **E tambem revela um ponto para a defesa:** o volume principal nao aponta para o
suplemento em lugar nenhum, entao um leitor do PDF principal nao descobre que os cinco apendices
existem. Vale uma frase na §1.5, e ela seria errata.

Por isso a decisao aqui e **auditar, nao mover**. A `wrapup` guarda o que veio depois do envio; o
suplemento veio antes, e junto. O que esta auditoria produz e o veredito por apendice, para que
material invalido nao seja usado em argumentacao oral.

## Veredito por apendice

| apendice | o que registra | le vetores? | veredito |
|---|---|---|---|
| **B, Errata aos artigos reproduzidos** | cada divergencia dos tres capitulos reproduzidos em relacao ao original publicado ou submetido | nao, e um registro editorial | **VALIDO**, com uma linha a retirar (ver abaixo) |
| **D, Benchmark de historico de rotulos** | quanto da proxima categoria se preve do historico de categorias da janela | **nao**: o artefato declara `label-only ... (no embeddings read)` | **VALIDO** |
| **E, A questao de sujeitos humanos** | a posicao do autor sobre necessidade de comite de etica | nao, e uma posicao declarada | **VALIDO** |
| **F, Adaptacao da baseline HGI** | a selecao do peso de aresta entre regioes, 0,4 a 0,7, cinco folds em Alabama | sim, mas e a **selecao de um hiperparametro da propria baseline**, feita antes de aplica-la | **VALIDO**: descreve como a baseline foi configurada, nao um resultado da dissertacao |
| **G, Controle de contagem de parametros** | alargar o dedicado de categoria ate o orcamento do conjunto | sim | **VALIDO, e na preparacao ATUAL** (ver correcao abaixo) |

## Correcao a auditoria de 2026-08-13

A auditoria pre-leak classificou o controle de capacidade em categoria como rodado na preparacao
anterior, com base no diretorio `capacity_matched_stl_cat/`, que de fato carrega marcas de
`check2hgi_dk_ovl` e v17. **Estava errado sobre a fonte.**

Os numeros que o apendice imprime vem de `docs/results/closing_data/apxi_v18/apxi_final.json`, e
reproduzem exatamente: Alabama, quatro sementes, largo $30{,}2410$ contra estreito $30{,}7750$, que
da $-0{,}53$ com $p = 0{,}0011$ e direcao unanime, os tres valores que o apendice declara; California
semente 0, os tres bracos em $0{,}057$ ponto, que o apendice arredonda para $0{,}06$. O sufixo do
diretorio nomeia a preparacao: **v18**.

O `capacity_matched_stl_cat/` e a execucao anterior, superseda. O veredito da auditoria nao muda, o
apendice continua valido, mas o motivo muda: nao e "valido apesar de pre-leak porque a comparacao e
interna", e sim **valido porque foi medido na preparacao atual**.

## A linha do Apendice B que sai

E a de Q15, ja tratada em `erratas/RESPOSTAS_ORAIS.md`: a linha que descreve um quarto fundamento de
integridade com sonda linear em Florida. Ela descreve uma correcao que o texto depositado nao
carrega, medida sobre construcoes anteriores da representacao, e a propria linha declara esse limite.

## O `TODO` que o Apendice G carrega, e que agora tem resposta

O arquivo abre com `%TODO: AUTHOR do this experimento for next-region`. Esse experimento foi
executado em 2026-08-13 e esta em `post_submission_studies/P1_capacity_region.md`. O apendice cobre
categoria; P1 cobre regiao, e e a errata Q14 que leva o resultado ao texto.
