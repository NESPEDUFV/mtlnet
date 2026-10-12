# Investigação — alternância CPU/GPU na célula dedicada next-region (p1)

**Data:** 2026-08-10 · **Escopo:** por que o treino dedicado `next_reg`
(`scripts/p1_region_head_ablation.py`, lançado por `docs/studies/closing_data/v18/run_wave.sh`)
alterna fases GPU-pesadas e CPU-pesadas na A40, enquanto o next-category dedicado e o
joint/MTL ficam predominantemente na GPU. **Somente investigação — nenhum arquivo de
produção foi alterado.**

Métodos: leitura do caminho de execução real em `src/` + `scripts/`, arqueologia de git
(o estado do código que a A40 executava vs `2c844974`), evidência prévia em
`docs/studies/closing_data/v18/log.md` (linhas 40–81, medições datadas), e um
microbenchmark local de CPU reproduzindo os três estados históricos do scoring de
validação (paridade 0.0e+00 entre caminhos; ver §3).

---

## 1. Reconstrução do caminho de execução

### 1.1 Célula reg dedicada (p1) — o caminho que alterna

Por célula (`run_wave.sh:157-162`): `p1_region_head_ablation.py --heads next_stan_flow
--input-type region --folds 5 --epochs 50 --compile --tf32`, com
`MTL_CHUNK_VAL_METRIC=1 MTL_DISABLE_AMP=1`.

1. **Uma vez por célula (CPU puro):** carga dos parquets + construção do tensor de
   sequência de regiões — loop Python sobre 9 posições com `pd.Series.map`
   (`p1:259-299`), `_convert_to_tensors`, split `StratifiedGroupKFold` (`p1:934-943`).
2. **Uma vez por fold (CPU puro):** `seed_everything`; fatiamento fancy-index do tensor
   completo na CPU (`p1:591-592`) + cópia H2D via `POIDataset(..., device=DEVICE)`
   (`folds.py:237-239` — o dataset do p1 é **sempre** GPU-residente, sem auto-fit);
   construção do head + **`torch.compile` de um modelo novo a cada fold** (`p1:622-646`,
   variantes train/eval + shapes de último batch parcial); `build_calibrated_loss`
   (bincount CPU, trivial); checkpoint JSON atômico ao fim do fold (`p1:1083-1087`).
3. **Loop de treino (GPU):** sem métrica de treino nenhuma — por batch apenas
   `forward → loss → backward → clip → step → scheduler.step()` (`p1:677-687`).
   Dataset na GPU com fetch batched `index_select` (`folds.py:250-257`), `num_workers=0`
   (`folds.py:315-328`). Nenhum `.item()`/`.cpu()` no loop. **Limpo.**
4. **Validação (o ponto da divergência):** ver §2 — aqui mora a alternância.

Colateral encontrado: com `freeze_alpha=True alpha_init=0.0` e sem
`--per-fold-transition-dir`, o head registra `log_T` de **zeros** `[C,C]`
(CA: 8501² × 4 B ≈ 289 MB de VRAM) e, mesmo assim, executa a cada forward o gather
`log_T[safe_idx]` ([B,C] ≈ 70 MB), `masked_fill`, multiplicação por α=0 e soma
(`src/models/next/next_stan_flow/head.py:119,142-151`) — trabalho GPU provadamente
inerte (~3-4 passes [B,C] extras por batch, em treino E validação). Não causa a
alternância (é GPU), mas é wall desperdiçado; o análogo do MTL tem
`MTL_SKIP_INERT_LOGT=1`, o p1 não tem equivalente.

### 1.2 Célula cat dedicada — por que não alterna

`train.py --task next` → `next_cv.py:100-209` → `_single_task_train.py`. C=7:
os logits de val `[N_val, 7]` ficam na GPU, `compute_classification_metrics` roda o
caminho torchmetrics **no device dos logits** (`metrics.py:525-541`); os poucos
`.item()` por época são desprezíveis. A métrica de treino (`compute_train_f1=True`)
retém logits [N,7] na GPU — trivial. **Não existe nenhuma operação O(N·C) na CPU
porque C=7 torna O(N·C) ≈ O(N).** A célula cat nem lê `MTL_CHUNK_VAL_METRIC`
(log.md:43).

### 1.3 Joint/MTL — por que não alterna (mais)

- **Val (S2):** `mtl_eval.py:190-208,276-291` — com `MTL_CHUNK_VAL_METRIC=1` o reg-head
  faz streaming de reduções por linha **na GPU** ("streamed on GPU … NEVER CPU-moved");
  só vetores [N] chegam ao host.
- **Treino (S1):** `mtl_cv.py:1729-1751` — streaming na GPU com `store_on="cpu"`
  (apenas [batch] int64 vai ao host por batch). O comentário no próprio código registra
  que **o joint teve exatamente a mesma doença** ("the old path did a per-batch [batch, C]
  `.cpu()` copy … the dominant sink that pegged the CPU and starved the GPU on the
  wide-reg-head states (CA/TX)") — **corrigida em 2026-06-24**.
- Perdas acumuladas on-device, um `.item()` por época (`mtl_cv.py:1712,1777-1779`);
  diagnósticos pesados default-OFF (`MTL_TRAIN_DIAGNOSTICS`, `train.py:2075-2085`).
- Além disso o modelo do joint (mtlnet_crossattn_dualtower, bs8192, duas tarefas) tem
  trabalho GPU por batch ordens de grandeza maior que o head de 0.47 M — mesmo um custo
  CPU igual seria proporcionalmente invisível (TX joint 22453 s vs reg 5897 s na A40).

**Resposta à pergunta central ("o que é diferente no next-region?"):** não é a tarefa,
é a **combinação (C alto) × (caminho de scoring que ficou para trás)**. O mesmo padrão
per-batch-`.cpu()`+scoring-CPU já tinha sido identificado e removido do joint (S1 em
06-24, S2 sempre-GPU) e nunca existiu no cat (C=7). O p1 era o último call-site com o
padrão antigo — e `run_wave.sh:157` ainda o **forçava** em todos os estados via
`MTL_CHUNK_VAL_METRIC=1`, inclusive nos pequenos onde a guarda de OOM não protege nada
(AL 0.09 GB, AZ 0.25 GB, IST 0.11 GB vs orçamento de 4 GB — log.md:42,73).

---

## 2. Hipóteses testadas e vereditos

| # | Hipótese | Evidência / teste | Veredito |
|---|----------|-------------------|----------|
| H1 | Offload de logits de val para CPU | `git show 82bca519:p1` (o código na A40): por batch `out.cpu()` síncrono + `torch.cat` CPU do [N_val,C] + `compute_classification_metrics` na CPU com `topk(5)`, `topk(10)`, argmax e rank ([4 passes sobre [N,C]](log.md:69)) | **CAUSA PRIMÁRIA — confirmada por 4 medições independentes** (§3) |
| H2 | Sincronização escondida do `.to("cpu")` além da aritmética | Instrumentado (log.md:72): remover o offload economizou 6.4 s de uma wall de 17.89 s cujo scoring era só 2.87 s → **o custo invisível (sync/serialização por batch) ≈ 1.2× o visível** | **Confirmada — contribuinte majoritário** |
| H3 | `MTL_CHUNK_VAL_METRIC=1` força CPU onde não precisa | `p1:111-117` (env força `_chunk_val` independente do tamanho); log.md:42,73 | **Confirmada** (agrava H1 nos estados pequenos) |
| H4 | Métrica de treino na CPU | p1 não computa métrica de treino (`p1:677-687`); no joint foi a doença de 06-24, já corrigida | **Refutada para o p1**; histórica no joint |
| H5 | `torch.compile` / recompilação | Modelo recompilado por fold (`p1:622-646`); fold 1 carrega warm-up (análogo joint: TX 26.3 min vs 21.2 em regime, log.md:47); sem o bump de cache havia fallback eager silencioso (~770 s/fold no H100, `p1:626-629`) | **Contribuinte secundário** — fases CPU longas no início de cada fold, não a alternância por época |
| H6 | Construção de dados/folds, parquet, SGKF | Uma vez por célula; minutos nos estados grandes | **Contribuinte menor** (fase única, não alternante) |
| H7 | Host-syncs no head (`.any()` etc.) | Removidos no fix P1 (`next_stan/head.py:287-298`, `next_stan_flow/head.py:142-151`) | **Refutada** (pós-fix) |
| H8 | Dataloader/H2D por batch | Dataset GPU-residente, `__getitems__` batched (`folds.py:250-257`) | **Refutada** |
| H9 | Checkpoint/logging/tqdm/`_update_per_metric_best` | JSON 1×/fold; p1 não tem tqdm; tracker é dict de floats | **Refutada** (desprezível) |
| H10 | Loop launch-bound (modelo 0.47 M) | Cat cell = 2.04× H100/A40 (teto de launch); reg pós-fix senta nesse teto; util 10-57 %, 1.8 GB VRAM; fan-out 5 folds → 100 % util (log.md:71,77-78) | **Confirmada como condição de fundo** — explica por que a GPU nunca passa de ~57 %, não explica os vales de ~0 % |
| H11 | Diagnóstico de ties | Versão antiga fazia `sort` completo toda época (~26 min/fold no TX antes de corrigir para `topk(11)`, 2.9 ms — log.md:59); gate antigo sobre-reportava 3 ordens de magnitude e **vetou o GPU-scoring indevidamente** (log.md:61,68) | **Contribuinte episódico** — e a razão histórica de o fix ter demorado |

---

## 3. Orçamento de fases (célula reg, A40, protocolo pré-`2c844974`)

Quatro medições independentes concordam sobre o tamanho de H1+H2:

1. **H100, célula AZ completa:** CPU+topk 240 s → GPU+rank 147 s ⇒ **~93 s (39 %) da
   célula era scoring CPU** (log.md:76, commit `2c844974`).
2. **H100 instrumentado, 1 fold × 10 épocas AZ:** 17.89 s → 11.45 s; scoring 2.87 s +
   ~3.5 s de sync/serialização (log.md:72).
3. **Contêiner 8-cores:** AZ reg 343 s vs 185 s na A40 — a única família mais LENTA em
   silício mais rápido, porque o gargalo era CPU (log.md:40,42; corrigido: com 32 threads
   no mesmo contêiner, 23 s vs 41 s a 8 threads — log.md:66).
4. **Microbench local desta investigação** (M4 Pro, 8 threads, caminhos reais de
   `tracking/metrics.py`, paridade 0.0e+00 entre os três caminhos):
   - AZ (N_val=100 448, C=1547): full-logit CPU **0.41 s/época → ~104 s/célula** (bate com o item 1);
     streamed-CPU 0.20 s/época; rank-derived 0.13 s/época.
   - CA (N_val≈150 000, C=8501): full-logit CPU **~3.2 s/época → ~800 s/célula** (a 8
     threads; na A40 com 32 threads ~2×-menos, mais o custo de sync do item 2).

**Linha do tempo por época (reg, pré-fix):** treino GPU (~0.2-0.4 s no AZ) → forward de
val GPU intercalado com D2H síncrono de [2048,C] por batch (49-75 syncs/época) → **fase
CPU pura de 0.3-3+ s** (cat + argmax + topk×2 + rank sobre [N_val,C]) → volta ao treino.
É exatamente o padrão observado: util de GPU amostrada 10/32/57/10 % com 1 779 MiB de
VRAM (log.md:71). Nos estados grandes a fase CPU cresce com N_val·C (CA/TX: a maior
fatia da célula), nos pequenos ela roda sem necessidade (H3).

| Fase | Onde | Frequência | Device | Sync? | Custo aprox. (A40) | Existe em cat/joint? |
|------|------|-----------|--------|-------|--------------------|---------------------|
| Build de dados + SGKF | p1:906-943 | 1×/célula | CPU | — | s→min (cresce c/ estado) | sim (equivalente) |
| Fatiar folds + H2D | p1:591; folds.py:237 | 2×/fold | CPU→GPU | sim | ~1-3 s | sim |
| `torch.compile` warm-up | p1:622-646 | por fold (pior no 1º) | CPU | — | dezenas de s/fold | sim (joint amortiza melhor) |
| Treino (fwd/bwd/step) | p1:677-687 | por batch | GPU | não | launch-bound (~50 % Python/launch) | sim, mas modelo do joint satura a GPU |
| Val forward | p1:788-794 | por batch de val | GPU | não | pequeno | sim |
| **D2H `[B,C]` por batch** | 82bca519:p1:706 | por batch de val | PCIe+sync | **sim** | ~1.2× o scoring (item 2) | **não** (joint: GPU; cat: irrelevante) |
| **Scoring da métrica** | 82bca519:p1:711-714 | 1×/época | **CPU** | — | AZ 0.3-0.4 s/ép; CA ~1.5-3 s/ép | **não** (joint: GPU S1/S2; cat: C=7) |
| `compute()`+best-tracker | p1:795,842 | 1×/época | misto | ~15 `.item()` | ms | sim |
| Checkpoint JSON | p1:1083 | 1×/fold | CPU | — | ms | sim |

---

## 4. Conclusão de causa-raiz

- **Primária:** o scoring de validação CPU do p1 — full-logit `[N_val, C]` movido ao
  host **batch a batch com sync**, depois 4 passes de CPU sobre o buffer. Guarda de OOM
  legítima para TX/CA (~20 GB) implementada do jeito caro (relocar em vez de streamar),
  e **forçada em todos os estados** pelo `MTL_CHUNK_VAL_METRIC=1` do `run_wave.sh:157`.
- **Secundárias:** (i) sync/serialização por batch do `.to("cpu")` (custa mais que a
  aritmética que motiva); (ii) recompilação por fold (fases CPU no início de fold);
  (iii) build de dados por célula; (iv) episodicamente, o diagnóstico de ties com `sort`
  completo (~26 min/fold no TX antes do fix).
- **Suspeitas refutadas:** dataloader/H2D de treino (dataset GPU-residente), host-syncs
  no head (removidos no fix P1), métrica de treino (não existe no p1), checkpoint/
  logging, `_update_per_metric_best`, GC.
- **Condição de fundo (não é a causa dos vales):** o loop é genuinamente launch-bound
  para um head de 0.47 M — teto medido ≈ 2× de A40→H100 (a célula cat, sem nenhum CPU
  scoring, dá exatamente 2.04×).

## 5. Antes vs depois de `2c844974`

**Antes (o que a A40 rodava, ≤`82bca519`):** alternância pronunciada por época; ~39 %
da célula AZ em CPU; CA/TX com fases CPU de segundos por época; célula reg mais lenta
em contêineres com poucos cores.

**Depois (streaming + `hits_from_rank` + `P1_STREAM_GPU=1` default):** o buffer [N,C]
não existe em nenhum device; hit@k = `rank ≤ k` (comparação inteira, idêntica CPU/CUDA,
`metrics.py:115-148,361-367`); certificado de ambiguidade medido a cada época
(`p1:777`, custo 1 pass de igualdade). Validado: célula AZ inteira 240→147 s, 5 folds
idênticos a 4 casas, pior delta 3.576e-08 (28× abaixo do quantum de 1e-6)
(log.md:76). `MTL_CHUNK_VAL_METRIC=1` vira no-op efetivo (seleciona só o caminho legado
não usado — `run_wave.sh:145-156`). **O que sobrevive de CPU:** build de dados por
célula, fatiamento+H2D e compile por fold, ~15 `.item()`/época, JSON por fold — nada
alternante por época. A célula fica então **launch-bound de verdade**: ela senta no
teto de 2× da família (log.md:78), com a solução estrutural sendo folds concorrentes,
não GPU maior.

## 6. Julgamento de engenharia (inerente / deliberado / acidental)

- **(a) Inerentes:** build de dados e SGKF por célula; fatiamento por fold; JSON por
  fold; parte do overhead de launch (modelo pequeno por definição do estudo).
- **(b) Trade-offs deliberados:** manter scoring CPU enquanto havia células bancadas
  CPU-scored (homogeneidade do pool n=20 — o revert deliberado em log.md:51);
  `num_workers=0` (RNG/reprodutibilidade, `folds.py:315-328`); compiled+sequential para
  os 9 cells restantes do board (log.md:81); a guarda de OOM em si.
- **(c) Acidentais/históricos:** implementar a guarda como *relocação* full-logit em vez
  de streaming GPU que o `mtl_eval` já tinha (reconhecido em log.md:54: "the better fix,
  deliberately deferred"); o blanket `MTL_CHUNK_VAL_METRIC=1` nos estados pequenos
  (log.md:73: "free win"); os 4 passes redundantes sobre [B,C] (top-5 ⊂ top-10, argmax =
  1ª coluna — log.md:69); contêiner com 8 cores para uma fase CPU-bound (log.md:40,66);
  o gate de ties defeituoso que vetou o GPU-scoring por um dia (log.md:68); o `sort`
  toda época (log.md:59).

## 7. Ranking de otimizações (avaliadas, NÃO implementadas)

Ordenadas por ganho esperado / risco de reprodutibilidade. "Bancados" = risco para os
números já registrados no board.

1. **Fan-out de folds em eager (`--only-fold k`, 5 processos):** H100 95 s vs 147 s
   sequencial; **byte-idêntico a 12 casas decimais** (RNG re-semeado por fold dentro de
   `_train_single_task`, `p1:581`) — log.md:79-80. Ganho ~2×, risco ~zero, bancados
   intactos. É o único lever que fura o teto launch-bound.
2. **Manter o default pós-`2c844974` (GPU + rank-derived):** 1.63× na célula; muda o
   device de scoring vs células bancadas → não bit-idêntico, mas certificado por época e
   ≤3.6e-08 (bem abaixo do quantum). Risco: só homogeneidade formal do pool.
3. **Retirar/escopar `MTL_CHUNK_VAL_METRIC=1` do `run_wave.sh`** (pendente — o script
   estava mid-run quando decidiram não editar, log.md:44): ~20 % nos estados pequenos
   mesmo sem mudar device. Byte-idêntico onde o auto-guard não dispararia.
4. **Fundir os 4 passes de scoring em 1 `topk(10)`** (1.73× da fase CPU, log.md:69):
   só relevante se o caminho CPU voltar; não incondicionalmente byte-idêntico (ties) —
   o gate corrigido é o certificado.
5. **Pular o gather inerte de `log_T` com α congelado em 0** (§1.1): remove ~3-4 passes
   [B,C]/batch de GPU + 289 MB de VRAM na CA; matematicamente `logits+0`, mas altera
   ordem de kernels sob `--compile` → dentro do ruído já aceito, ainda assim validar.
6. **Compiled fan-out:** 74 s (3.24× vs default antigo) mas drift ~1e-4 por contenção
   de compile (log.md:77) — para trabalho fora do board.
7. **Batch maior / CUDA graphs / overlap val-treino:** mudam semântica, consumo de RNG
   ou ordem de FP → **alterariam números bancados**; só num freeze boundary.
8. **Mais cores quando alugado:** paridade com a A40 a ~1.04× (log.md:66), mas
   economicamente perverso — CPU é o recurso mais caro do contêiner (log.md:67).

## 8. Avaliação launch-bound vs GPU-bound

A conclusão prévia ("família satura ~2×") **sobrevive ao teste, com a correção de que
ela só vale depois de remover o CPU scoring**: (i) VRAM 1 779 MiB/81 559 e util 10-57 %
(log.md:71); (ii) head ~0.47 M / ~30 GFLOP por batch → compute real sub-milissegundo,
~metade da wall é Python/launch; (iii) prova pelo sibling: cat = 2.04× A40→H100 sem
nenhum CPU scoring — esse é o teto; reg pré-fix ficava a 1.2× (o déficit de 0.84× ERA o
CPU scoring), pós-fix senta no teto (log.md:71,78). **Para tornar a célula GPU-bound:**
não adianta GPU maior; é preciso densidade de trabalho — 5 folds concorrentes levam a
util a 100 % (74-95 s vs 147 s) — ou fusão de launch (CUDA graphs/compile mode), que
esbarra em reprodutibilidade.

## 9-A. ADENDO 2026-08-10 (pós-investigação) — medições na própria A40 e ações tomadas

Executado nesta sessão, com a caixa livre:

1. **Fan-out eager validado NA A40 — byte-idêntico, mas SEM ganho de wall.**
   Célula AZ reg (v18, seed 0, eager, tf32, scoring GPU default): sequencial **227 s**
   vs fan-out 5× `--only-fold` **249 s**; os 5 folds idênticos a 0.000e+00 em todas as
   25 chaves headline (top10 a 12 casas). Motivo: **pós-`2c844974` o braço sequencial já
   roda a 96-99 % de utilização na A40** (mediana 99 %, p90 100 %) — não há GPU ociosa a
   preencher, e o fan-out ainda paga 5× o setup de dados por processo. **Correção ao §7:
   o fan-out é um lever de GPU-ociosa (H100: 147→95 s), não da A40 pós-fix.** A
   alternância CPU/GPU observada originalmente desapareceu na A40 com o default novo —
   confirmação in-situ do §5 (o experimento nº 1 do §9). Artefatos:
   `docs/studies/closing_data/v18/fanout_a40_test/` (na caixa).
2. **Skip do prior α·log_T inerte implementado** em `NextHeadStanFlow.forward` e
   `NextHeadStanFlowDualTower._apply_prior` (predicado = α congelado em 0.0, o mesmo de
   `_log_t_is_inert`, `mtl_cv.py:553-576`; kill-switch `MTL_SKIP_INERT_PRIOR=0`).
   Byte-idêntico por construção (`logits + 0.0·prior ≡ logits` para prior finito) e
   pinado por `tests/test_models/test_stan_flow_inert_prior.py` (5 testes; suíte de
   modelos 197/197). O mecanismo do prior é MANTIDO — o champion v11/BRACIS (α
   aprendível + log_T por fold) e o log_T-KD v12 ainda o usam.
3. **Eager sequencial (227 s) vs compiled sequencial bancado (185 s)** na mesma célula:
   o `--compile` vale ~1.23× na A40 — na A40 saturada, compile ainda paga; o fan-out não.
4. **A/B do skip do prior na A40 vs os números bancados do wave** (AZ s0, 4 braços reg +
   smoke do joint; artefatos em `docs/studies/closing_data/v18/inert_prior_ab/`):
   - **eager, skip ON vs OFF: 25/25 chaves exatas, 0.000e+00** — a mudança é
     byte-idêntica em GPU na célula real;
   - **joint (dualtower, fold 0 × 4 épocas, eager): 4776/4776 células numéricas exatas**;
   - **compiled skip OFF vs JSON bancado `v18_arizona_reg_s0`: 25/25 exatas, 0.000e+00**
     — um run fresco no protocolo bancado (compile+tf32 + scoring CPU legado via
     `P1_STREAM_GPU=0`) reproduz o wave publicável **bit a bit** (sessão de cache
     inductor quente da caixa); de quebra prova que a cadeia de refactor
     a9a2b80d..dafdc74d é bit-exata vs as células bancadas;
   - **compiled skip ON vs bancado: pior delta 1.494e-04** (fold0.top5_acc; top10 média
     59.4858 vs 59.4813) — NÃO é o skip errar a matemática (eager = 0.000e+00): remover
     o gather muda o grafo compilado → fusão/ordem de fp do inductor muda, o mesmo
     mecanismo do fix P1 do STAN, 20× abaixo da banda de ±0.3 pp que o protocolo já
     aceita para compile;
   - wall: eager 221 s (ON) vs 227 s (OFF) ≈ −2.7 %; compiled 169 vs 170 s (≈ nada na
     AZ — o ganho esperado cresce com C, CA/TX não medidos).
   **Consequência operacional:** para reproduzir células bancadas bit a bit, rodar com
   `MTL_SKIP_INERT_PRIOR=0`; para as células compiladas que faltam no board, a escolha
   conservadora é `=0` até o board fechar (homogeneidade bit-exata), ligando o skip como
   default depois.
5. **Probe TX (~5 min) pós-mudanças** (fold 0 × 5 épocas, eager, GPU-scoring + skip;
   artefatos em `docs/studies/closing_data/v18/tx_probe_5m/`): N=3 830 414, C=6553
   (val fold ≈ 766k). Build de dados só **24 s**; **18.8 s/época** em regime;
   **util GPU fora do build: média 95 %, mediana 99 %, apenas 4 % das amostras <20 %**
   — a alternância CPU/GPU sumiu também na maior cardinalidade do estudo, sem esperar
   pelo certificado de ties (medido em TX real: 0 avisos no probe). Pico de VRAM
   9 763 MiB (dataset residente). **ETA da célula completa (5×50): eager sequencial
   ≈ 79 min; compilada projetada ≈ 66 min (razão 1.23× da AZ + ~120 s de warmup) vs
   98 min do protocolo bancado → ~1.25–1.5×.** Fan-out em TX na A40 é inviável e inútil:
   GPU já a ~95 % e 5 cópias do dataset (~8.8 GB cada) não cabem nos 44 GB.

## 9. Menores experimentos para fechar incertezas restantes

1. **Confirmação in-situ na A40** (nada foi medido na A40 pós-flip): 1 fold × 10 épocas
   AZ com `P1_STREAM_GPU=1` vs `=0` + `nvidia-smi dmon`; esperado: vales de util
   desaparecem e wall cai ~1.3-1.6×.
2. **Medir a fase de compile por fold no p1** (`TORCH_LOGS=dynamo` ou timestamps):
   quantificar a fatia CPU de início de fold que sobra pós-flip.
3. **CA/TX: 1 época instrumentada** (o certificado de ties ainda não foi medido nas
   cardinalidades 6553/8501 com logits reais — a extrapolação AZ→TX é exatamente o que
   log.md:59 diz para não fazer).
4. **A/B do gather inerte de log_T** (α=0): wall e paridade eager numa AZ 1-fold.
5. **Fan-out eager na A40** (a validação byte-idêntica foi no H100): confirmar com 2-3
   folds concorrentes respeitando a RAM da caixa compartilhada.
