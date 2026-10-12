# material_extra

O volume de material extra, escrito como apoio a defesa. Ele vive aqui, e nao em `src_fix/`, porque
nao faz parte do texto depositado: o volume principal cita apenas o proprio texto e o repositorio,
sem referencias externas.

## Como construir

    cd wrapup/material_extra && make extra

Sai em `build/main_extra.pdf`, 27 paginas. O comando antigo, `make extra` dentro de `src_fix`,
continua funcionando e chama este.

## O que ele contem

| apendice | o que registra | ainda vale? |
|---|---|---|
| Errata aos artigos reproduzidos | cada divergencia dos capitulos 3 a 5 em relacao ao original publicado ou submetido | sim, menos uma linha (abaixo) |
| Benchmark de historico de rotulos | quanto da proxima categoria se preve so do historico de categorias da janela | sim. O artefato declara que nao le embeddings, entao a correcao do vazamento nao o alcanca |
| A questao de sujeitos humanos | a posicao do autor sobre necessidade de comite de etica | sim |
| Adaptacao da baseline HGI | como o peso de aresta entre regioes foi escolhido, de 0,4 a 0,7, em Alabama | sim. Descreve como a baseline foi configurada, nao um resultado da dissertacao |
| Controle de contagem de parametros | alargar o dedicado de categoria ate o orcamento do modelo conjunto | sim, e medido na preparacao atual |

## A linha que sai da errata

E a que descreve um quarto fundamento de integridade, com uma sonda linear em Florida. Ela promete
uma correcao que o texto depositado nao carrega, e foi medida sobre construcoes anteriores da
representacao. A propria linha declara esse limite. Detalhe em `../erratas/RESPOSTAS_ORAIS.md`.

## Duas notas para quem for usar isso na defesa

**A razao de parametros do controle de capacidade.** O apendice diz que o modelo alargado carrega
$6{,}5$ vezes os parametros do estreito. Essa razao vem de uma auditoria cujo alvo foi o modelo
conjunto como ele era quando o controle foi desenhado. O modelo conjunto atual e maior, entao a
razao contra ele seria maior ainda. Os escores do apendice sao da preparacao atual; so a razao e
que descreve o modelo anterior. Isso nao muda a conclusao, porque a conclusao e que largura piora o
resultado de categoria, e um alvo maior so aumentaria a largura.

**As dependencias.** As tabelas, a classe e a bibliografia continuam vindo de `../../src` (era `../../src_fix` ate a reorganizacao de 2026-08-20), por
`TEXINPUTS` e por um link em `references.bib`. Duplicar esses arquivos criaria duas copias que
divergem sem aviso.
