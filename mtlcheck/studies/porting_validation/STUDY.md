# porting_validation

**Aberto:** 2026-08-12 · **Status:** aberto

## A pergunta

O `mtlcheck` reproduz as **conclusões científicas** do v18, ou a reescrita introduziu deriva?

A barra foi fixada pelo autor: não é igualdade dígito a dígito — inatingível de qualquer forma, já
que o protocolo v18 roda com `--compile` e o próprio `METHODOLOGY.md` registra que números compilados
não são bit-reproduzíveis. É reproduzir as conclusões.

## Critério de decisão

Duas camadas, com exigências diferentes:

**Determinística — tem que ser exata.** Folds, contagens, janelas, pesos de aresta, contagens de
parâmetro, loss, métricas e seleção de época. Aqui não há tolerância: são funções puras dos mesmos
dados, e qualquer diferença é defeito.

**Treinada — dentro do desvio entre folds.** Um número de treino em MPS não vai igualar um em A40 com
compile. O que tem que se manter é a ordem de grandeza e a direção.

## Referências congeladas

| O quê | Valor |
|---|---|
| Código de referência | `/Users/vitor/Desktop/mestrado/ingred`, worktree em `aab23985` |
| Board de referência | `docs/studies/closing_data/v18/V18_RESULTS.md` (dedicada AL cat = 30,77, n=20) |
| Receitas | `recipes/v18/{cat,reg,joint}.toml` |
| Substrato | `check2hgi_v18`, artefatos de Alabama copiados do A40 |
| Datasets | alabama (os demais quando houver GPU) |
| Seeds | 0 (as quatro quando houver GPU) |

## O que este estudo NÃO vai responder

- Se o v18 está cientificamente certo. Ele é a especificação, não o objeto de teste.
- Se o substrato reconstruído bate com o do A40 — o treino do encoder não foi portado.
- Nada sobre estados que não sejam Alabama, enquanto o A40 estiver ocupado.
