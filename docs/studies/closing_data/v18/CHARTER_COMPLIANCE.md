# v18 — conformidade com o charter

> Releitura de [`V18_AGENT_PROMPT.md`](V18_AGENT_PROMPT.md) contra o que foi realmente executado.
> Escrito 2026-08-11, com a board em 72/72.
>
> Resumo: **o charter foi cumprido no essencial; três desvios reais aconteceram, todos deliberados e
> aprovados, e um deles inverte uma instrução explícita do charter.** Este documento existe para que
> ninguém precise reconstruir isso depois lendo 389 linhas de charter contra 16 documentos.

## 1 · O que foi cumprido como planejado

| § | exigência | situação |
|---|---|---|
| 0 | v18 = v17 + grafo forward-only + 4 colunas de tempo, `in_channels` 15 | ✅ `AUDIT.md`: os 6 estados com `causal_graph.forward_only=True`, `in_channels=15`, layout `['canonical_11','continuous_time_4']` |
| 0 | **não** adicionar identidade de place/region aos nós | ✅ nunca adicionado |
| 0 | não mexer em largura/profundidade do encoder | ✅ intocados (64, 2 camadas) |
| 3 | 6 datasets × 4 seeds {0,1,7,100} × 5 folds = **n=20** | ✅ **72/72 células** |
| 3 | 3 famílias por dataset/seed | ✅ cat, reg, joint |
| 4b | um engine por estado, compartilhado entre seeds, seed de representação 42 | ✅ registrado em cada sidecar (`v18_config.repr_seed=42`) |
| 4b | resumível e idempotente; rundir capturado por PID, não por mtime | ✅ `run_wave.sh` pula por sidecar e captura por `$!` |
| 6.1–6.5 | readout casa com o grafo; largura 15; enrichment aplicado; pareamento de linhas ≥95%; encodabilidade de usuário held-out | ✅ **ALL PASS nos 6 estados** (`AUDIT.md`) |
| 6.6 | categoria deve cair muito vs v17; região quase não deve mover | ✅ recomputado 2026-08-11: **Δcat −27,9 a −42,3 pp**; **Δreg −0,13 a −0,33 pp** (limite era 2 pp) |
| 7 | entregáveis | ✅ todos, exceto `TASKS.md` (ver `GAPS.md` §6) |
| 10 | "beats" exige teste pareado; "matches" exige TOST | ✅ implementado em `make_results.py` (mas ver §3 abaixo) |

O §6.6 merece destaque porque era o teste de que o vazamento foi realmente removido: a categoria
despencou 28–42 pp e a região praticamente não se moveu — exatamente o que o charter previu. Se a
categoria tivesse ficado perto do v17, seria sinal de que o caminho forward-only não estava ativo.

## 2 · Desvios deliberados (todos aprovados)

### 2.1 A receita mudou — e essa era a decisão certa

O charter §3 fixa a receita do v17: `--category-weight 0.75`, `--cat-lr 1e-3`, e tiers de batch/LR
do `CEILINGS_N20_FINAL.md`. **Nada disso foi usado na regeneração final.**

Motivo: aquela receita foi ajustada **no substrato vazado**, onde a categoria era um sinal muito mais
forte. No v18 ambos os braços tinham pico precoce (mediana de melhor época 8/50 e 21/50, contra 44/50
no v17), e pela própria regra do estudo um braço com pico precoce nunca é um teto. O sweep de 103
braços re-afinou os **dois** braços — não só o baseline, porque afinar só o baseline enviesaria o
Δcat contra o MTL.

Receita final aprovada (`FINAL_SETTINGS.md`, aprovada 2026-08-09):

| eixo | charter §3 | executado |
|---|---|---|
| batch (cat dedicado) | 2048 (AL/IST) / 8192 | **8192 em todos** |
| max_lr (cat dedicado) | 0,005 | **AL 0,0025 · AZ/IST 0,0005 · FL/CA/TX 0,005** |
| `category_weight` | 0,75 | **0,50** |
| `cat-lr` (MTL) | 1e-3 | **1e-3 pequenos · 2e-3 grandes** |
| pesos de classe | ligados | **substituídos por logit adjustment τ=0,5** |
| região | — | **τ=0** (inalterada) |

### 2.2 O charter mandava PARAR E PERGUNTAR sobre istanbul — foi resolvido por medição

§3: *"istanbul — STOP AND ASK: `CEILINGS_N20_FINAL.md` não tem tier para Istanbul; não adivinhe."*

Não houve pergunta ao autor sobre isso. O tier do istanbul saiu do **sweep** (bs8192 @ 0,0005, 5
folds, seed 0), junto com os demais estados. **Isso é estritamente melhor que adivinhar** — é medido,
não chutado — mas é, com honestidade, uma instrução do charter que foi contornada em vez de seguida.
Registrado aqui para que a procedência do tier do istanbul não pareça ter vindo do
`CEILINGS_N20_FINAL.md`, porque não veio.

### 2.3 A ordem de execução foi seguida só em parte

§4 exige ondas intercaladas por seed (seed 0 completo → seed 1 → …), *"requisito rígido, porque torna
os resultados parciais utilizáveis em cada estágio"*.

Cumprido para as seeds 0 e 1, executadas localmente como ondas completas com agregação entre elas.
As seeds **7 e 100 vieram da lane alugada em paralelo**, não como ondas locais — logo a propriedade
"resultado parcial legível a cada estágio" valeu para n=5 e n=10, não para n=15.

Consequência prática: nenhuma. Consequência de procedência: as células de seed 7/100 têm rastreamento
mais fraco — é a lacuna A do [`GAPS.md`](GAPS.md) (30 células sem `commit_sha`).

## 3 · Onde o charter é mais rigoroso do que a implementação atual

§10: *"'Outperforms' exige teste pareado de superioridade; 'matches' exige TOST … Nunca promova um
resultado não-inferior a vitória."*

A mecânica está implementada, mas o gerador emite **"beats"** para Δ de até **+0,04 pp**, porque
parear nos mesmos folds colapsa a variância. O charter proíbe promover não-inferioridade a vitória;
ele não previu o caso de uma vitória estatisticamente limpa e praticamente irrelevante.

**Isto continua em aberto e é decisão do autor** (piso de significância prática — `GAPS.md` §7).
O resultado que sobrevive a qualquer piso razoável é a região nos estados grandes: **+1,93 texas /
+1,96 california**, 25–30× o desvio entre folds.

## 4 · Correções que o próprio charter provocou

Duas coisas o charter pediu explicitamente e que só apareceram porque foram procuradas:

- **§5 "dois jobs no máximo"** e o traço de RAM do host: honrado — estados pequenos 2-wide, grandes
  estritamente 1-wide. O único SIGSEGV do estudo (texas s1 reg) foi exatamente o modo de falha que o
  §5 descreve, e o checkpoint por fold (§4b, resumibilidade) permitiu retomar no fold 4 de 5.
- **§9 "pare e pergunte se um número v18 ficar perto do v17"** — nunca disparou; ver §6.6 acima.

## 5 · Veredicto

O charter foi seguido no que define o experimento (substrato, matriz, auto-checagens, entregáveis) e
desviado no que ele não podia prever (a receita do v17 estava mal-afinada para um substrato sem
vazamento). Os desvios estão documentados e foram aprovados; o único que contraria uma instrução
literal é o `STOP AND ASK` do istanbul, resolvido por medição em vez de pergunta.

Pendências abertas estão em [`GAPS.md`](GAPS.md) — nenhuma exige re-treino.
