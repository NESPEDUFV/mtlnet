# studies/ — workspaces de pesquisa isolados

Um estudo é uma pergunta com começo, meio e fim, conduzida por uma pessoa ou por um agente ao longo
de dias ou meses. Este diretório é o registro de estado deles.

Herdado do `docs/studies/` do repositório anterior, que funcionou muito bem para trabalho com
agentes — com um contrato novo que impede as duas patologias que ele desenvolveu.

## Registro

| Estudo | Pergunta | Status | Última atualização |
|---|---|---|---|
| [`v19_defence`](v19_defence/STATE.md) | Sob o protocolo de avaliação novo, o modelo conjunto perde para os dedicados? | **aberto — vivo**; a vitrine do protocolo, refeita do zero | 2026-08-25 |
| [`scratch_ladder_local`](scratch_ladder_local/STUDY.md) | A escada do §2a escala sozinha de ponta a ponta? | descartável — validação de máquina, sem número citável | 2026-08-25 |
| [`porting_validation`](porting_validation/STUDY.md) | O `mtlcheck` reproduz as conclusões do v18? | **fechando** — em paridade | 2026-08-19 |
| [`improvements`](improvements/STUDY.md) | O que melhorar agora que o porte está em paridade? | **aberto — trabalho vivo** | 2026-08-19 |
| [`root_migration`](root_migration/STUDY.md) | Como promover o `mtlcheck/` a raiz sem quebrar o que depende dos irmãos? | aberto — bloqueado por `improvements` | 2026-08-20 |

Log de desfechos entre estudos: [`log.md`](log.md).

**Arquivados.** [`archive/v19_defence_bridge`](archive/v19_defence_bridge/ARQUIVADO.md) — a campanha que rodou a ponte de calibração, aposentada em 25-08. Os 36 pares que ela gastou continuam gastos em `READ_LEDGER.json`; arquivar um estudo não devolve leitura.

## O contrato

Um estudo **pode** conter:

- prosa — `STUDY.md` (a pergunta e as referências congeladas), `STATE.md` (o que um agente que
  retoma precisa saber), `log.md` (achados datados, append-only);
- manifestos de wave — TOML declarativo: células como receita × estado × seed, com overrides;
- `status.json` — registro legível por máquina das células e seus run-ids;
- análise **read-only** — pode importar `mtlcheck` para ler resultados;
- `board/` — o registro científico commitado.

Um estudo **nunca** pode conter:

- laço de treino, código de modelo, de métrica ou de scoring;
- cópia de driver;
- import de torch/sklearn/lightning;
- script de shell como driver de experimento;
- arquivo acima de 1 MB.

Isso é verificado por `tests/test_studies_contract.py`, não por convenção. Os dois motivos estão no
cabeçalho daquele arquivo: um estudo do repo antigo manteve cópia própria do laço de época/validação
e ficou dois meses atrás dos fixes da biblioteca; outro manteve a matriz em 30+ drivers de shell, um
dos quais vazou um `export` entre células e mudou silenciosamente a precisão de oito resultados
bancados.

## Como parametrizar sem forkar

```bash
mtlcheck train --recipe recipes/v18/cat.toml --state alabama --seed 0 --set max_lr=0.005
mtlcheck wave run studies/<estudo>/waves/gate.toml
```

Se o estudo precisa de **comportamento** novo — não de um valor novo — ele entra em
`src/mtlcheck/` atrás de um campo de config, passa pelos testes de equivalência, e o estudo o
referencia por receita. Não há caminho em que um estudo edite o runner.

## Ciclo de vida

1. **Abrir** — copiar `_template/`, preencher `STUDY.md` com a pergunta e as referências congeladas
   (SHA do código, arquivos de receita, hashes dos manifestos de substrato), abrir linha no registro.
2. **Rodar** — as waves anexam células ao `status.json`; os artefatos vão para `runs/<estudo>/<cell-id>/`.
3. **Retomar** — um agente lê `STATE.md` e `status.json`. Quem encerra uma sessão atualiza os dois.
4. **Fechar** — escrever `CLOSURE.md`; promover as conclusões sobreviventes para `docs/CLAIMS.md`;
   `git mv` para `archive/`; apagar o bulk de `runs/<estudo>/` exceto as células citadas pelo board.

O que fica depois do fechamento: prosa, board e `status.json`. Quilobytes.
