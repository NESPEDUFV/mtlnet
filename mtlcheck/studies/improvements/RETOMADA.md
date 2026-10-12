# Retomada — leia isto primeiro se você está voltando à v20 depois de meses

**Escrito 2026-08-21**, quando o estudo foi pausado a favor da campanha `v19_defence` (defesa 28-08).
Existe porque quem retomar não vai ter nada disto na cabeça.

## 1 · Onde o estudo parou, em um parágrafo

A triagem das três fontes está **fechada** (`PLAN.md`): 7 itens IMPLEMENTATION, 8 RESEARCH, o resto
DONE-BY-PORT ou OBSOLETE. Da Fase 1 rodou **só o fatorial A2 × A3**, em **Alabama, uma réplica, um
sorteio de substrato** — e é justamente a réplica que falta que impede qualquer congelamento. Nada da
v20 foi congelado, nenhum default do código foi mudado, e a v19 continua sendo a versão de verdade.

## 2 · A decisão aberta, dita com precisão

> **Quais correções entram na v20 — A3 sozinho, A2 + A3, ou nenhuma?**

O que a medição diz ([`evidence/FASE1_FATORIAL_A2xA3.md`](evidence/FASE1_FATORIAL_A2xA3.md)):

* **Em região, nenhum dos três braços é resolvido** — todos abaixo de 1,25 erro-padrão. A região não
  decide nada.
* **Em categoria, A2 (+0,141) e A3 (+0,170) são reais** (2,4 e 3,0 ep). **A combinação (+0,116) não
  é** (1,07 ep), e é **menor que qualquer um sozinho** — os dois interferem, não compõem.
* Portanto o eixo da decisão é **categoria**, e o candidato limpo é **A3 sozinho**.

⚠ **Isto NÃO é suficiente para congelar.** Uma réplica, um estado, com erros-padrão de 0,06 a 0,18:
quatro réplicas podem virar qualquer um dos três do avesso. O passo 2 do [`STATE.md`](STATE.md) pede
**≥ 2 sorteios de substrato por braço** e isso **não foi feito**.

## 3 · ⚠ Duas flags de ablação estão no config central, e têm prazo

`src/mtlcheck/config.py` carrega **`fix_unit_mismatch`** e **`symmetrise_poi2vec`**, ambas default
`False`, atravessando `substrate/pipeline.py` e `substrate/delaunay.py`/`poi2vec.py`.

**Elas são andaime de decisão, não estado permanente.** O compromisso assumido com o autor em
2026-08-21, e a razão dele:

> Quando a v20 decidir, **o braço vencedor vira comportamento sem flag e o perdedor é deletado.**
> Nenhuma das duas fica default-off para sempre.

O motivo é concreto: foi exatamente assim que o `src/` do repositório de referência ficou impossível
de navegar — cada flag temporária que sobreviveu à sua decisão. Se você está lendo isto e as duas
ainda existem, **essa é uma dívida em aberto, não um projeto de design.**

## 4 · O que existe no disco (A40) e o que dá para reaproveitar

Substratos, em `/dados/poimtlnet/artifacts_final/substrate/`:

| engine | estados | o que é |
|---|---|---|
| `check2hgi_v18` | AL AZ FL CA IST TX | **a v19** — a base. Não sobrescreva |
| `check2hgi_a2` | alabama | braço A2 do fatorial |
| `check2hgi_a3` | alabama | braço A3 |
| `check2hgi_a2a3` | alabama | braço combinado |
| `check2hgi_mae7` | alabama | `mae_poi_target_dim = 7` |

Execuções, em `/dados/poimtlnet/runs/`: `final_al` (3 células, a base), `factorial_a2`,
`factorial_a3`, `factorial_a2a3` (2 células cada — `cat` e `reg`).

⚠ **Confira a idade e a proveniência antes de confiar.** Todos são de 20–21/08 e foram construídos
com o código daquela data. Se o `substrate/` mudou desde então, o `identity.of()` de cada um vai
divergir dos manifestos — e é para isso que ele existe. **Um substrato cujo código produtor não está
mais na árvore não serve para congelar nada** (aconteceu com Istambul em 21-08; a saída foi
reconstruir num diretório à parte e comparar os fingerprints).

## 5 · Como retomar, concretamente

```bash
# 1. os manifestos do fatorial ja existem
ls studies/improvements/waves/          # factorial_a2, factorial_a3, factorial_a2a3

# 2. o que falta e replicar. Edite `seeds` nos tres + a base, e varie o sorteio de substrato
#    (`repr_seed` na receita do braco) — sao DOIS eixos distintos, ver NOMENCLATURE.md §1

# 3. rode (na A40, uma wave de cada vez — ver docs/BEST_PRACTICES_NESPEDGPU.md)
PYTHONPATH=src python -m mtlcheck.cli wave run studies/improvements/waves/factorial_a3.toml
```

⚠ **Antes de qualquer execução longa, leia [`../../docs/BEST_PRACTICES_NESPEDGPU.md`](../../docs/BEST_PRACTICES_NESPEDGPU.md)**
— principalmente §5 (dois POI2Vec simultâneos dividem os núcleos pela metade) e §5b (build e treino
competem por memória de GPU; um build grande **não cabe** ao lado de uma campanha). Os dois erros
custaram mais de duas horas num único dia.

## 6 · O que mudaria a conclusão

* **Réplicas.** É o que falta e é o que mais importa. Com ep de 0,06 a 0,18, quatro réplicas decidem.
* **Outro estado.** Tudo aqui é Alabama. Um estado grande pode inverter — já aconteceu no programa:
  o `design_k` foi descartado por um estudo AL/AZ e a Flórida o reabilitou.
* **A base de comparação.** O fatorial foi medido contra `final_al`. Se a v19 congelada da campanha
  `v19_defence` for a nova referência, **a base muda** e os Δ têm de ser recalculados contra ela.

## 7 · Onde mais olhar

| | |
|---|---|
| [`PLAN.md`](PLAN.md) | a triagem completa — toda ideia tem uma linha, nada foi descartado em silêncio |
| [`STATE.md`](STATE.md) | o estado corrente e os passos na ordem |
| [`STUDY.md`](STUDY.md) | por que este estudo é separado do `porting_validation` |
| [`evidence/FASE1_FATORIAL_A2xA3.md`](evidence/FASE1_FATORIAL_A2xA3.md) | os números, e a correção de um erro de grandeza que passou por dois revisores |
| [`../../docs/DIVERGENCE_REGISTER.md`](../../docs/DIVERGENCE_REGISTER.md) | ⚠ **todo número da v20 é coluna 3**: a comparabilidade com a dissertação é quebrada por declaração |
| [`../v19_defence/`](../v19_defence/) | a campanha que tem prioridade sobre este estudo |
