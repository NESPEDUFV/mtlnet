# A leitura — o procedimento

> **Este documento governa a ação irreversível do projeto.** Cada `mtlcheck compare` sem
> `--dry-run` consome, de uma vez e para sempre, o teste externo selado de um conjunto. Não há
> desfazer, não há segunda tentativa, e "rodar de novo com outro parâmetro" não existe.
>
> **Nada aqui roda sem autorização explícita do autor, por conjunto.**

## Antes de qualquer coisa: o estado tem de ser este

- [ ] os seis conjuntos fecharam, e cada um tem `runs/v19_ladder/ladder_<estado>.json` com
      desfecho `para` ou `teto` nas duas tarefas — nunca `incompleto`;
- [ ] `mtlcheck compare … --dry-run` passa em todos os seis (ver §Ensaio);
- [ ] a suíte passa na máquina onde a leitura vai rodar;
- [ ] o commit está limpo, e o hash dele vai no registro.

Se algum conjunto não fechou, **leia os que fecharam e deixe o resto para depois**. A escada fecha
por conjunto, e uma leitura parcial não contamina nada — o que não se pode é ler um conjunto duas
vezes.

## O ensaio, que não gasta nada

```bash
cd /dados/poimtlnet/mtlcheck
export DATA_ROOT=/dados/poimtlnet/data ARTIFACTS_ROOT=/dados/poimtlnet/artifacts_final \
       RUNS_ROOT=/dados/poimtlnet/runs PYTHONPATH=src

for e in alabama arizona istanbul florida california texas; do
  echo "═══ $e"
  ~/.venv/bin/python -m mtlcheck.cli compare /dados/poimtlnet/runs/v19_ladder \
      --analysis recipes/analysis/v19_ladder.toml --state "$e" --dry-run 2>&1 | tail -9
done
```

Confirmado no código: `_dry_run` retorna **antes** de qualquer escrita no livro, e `_record_reads` só
é chamado no caminho real. Ensaie à vontade.

**O que tem de aparecer em cada um**, e o que cada linha significa:

| linha | o que ela garante |
|---|---|
| `receita … (56547de73f015cdc)` | a receita congelada certa — se o fingerprint diferir, **pare** |
| `partições N, uma por execução` | o desenho marginal; N tem de ser o P do `ladder_<estado>.json` |
| `réplicas [...] · N linhas` por braço | os três braços com as MESMAS execuções |
| `train_labels {...}` | o canário do §1 tem o que precisa, por tarefa e fold |
| `canário §1 … não disparou` | sem vazamento de rótulo de região entre treino e teste |
| `escada §2a P=N execuções [...]` | o gate reconheceu o degrau, e ele resolve |
| `TODAS AS GUARDAS PASSAM` | as sete |

## A leitura

**Uma invocação por conjunto**, sem `--dry-run`:

```bash
~/.venv/bin/python -m mtlcheck.cli compare /dados/poimtlnet/runs/v19_ladder \
    --analysis recipes/analysis/v19_ladder.toml --state <conjunto> --json > leitura/<conjunto>.json
```

Ela lê a **família manchete inteira do conjunto numa vez** — as duas tarefas, com Holm entre elas e
a co-primária. Isso não é conveniência: a correção de multiplicidade só significa alguma coisa
relativa ao conjunto que **poderia** ter sido reportado, e ler tarefa por tarefa destruiria isso.

**Depois de cada uma, imediatamente:**

1. **confira o livro.** A leitura tem de ter entrado:
   ```bash
   python3 -c "
   import json
   livro = json.load(open('studies/READ_LEDGER.json'))
   novas = [r for r in livro if r['study'] == 'v19_ladder']
   print(f'{len(novas)} leituras de v19_ladder')
   for r in sorted(novas, key=lambda x: (x['state'], x['fingerprint'])):
       print(' ', r['state'], r['fingerprint'][:12], r['on'])
   "
   ```
   Devem ser **3 por conjunto** (um fingerprint por braço), e o próprio `compare` levanta se algum
   braço não entrar — com a mensagem em maiúsculas mandando registrar à mão. Se isso acontecer,
   **registre antes de qualquer outra coisa**: o teste está gasto e o registro é a única coisa que
   ainda pode ser salva.

2. **commite o livro.** Ele é versionado de propósito: uma leitura tem de aparecer como um commit
   datado.

⚠ **O `compare` vai AVISAR, em AL, AZ e IST, que aquele par já foi lido em 24-08 pela campanha da
ponte.** Isso é correto e esperado — a receita de treino não mudou, então o `science_fingerprint` é o
mesmo. O aviso existe para que a ressalva não se perca, e ela tem de aparecer onde o número for
reportado: **é segunda olhada nos mesmos usuários.** Ver [`STUDY.md`](STUDY.md).

## Depois dos seis: a camada cross-state

```bash
~/.venv/bin/python -m mtlcheck.cli conjunction leitura/*.json
```

⚠ **A precondição do §4a rodou em 23-08 e REPROVOU**: 24,5 % dos usuários aparecem em mais de um
estado americano, e Istambul é o único conjunto genuinamente independente. Por isso o combinador é
**Bonferroni** e não Simes — está na receita, e não é escolha desta sessão: é o ramo que a precondição
disparou. Ver [`../archive/v19_defence_bridge/S4A_USER_OVERLAP.md`](../archive/v19_defence_bridge/S4A_USER_OVERLAP.md).

## Como ler o que sai

**Dois intervalos, e eles respondem perguntas diferentes.** Qual é a manchete foi decidido antes de
qualquer leitura, que é o único momento em que a escolha não é enviesada pelo resultado:

* **manchete** — o bootstrap por usuário do §3, com as execuções promediadas dentro de cada réplica.
  É o pré-registrado, e ele **não** encolhe com P;
* **eixo de execução (§10.2)** — `t₀.₉₇₅,P−₁ · s / √P` sobre os deltas por execução. É a única
  quantidade que P encolhe, e é o que as execuções extras compraram. Responde ao revisor que
  perguntar *"seu delta se moveria sob outra divisão dos usuários?"*.

E o **δ crítico** por tarefa: a margem a partir da qual o veredito mudaria. É mais informativo que o
veredito sozinho, porque diz de quanto foi.

## O que a leitura NÃO autoriza

- **reler.** Nem com outra receita, nem "só para conferir";
- **escolher a manchete depois de ver as duas.** Já foi escolhida;
- **afirmar sensibilidade à partição a partir de um carimbo `partition-limited`** — ele diz "não
  resolveu nesta margem pelo proxy interno". Ver §2a e
  [`../../docs/future_works/escada_mede_o_ruido_do_medidor.md`](../../docs/future_works/escada_mede_o_ruido_do_medidor.md);
- **comparar estes números com os do v18 ou com os da dissertação.** `eval_stream` diferente,
  protocolo diferente. Ver [`../../docs/QUAL_CONJUNTO_USAR.md`](../../docs/QUAL_CONJUNTO_USAR.md).
