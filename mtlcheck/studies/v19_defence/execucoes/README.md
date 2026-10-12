# Os artefatos das 81 células — registro histórico

O que a campanha `v19_ladder` produziu, guardado aqui porque `runs/` não é versionado e estes
números são o registro científico da defesa.

| arquivo | o que é |
|---|---|
| `ladder_<estado>.json` | o veredito da escada por conjunto: δ, execuções, `sd`/UCL/meia-largura e desfecho por tarefa. É o que o `assert_ladder` exige na leitura |
| `<braço>-<estado>-p<S>s<M>/result.json` | o registro por célula: config resolvida, `science_fingerprint`, substrato, os 5 folds com época selecionada, métricas de validação **interna**, e a telemetria de gradiente do braço conjunto |
| `<braço>-<estado>-p<S>s<M>/report.md` | o mesmo, legível |

## O que NÃO está aqui, e por quê

- **`predictions.parquet` (6,5 GB)** — as linhas do fold externo selado. Ficam no servidor. São o
  insumo do `compare`, e a leitura já aconteceu: os vereditos estão em [`../leitura/`](../leitura/).
- **`checkpoints/` (3,4 GB)** — pesos. Regeneráveis pela receita mais a semente.
- **`folds/*.csv`** — a série por época. Fica no servidor; o essencial dela já está no `result.json`.

## ⚠ Estes números são de validação INTERNA

Tudo em `result.json` e `report.md` é a lane que escolhe a época — **não é resultado**. O resultado
da campanha são os seis payloads em [`../leitura/`](../leitura/), que saíram do teste externo selado,
lido uma vez. Confundir os dois é o erro que o
[`docs/QUAL_CONJUNTO_USAR.md`](../../../docs/QUAL_CONJUNTO_USAR.md) existe para desfazer.

## A telemetria de gradiente

As células `joint-*` carregam, em `folds[].diagnostics`, o cosseno entre os gradientes das duas
tarefas sobre os parâmetros compartilhados e a norma de cada um, por grupo do tronco (`cross_ab`,
`cross_ba`, `ffn_a`, `ffn_b`, `final_ln`, `norms`). É a medição que sustenta a seção de mecanismo do
[`../ACHADOS.md`](../ACHADOS.md).
