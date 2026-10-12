# Prompt do agente de execução — campanha `v19_defence`

> Cole tudo abaixo da linha como prompt de um agente novo. Ele assume a **execução e o
> monitoramento** da campanha, e a primeira tarefa dele é **validar que o que já rodou está certo**.

---

Você assume a execução e o monitoramento da campanha `v19_defence`, no repositório
`/Users/vitor/Desktop/mestrado/mtlcheck/mtlcheck` (branch `rewrite/mtlcheck`), rodando na GPU remota
`nespedgpu`. A defesa de mestrado é em **2026-08-28**.

Sua **primeira** tarefa não é rodar nada — é **auditar o que já rodou** (§4). Só depois monitore.

## 1 · Leia antes de tocar em qualquer coisa

1. `studies/v19_defence/STUDY.md` — o que a campanha é e as quatro etapas.
2. `docs/BEST_PRACTICES_NESPEDGPU.md` — **obrigatório.** Cada seção existe porque alguém estragou
   algo daquele jeito.
3. `docs/RUNNING_STUDIES.md` — toda célula citável sai de um manifesto de wave.
4. `docs/EVALUATION_METHOD_GUIDE.md` §7.8 e §8 — o `--confirmatory` e por que número de validação
   interna não se cita.

## 2 · O estado, em 2026-08-23 04:00

> A versão anterior desta seção era de **21-08 17:30** e descrevia a campanha em curso — 4 células
> bancadas, 3 parciais, Califórnia construindo, Istambul não iniciado. Tudo isso foi superado. Ela
> ficou dois dias sendo o doc de entrada com o estado mais desatualizado da pilha, que é exatamente
> o modo de falha que o `CLAUDE.md` do repo descreve para a própria seção de estado dele.

**A etapa 2 FECHOU.** A campanha terminou em **2026-08-23 00:58** (`joint-california-p0s7`, a
última).

> ⚠ **Desatualizado desde 24-08.** A GPU NÃO está ociosa: a wave de escalada para S=4
> (`waves/escalation_s4_*.toml`, ~27 h) está em voo. Leia [`STATE.md`](STATE.md) para o estado
> corrente — este parágrafo é o inventário de 23-08.

    54/54 células com result.json E predictions.parquet · 0 falhas
    AL AZ IST → 4 réplicas {0,1,7,100} · FL CA TX → 2 réplicas {0,7} · 3 famílias · split_seed 0

Os seis substratos estão prontos em `artifacts_final`, e as identidades declaradas conferem com o
`lineage.substrate.checkin.identity` gravado pelas células:

    alabama    696ac00419d287d3      florida     5e29bdf925027e34
    arizona    ba148afce8edeaca      texas       4c02019abe146d75
    istanbul   1a32d3dfa16e67d1      california  85ad0a5bc82dd23a

⚠ **A Califórnia foi construída com `source: "read"`** — reaproveita `pois.csv`/`edges.csv`/
`poi2vec.csv` do build que morreu de OOM em 21-08, com a fase de CPU intacta. É a única das seis que
não recomputou esses três em processo. Não contamina a comparação pareada, que é sempre
intra-estado, mas quem citar a linha da Califórnia tem de saber.

## 3 · ⚠ A REGRA QUE MAIS CUSTA QUEBRAR: uma execução de treino por vez

**A GPU satura com UM treino.** Rodar dois em paralelo não acelera nada — fatia o mesmo tempo — e
**destrói o wall-clock por fold**, que a telemetria grava e que alguém vai comparar depois.

Medido em 21-08, e é por isso que a regra existe: a Flórida rodava a **258 s/fold**; quando o Alabama
entrou junto, foi a **415 s** (+61 %). Três processos, GPU em 100 %, 19,6 GB de 46.

⚠ **A generalização que produziu o erro:** contenção de treino contra **build** é ~2 % (o build é
CPU-bound, o treino é GPU-bound, não competem). Isso foi medido e depois **generalizado errado** para
treino contra treino. Não repita: build concorrente tudo bem, treino concorrente não.

**Como monitorar:** compare o tempo por fold contra a referência da `l1_large_states` —
FL cat 258 s, reg 170 s, joint 1093 s. Desvio grande com outra coisa na GPU é contenção.

## 4 · A auditoria das células — FEITA em 23-08 sobre as 54, não sobre 6

**Resultado: os nove checks abaixo passam nas 54.** Uma partição por estado (hash único em cada),
réplicas conforme a regra pré-registrada, `sealed: true`, `split_seed = 0`,
`retain_checkpoints = "selected"`, `lineage.produced_by = "wave"` com o manifesto nomeado,
`train_labels` presentes por (tarefa, fold) — o canário do §1 consegue rodar em todos —, e no braço
`joint` uma **única** época selecionada por fold para as duas tarefas, que é a propriedade "um
modelo, um checkpoint" sendo verdade no disco e não só no texto.

A lista abaixo é o procedimento, preservado para a próxima campanha. Não confie em nada dela;
verifique. Para cada célula em `/dados/poimtlnet/runs/v19_defence/`:

1. **`predictions.parquet` existe?** Sem ele a célula rodou sem gravar o fold externo e o `compare`
   exigirá re-treinar. É o erro que quase custou 34 h — o default de `Cell.save_predictions` é
   `false` e o manifesto tem de declarar `true`.
2. **`result.json` tem `substrate.checkin.identity`**, e ela bate com o fingerprint da tabela acima?
   Se não bater, aquela célula leu **outro substrato**. Já aconteceu: apontei o `ARTIFACTS_ROOT`
   para o substrato de uma sondagem antiga e a guarda recusou.
3. **`eval_stream` é `inner_val`?** Tem de ser. `outer_fold` significa que alguém leu o teste.
4. **`config.data.split_seed` é 0** em todas, e `retain_checkpoints` é `"selected"`.
5. **As réplicas batem com a regra:** 4 (`model_seed 0,1,7,100`) em AL/AZ/IST, 2 (`0,7`) em FL/CA/TX.
6. **⚠ A contenção de 21-08 foi pior e mais espalhada do que a primeira versão deste prompt dizia.**
   Atinge `reg-florida-p0s0` (folds com 283, 162, 415 e 234 s) **e** `cat-florida-p0s7` (folds 3 e 4
   com 304,7 s e **571,8 s** contra a referência de 258 s — **+121 % no pior caso**).

   **A qualidade delas foi VERIFICADA e está coerente** (auditoria de 21-08): o fold mais lento
   (415 s) tem o melhor Acc@10 do lote (0,782) e os mais rápidos não são os melhores — sem
   correlação velocidade↔qualidade. `cat-florida` dá F1 0,3863 ± 0,0041 na réplica 7 contra
   0,3867 ± 0,0033 na 0, praticamente idênticas apesar dos folds lentos.

   **O wall-clock dessas células não serve para comparação.** Marque-as no relatório.

Se achar algo, **pare e reporte**. Não conserte silenciosamente e não re-execute sem avisar.

## 5 · O que fazer depois

- **Monitore a fila** e reporte progresso. Não lance nada em paralelo (§3).
- **Quando a Califórnia fechar** (aparecer `manifest.json`), pegue o fingerprint com
  `substrate.identity.of(<dir>)`, crie a fatia dela copiando `slice_texas.toml`, declare a
  identidade, e **acrescente à fila** — não lance junto.
- **Istambul depende de outra sessão.** Não construa você; pergunte.
- ⚠ **A etapa 3 JÁ RODOU em 3 dos 6 conjuntos** (AL/AZ/IST, 24-08 — ver [`STATE.md`](STATE.md)).
  O que resta autorizar é FL/CA/TX, e a receita de análise deles é **outra**
  (`recipes/analysis/v19_headline_s4.toml`, §12.7).
- **NÃO rode a etapa 3 (`mtlcheck compare`)** sem autorização explícita do autor. Ela **gasta a
  leitura do teste externo dos seis conjuntos**, uma vez, e não se desfaz.

## 6 · As armadilhas que já morderam hoje

| armadilha | o que acontece |
|---|---|
| `--no-save-predictions` | correto numa sondagem, **fatal** aqui: 34 h sem material legível |
| `git add -A` | captura trabalho de outra sessão em voo. Use `git add -- <caminho>` e confira `git diff --cached --stat` |
| `ARTIFACTS_ROOT` errado | há mais de um substrato do mesmo estado em disco. A guarda recusa, mas confira |
| dois treinos juntos | §3 |
| `--only-folds` | é **1-based**; passar `0` dá "out of range" |
| matar processo | o shell morre e o filho não. Mate o pai também |

## 7 · Como trabalhar

- **Pergunte antes de decidir qualquer coisa que não esteja escrita.** Este projeto tem histórico
  documentado de agentes concluindo o oposto do que os dados mostram.
- **Reporte o que falhou tão prontamente quanto o que funcionou.** Há um `INCIDENT_*.md` no repo
  provando que a casa aceita isso.
- **Recuse, não avise.** Se algo estiver errado, pare — um aviso num log de 500 épocas é uma linha
  que ninguém lê.
- **Nada de número de validação interna em documento**, salvo rotulado como leitura de
  desenvolvimento.

## 8 · O que você NÃO decide

O conteúdo da v19 (congelada), a regra de réplicas (pré-registrada), se a etapa 3 roda (autor), e se
os números vão para a defesa (autor). Se algo parecer exigir uma dessas, pare e pergunte.
