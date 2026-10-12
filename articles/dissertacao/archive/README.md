# archive

Documentos **consumidos**: planejamento cujo prazo passou, e andaimes de uso unico que ja
produziram o que existiam para produzir. A pasta existe para que a fronteira seja explicita,
do mesmo jeito que a `wrapup/`:

> **`wrapup/`** e o que veio **depois** do envio.
> **`archive/`** e o que ficou **para tras** dele.
> O que esta fora das duas e o documento vivo.

**Nada aqui e fonte de nada.** Nenhum numero, nenhum caminho e nenhum estado deste diretorio
deve ser citado como corrente. Varios destes arquivos afirmam com confianca coisas que eram
verdade quando foram escritos e deixaram de ser: e por isso que estao aqui e nao la fora.

| arquivo | o que e | ainda vale? |
|---|---|---|
| `PLAN.md` | cronograma retroativo ate a defesa de agosto, revisao 4 de 24/07 | **nao.** Todos os prazos passaram e o texto ja foi entregue. Ele ainda descreve builds de 118/113 pp, que sao contagens da arvore v1 |
| `TEMPLATE.md` | decisao do template LaTeX mais lista de adaptacao de 12 itens | **nao como lista de tarefas** (o documento foi construido e entregue com ela por marcar). Vale como registro de *por que* o esqueleto Germano foi escolhido |
| `prompts/science.md` | encomenda da rodada de levantamento cientifico | nao. Andaime de uso unico, ja executado |
| `prompts/story_review_prompt.md` | encomenda da revisao da linha narrativa | nao. Idem |
| `prompts/v1_assembly_prompt.md` | encomenda da montagem da v1 | nao. Idem, e a v1 que ele monta foi substituida |
| `prompts/useful_prompts.md` | colecao de prompts reaproveitaveis da fase de escrita | so como material de consulta; nada depende dele |
| `RESUME_tarik_authorship_cleanup.md` | nota de retomada de uma sessao sobre autoria e apendices | **nao.** A propria nota declara a sessao como `completed`. As duas decisoes que ela registra ja estao no texto |

## O que NAO veio para ca, e por que

- **`wrapup/open_points/RESUME_paused_texas_job.md`** parece uma nota de sessao antiga, mas
  carrega estado de computacao vivo: o braco `rg2` da triagem de mecanismo de regiao foi morto
  no meio de uma dobra e **precisa ser relancado**. Isso e o item P4 de `LACUNAS.md` §1, que
  continua aberto. Foi para `wrapup/open_points/`, junto do registro que o cita.
- **`fundamentals/` e `storyline/`** sao rascunhos congelados, e pareceriam candidatos obvios.
  Ficaram onde estavam porque o texto **entregue** cita caminhos dentro deles como proveniencia
  (o `preamble.tex` e capitulos apontam para `storyline/audit/`, e o `references.bib` para
  `fundamentals/_bib/`). Move-los quebraria citacoes do documento que foi para a banca.
- **A antiga arvore `src/` (v1)** nao foi arquivada, foi **apagada**. Manter uma segunda copia
  completa de cada capitulo, com numeros que contradizem os entregues, e exatamente a armadilha
  que esta reorganizacao existiu para remover: entre 11/08 e 20/08 os portoes de qualidade
  rodaram sobre ela sem que ninguem percebesse. Ela esta no historico, recuperavel com
  `git checkout dissertacao-pre-reorg -- articles/dissertacao/src`.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-20 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
