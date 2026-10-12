---

## Nota de verificacao do autor-agente (2026-08-13)

Os dois registros desta pasta foram escritos por sub-agentes. Esta nota declara o que **eu** verifiquei
de forma independente, item por item, e o que aceitei sem medir. Ela existe porque afirmei duas vezes
uma cobertura de leitura maior do que a que tinha, e a correcao pertence ao arquivo, nao so a conversa.

### Lido por inteiro
`LACUNAS.md` (633 linhas) e `ARGUICAO.md` (705 linhas), integralmente.

### Medido de forma independente, e confere
| alegacao | fonte da alegacao | medido |
|---|---|---|
| `apx_b_static_scope` sem `\input` vivo | NSO-46 | 0 inclusoes; o paragrafo nao chega ao leitor |
| 100 entradas no bib, 98 citadas, 2 orfas | ERR-4 | identico; as orfas sao `belkin2003laplacian` e `santos2024urban` |
| 16 blocos `[ORPHANED]` | PENDENCIAS 2.27 item 1 | 16 em `src_fix` e `src`, 0 em `src_clean` |
| 34 marcadores de aval, 32 CLOSED, 1 OPEN | PENDENCIAS 2.1 / NEEDS_SIGN_OFF | identico nas tres arvores |
| builds de 119 / 114 / 27 pp | PENDENCIAS 2.27 (C) | identico |
| `\ref` vivo para o Apendice E | PENDENCIAS 2.32 | 1 ocorrencia |
| 9 de 9 rotulos congelados | REVISION_PLAN §15.5 | 9 de 9 |
| 0 linhas decorativas | LO-10 | 0 |
| paginas do Nash-MTL | _round6 item 14 / LO-9 | `16428--16446`, bate |
| "of the twelve" ausente dos builds | REVISION_PLAN §17.3 | 0 nos dois volumes |
| 13 ambientes de definicao no Cap. 2 | CONSIDERATIONS GER-09 | 13 |
| tres expressoes do limite de capacidade ausentes | Q14 | 0 nos dois volumes |
| escopo declarado do apendice do cosseno | U4 | "four of the six datasets" 2x, "largest label spaces untested" 1x |
| as duas afirmacoes de ausencia de Q13 | Q13 | "place-to-check-in gap" 1x no principal; "separate study" 0x nos dois |

### Uma divergencia encontrada
**LO-13** afirma 2 ocorrencias de "share an origin by construction"; medido **1** em toda a arvore. Nao
altera a conclusao do item, mas o numero esta inflado.

### Aceito sem medir, e declarado como tal
- **GAPS B, E, F** e **LO-2 a LO-8**: fechados por decisao registrada e por execucao, nao por
  inspecao de fonte. Nao ha grep que os confirme; eu li o registro e nao reexecutei a evidencia.
- **Q9** (escolha do balanceador) e as demais respostas do Grupo A: li as entradas e as citacoes que
  elas fazem, e nao remedi cada numero contra o PDF.
- Tudo que o proprio `LACUNAS.md` declara como nao coberto: os numeros dos Caps. 3 e 4 contra os
  artigos publicados, 19 dos 21 itens `[I DECIDE]`, e a prosa de 43 dos 46 blocos de `CONSIDERATIONS`.
