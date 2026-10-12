# evidence

Copias unicas resgatadas das arvores que foram apagadas na reorganizacao de 2026-08-20
(`src/`, `src_clean/`, `tmp/`, `handoff/`). A pasta existe porque cada arquivo aqui era o
**unico** exemplar do que ele registra: nenhum deles reproduz a partir de outro lugar do
repositorio, e todos estavam em arvores marcadas para exclusao.

Nada aqui entra em nenhum build. Nada aqui altera o documento entregue.

| arquivo | o que registra | ainda vale? |
|---|---|---|
| `ladder_recompute.json` | a escada de veredito do Cap. 5 em precisao completa: por tarefa e por dataset, o dedicado, o conjunto, o desvio, o delta, o `p` de superioridade, o TOST, o intervalo e o `p` de Holm | **sim, e e a fonte de maior precisao que existe.** As tabelas do texto arredondam para duas casas. Uma busca no repositorio inteiro por `35.42276814579964` retorna so este arquivo |
| `ledger_extra.json` | a folga de convencao (`db_minus_jb`: melhor-diagnostico menos checkpoint-servido) por dataset, mais o contraste de nivel de lugar | sim. Limita o que a frase de robustez pode afirmar |
| `mobiwac_applied.diff` | o diff de 99 KB efetivamente aplicado em `articles/[mobiwac]/src_fix`, lido na integra durante a auditoria do REVISION_PLAN | sim como registro do que foi aplicado. Nao e a fonte do texto: essa e a propria arvore do MobiWac |
| `site_inventory_v1anchored_2026-08-11.json` | inventario de sitios de afirmacao por arquivo e linha, com o trecho citado | **so em parte.** Os numeros de linha estao ancorados na arvore v1 de 11/08, que nao existe mais. Os arquivos e os trechos continuam validos; **as linhas nao.** Localize pelo trecho, nunca pela linha |
| `signoffs_snapshot_2026-08-03.json` | os 56 marcadores `[NEEDS SIGN-OFF]` como estavam em 03/08, com o texto integral de cada um | **so como historico.** A contagem 56 esta invalidada (LACUNAS declara a de 56 como item invalido) e os caminhos dizem `src/chapters/...`, que era a arvore v1. A contagem viva e outra, e esta em tres lugares (veja abaixo) |
| `review_screenshots/` | **removido em 2026-09-30** (37 imagens de paginas de builds anteriores, sem citador; os achados vivem em `open_points/LACUNAS.md` e `REVISAO_BANCA_PDF.md`) | recuperavel na tag `dissertacao-pre-organizacao` |

## A contagem de marcadores de aval nao mora mais em um lugar so

O `signoffs_snapshot` conta 56 sobre uma arvore unica. Depois do commit `264c7996` os
marcadores ficaram repartidos em tres lugares, e um comando que entra so na arvore principal
perde dez deles, **incluindo o NSO-46, que e o unico item de aval que LACUNAS §2 ainda lista
como aberto**. Medido em 2026-08-20:

    src/                     24
    wrapup/material_extra/    9
    wrapup/erratas/           1
    total                    34

Reproduza com `grep -rho "\[NEEDS SIGN-OFF" --include="*.tex" <dir> --exclude-dir=build | wc -l`
nos tres diretorios, e some. Um numero unico aqui e sempre suspeito.
