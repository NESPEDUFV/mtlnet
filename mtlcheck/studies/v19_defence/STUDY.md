# v19_defence — a vitrine do protocolo de avaliação

## Para que este estudo existe

**Ele não é o resultado da dissertação.** Os números que a dissertação escreve vieram do pipeline
anterior, sob o protocolo antigo — aquele sem conjunto de teste selado, cujas falhas estão
catalogadas em [`../../docs/v19_RECORD.md`](../../docs/v19_RECORD.md) e na auditoria que originou
tudo isto.

Este estudo é o **extra**: uma demonstração de que o protocolo de avaliação novo funciona e do que
ele produz. É por isso que ele foi refeito quando o protocolo mudou — uma vitrine que demonstra um
mecanismo descartado não demonstra coisa nenhuma.

## O que ele demonstra

A pergunta científica é a mesma da dissertação: **um modelo conjunto — uma rede, um forward, duas
tarefas — perde para modelos dedicados a cada tarefa?** Seis conjuntos, três braços (`joint`, `cat`,
`reg`), delta pareado do Acc@10 e do macro-F1.

O que muda é **como** se responde:

| | protocolo antigo | este |
|---|---|---|
| conjunto de teste | não havia — a época era escolhida nas mesmas observações que reportavam | 70/10/20 selado; a época sai da validação interna |
| quantas execuções | número fixo, herdado | a **escada do §2a** — cada conjunto mede a própria dispersão e escala |
| o estimando | condicional a uma partição | **marginal** sobre o sorteio de partição |
| quantas leituras | quantas se quisesse | **uma**, racionada por um livro que registra o gasto |

## Onde estamos — 2026-08-25

**Campanha nova, do zero.** A anterior está em
[`../archive/v19_defence_bridge/`](../archive/v19_defence_bridge/ARQUIVADO.md) — ela rodou sob a
**ponte de calibração**, que foi aposentada por não ter precedente publicado em ML e por medir o
regime errado. Nada dela é reaproveitado: as células antigas são todas de `split_seed = 0`, e só a
execução `(0,0)` seria reutilizável.

**Estado em 25-08:** Alabama e Istambul fechados, os dois resolvendo no teto (P=6); faltam Arizona,
Florida, California e Texas. 36 células, zero falhas, auditadas e declaradas bancáveis. A leitura
não aconteceu. Estado corrente e próximo comando: [`STATE.md`](STATE.md).

## ⚠ A ressalva que esta vitrine tem de carregar

**Alabama, Arizona e Istambul já foram lidos**, na campanha arquivada. Uma leitura nova sorteia
partições novas, e o `compare` a permite — mas **são os mesmos usuários**, e quem lê já sabe o que
procurar. É segunda olhada, e a contabilidade que importa é *quem foi medido*, não o hash da célula.

Florida, California e Texas **nunca foram lidos** e seguem limpos.

Onde a vitrine reportar os três primeiros, isso vai escrito. Numa demonstração de método a
afirmação é *"veja como o protocolo se comporta"* e não *"este é o efeito verdadeiro no Alabama"* —
o que torna a segunda olhada aceitável **declarada**, e só declarada.

## A escada, e o que esperar de cada conjunto

O manifesto declara o **piso** (2 execuções) e a escada decide o resto, medindo a dispersão na
validação interna — que não gasta leitura. Cada execução é um par `(split_seed, model_seed)` com os
dois botões sorteados juntos: `(0,0)`, `(7,7)`, `(1,1)`, `(100,100)`, …

Projeção a partir da campanha anterior — **planejamento, não medição**; a escada remede tudo no
próprio ciclo (protocolo §2a). O custo por execução da campanha anterior foi **medido na A40**; a
coluna nova é a placa que a substituiu:

| conjunto | por execução (A40) | por execução (RTX 6000 Ada) | razão | execuções esperadas | total |
|---|---:|---:|---:|---:|---:|
| alabama | 0,17 h | **0,14 h** | **1,21× medido** | 6 | 0,8 h |
| arizona | 0,34 h | 0,26 h | 1,3× suposto | 6 | 1,6 h |
| istanbul | 0,45 h | 0,32 h | 1,4× suposto | 4 | 1,3 h |
| florida | 2,24 h | **1,46 h** | **1,53× medido** | 4 | 5,8 h |
| california | 4,89 h | 3,20 h | 1,53× suposto | 3 | 9,6 h |
| texas | 6,33 h | 4,14 h | 1,53× suposto | 3 | 12,4 h |
| | *≈ 47 h* | | | | **≈ 32 h** |

⚠ **A GPU da `nespedgpu` foi trocada em 25-08** — saiu uma A40 (`sm_86`), entrou uma RTX 6000 Ada
Generation (`sm_89`), mesmos 46 GB. Dois conjuntos foram remedidos na placa nova, receitas `v19`,
`(0,0)`:

- **Alabama**, execução inteira: **504 s** contra 0,17 h na A40 — 1,21×.
- **Florida**, folds 1–2 dos três braços, extrapolados para 5: `cat` 189 s/fold, `reg` 75 s/fold,
  `joint` 770 s/fold, mais ~17 s de custo fixo por célula → **5 264 s = 1,46 h** contra 2,24 h — 1,53×.

**A razão cresce com o tamanho do conjunto, e é por isso que há duas colunas de suposição.** O
Alabama ganha menos porque o custo que não é fold — subir o processo, compilar, escrever predições —
não encolhe com a placa, e num conjunto de 90 s de fold ele é quase 20 % do total. Na Florida, com
folds de 189 a 800 s, esse custo fixo some no ruído e o ganho por fold aparece inteiro (`cat` 1,37×,
`reg` 2,3×, `joint` 1,42×). Califórnia e Texas são maiores que a Florida, então **1,53× é o piso
delas**, não o teto — as 32 h devem sobrar.

⚠ **Não paralelize para tentar reduzir isso.** Medido em 25-08: rodar duas a quatro células
concorrentes na mesma GPU é de 3 % a 9 % **mais lento** que enfileirar, porque uma única célula já
satura a placa. Tabela em [`../../docs/BEST_PRACTICES_NESPEDGPU.md`](../../docs/BEST_PRACTICES_NESPEDGPU.md) §5c.

Alabama primeiro, de propósito: é o mais barato e é onde o eixo de partição foi medido **maior**
(+0,37 pp em região, quase o tamanho de δ = 0,4). Se a escada escala até o teto em algum lugar, é
ali — e é ali que descobrir isso custa uma hora em vez de vinte.

## O contrato de leitura, que não mudou

Cada `mtlcheck compare` consome, **de uma vez e para sempre**, o teste externo de um conjunto.
`studies/READ_LEDGER.json` registra o gasto e sobrevive ao arquivamento — os 36 pares da campanha
anterior continuam lá.

**Nada de `compare` fora de `--dry-run` sem autorização explícita do autor.**

## Leia também

- [`STATE.md`](STATE.md) — o estado corrente e o próximo comando
- [`../../docs/plans/EVALUATION_PROTOCOL.md`](../../docs/plans/EVALUATION_PROTOCOL.md) §1 e §2a — o
  estimando marginal e a escada
- [`../../docs/future_works/banda_da_ponte_transfere.md`](../../docs/future_works/banda_da_ponte_transfere.md)
  — por que a ponte saiu, com a literatura
- [`../archive/v19_defence_bridge/ARQUIVADO.md`](../archive/v19_defence_bridge/ARQUIVADO.md) — o que
  a campanha anterior mediu e o que dela continua valendo
