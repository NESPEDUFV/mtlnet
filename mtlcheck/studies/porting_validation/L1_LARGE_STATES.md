# L1 — o harness aguenta a escala? 2026-08-18

> **Sim.** 9 células (3 famílias × FL/CA/TX), 1 fold, 1 réplica, 2 h 45 min, **0 falhas, 0 batches
> não-finitos**. Dados: `runs/l1_large_states/`. Manifesto: `waves/l1_large_states.toml`.
>
> ⚠ **Isto não é um resultado científico.** É viabilidade. As métricas abaixo vêm da **validação
> interna** de **um** fold e de **uma** réplica — não são números de teste externo, não têm banda, e
> não devem ser citados como desempenho.

## O que esta wave NÃO gastou

Rodou **sem `--save-predictions`**. Sob `inner_validation` o runner só toca o fold externo para
capturar linhas, então **nenhuma leitura selada foi consumida**. ⚠ CORRIGIDO 2026-08-21: CA e TX NÃO são reserva intocada (batch size buscado neles sob o protocolo
antigo). O que segue foi escrito supondo que eram. CA e TX seriam a reserva confirmatória
inteira (§9.4); trocá-las por um teste de viabilidade seria gastar a evidência mais forte da
dissertação no exame mais barato.

## O que foi medido

| célula | janelas | classes reg | s/fold | pico GB | métrica interna |
|---|---:|---:|---:|---:|---:|
| cat/florida | 1 274 418 | — | 258 | 5,58 | 38,74 |
| cat/california | 2 925 466 | — | 599 | 9,14 | 36,02 |
| cat/texas | 3 830 414 | — | 783 | 11,10 | 36,61 |
| reg/florida | 1 274 418 | 4 703 | 170 | 3,16 | 76,52 |
| reg/california | 2 925 466 | 8 501 | 413 | 6,86 | 62,86 |
| reg/texas | 3 830 414 | 6 553 | 522 | 8,76 | 63,97 |
| joint/florida | 1 274 418 | 4 703 | 1 093 | 25,41 | — |
| joint/california | 2 925 466 | 8 501 | 2 504 | 33,02 | — |
| **joint/texas** | 3 830 414 | 6 553 | **3 244** | **36,69** | — |

`joint` não banca escalar único: são duas métricas, e o `score` as separa em `joint:cat`/`joint:reg`.

## As três coisas que isto fecha

**1 · A memória cabe, com folga conhecida.** O pico é `joint/texas` a **36,69 GB de 46**. O sistema
antigo acreditou por dois anos que região-MTL não cabia num A40 — e a causa era uma métrica por época
acumulando logits O(N·C), não o modelo. Aqui a família mais pesada roda a 80 % da placa sem
intervenção. **Esse é o teto real da máquina para o `joint`:** sobra ~9 GB, então não há espaço para
uma quarta família nem para dobrar o batch em TX.

**2 · Nenhum batch não-finito, em nenhuma célula.** O colapso fp16 que custou uma re-baseline inteira
na referência não tem análogo aqui — e agora existe um contador que o diria, em vez de uma
re-execução instrumentada depois do fato.

**3 · O cosseno em cinco estados.** A sonda entregou de graça o que a referência nunca conseguiu:

| estado | cosseno médio |
|---|---:|
| alabama | +0,001222 |
| arizona | +0,000966 |
| istanbul | +0,000396 |
| **florida** | **−0,000215** |
| **california** | **+0,000212** |
| **texas** | **+0,002223** |

Referência: +0,001, sd ≈ 0,012. **Os seis estados reproduzem**, e nenhum sai de ±0,0023 — bem dentro
de um desvio. A pergunta **U4** ("e o cosseno em CA/TX?"), registrada na dissertação como
permanentemente sem resposta por falta deste campo, **está respondida**: +0,000212 e +0,002223.

⚠ Continua sendo o cosseno **de minibatch**. Se é ortogonalidade real ou atenuação por ruído, só a
curva de acumulação (T6) separa — e T6 depende de retenção de checkpoint.

## Custo, para planejar

`joint/texas` a **54 min por fold** significa **~4,5 h para os 5 folds** de uma única réplica. Uma
wave confirmatória de TX (3 famílias × 4 réplicas × 5 folds) é da ordem de **dias**, não de horas.
Qualquer plano que trate TX como "mais um estado" está errado por uma ordem de grandeza.
