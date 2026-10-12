# scratch_ladder_mini — a escada inteira, em miniatura

**Descartável por construção.** Nada daqui é número de ninguém: 2 épocas e 2 folds não treinam
modelo nenhum, e o `science_fingerprint` das células é diferente do das reais por causa disso.

## A pergunta

`partitions = "pilot"` nunca **escalou** de verdade. Os testes cobrem `avalia()` com deltas
sintéticos; a validação em MPS de 25-08 rodou o piso e foi morta antes do degrau 2. O que ninguém
viu é o laço fechando: `_dispersao_interna` lendo os `result.json` que acabaram de sair, montando
`joint − dedicado` por tarefa, `avalia()` decidindo, `run_ladder` gerando o manifesto de P=3, e o
resume pulando as 6 células do piso em vez de retreiná-las.

Isso custa ~32 h para descobrir na campanha real e minutos aqui.

## O que observar no log, em ordem

1. `escada §2a: degrau 1/4, P=2 execuções` — o piso, com `(0,0)` e `(7,7)`;
2. seis células rodando;
3. **`alabama/cat: …` e `alabama/reg: …`** — a dispersão MEDIDA e o degrau decidido. Se estas linhas
   não aparecerem, o laço não fechou;
4. `escada §2a: degrau 2/4, P=3 execuções` — a escalada, obrigatória porque com P=2 há 1 grau de
   liberdade e o §2a proíbe parar aí;
5. **seis `skipped`** e três células novas em `(1,1)` — o resume reaproveitando o piso.

Um `SystemExit` com "nenhum delta pôde ser montado" ou "que o degrau exige" também é resultado
válido: é o fail-closed de `wave.py` funcionando, e diz exatamente o que faltou.

## Como rodar

```bash
export DATA_ROOT=/dados/poimtlnet/data
export ARTIFACTS_ROOT=/dados/poimtlnet/artifacts_final
export RUNS_ROOT=/dados/poimtlnet/runs
mtlcheck wave run studies/scratch_ladder_mini/waves/mini_alabama.toml
```

Apague o estudo inteiro depois. É o que "scratch" quer dizer.
