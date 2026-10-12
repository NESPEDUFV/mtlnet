# scratch_ladder_local — a escada roda de verdade?

**Descartável por construção.** Nada daqui vira número de ninguém.

## A pergunta

`partitions = "pilot"` foi implementado, revisado e testado — e **nunca executou de ponta a ponta**.
Os testes cobrem a lógica do degrau com deltas sintéticos; o que ninguém viu é o laço real: rodar o
piso, ler a dispersão da validação interna das células que acabaram de terminar, decidir o degrau e
disparar as execuções seguintes sozinho.

Este estudo exercita esse laço no MacBook, no conjunto mais barato, antes de o A40 gastar hora nele.

## O que ele NÃO valida

**Os números.** MPS e CUDA não produzem os mesmos pesos, e o substrato daqui é outro substrato — foi
construído nesta máquina, não é o `696ac00419d287d3` do A40. Uma célula daqui não se compara, não se
agrega e não se cita.

⚠ É por isso que o manifesto usa `study = "scratch_ladder_local"` e não `v19_ladder`. O
`science_fingerprint` de uma célula **não inclui o device**: se estas células caíssem em
`runs/v19_ladder/`, o resume do A40 as veria prontas e pularia — e a vitrine sairia com folds
treinados num MacBook sem que nada no registro dissesse isso.

## O que ele valida

1. a escada escala sozinha, e o log diz o que ela mediu e decidiu em cada degrau;
2. o piso de 2 execuções sai como `(0,0)` e `(7,7)` — os dois botões juntos, não `(0,0)` e `(7,0)`;
3. `save_predictions` grava o fold externo, que é o insumo do `compare`;
4. o resume da wave reencontra o que já rodou.

## Como rodar

```bash
mtlcheck check2hgi build --recipe recipes/v19/substrate.toml --state alabama
mtlcheck wave run studies/scratch_ladder_local/waves/ladder_alabama.toml
```

## Desfecho

Registrado em [`STATE.md`](STATE.md). Quando a escada tiver rodado no A40, este estudo pode ser
apagado inteiro — é o que "scratch" quer dizer.
