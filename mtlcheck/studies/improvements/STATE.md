# Estado — improvements

**Última atualização:** 2026-08-21 · **PAUSADO** a favor da campanha `v19_defence` (defesa 28-08).

> 🔵 **Voltando a este estudo depois de um tempo? Leia [`RETOMADA.md`](RETOMADA.md) primeiro.**
> Ele tem a decisão aberta, o que existe no disco, como retomar, e uma dívida com prazo (duas flags
> de ablação no config central que precisam ser aposentadas quando a v20 decidir).

## Onde estamos

Triagem das três fontes **fechada**. Da Fase 1 rodou **só o fatorial A2 × A3**, em Alabama, uma
réplica, um sorteio de substrato — e é a réplica que falta que impede congelar. **Nada da v20 foi congelado e
nenhum default do código mudou**; a v19 continua sendo a versão de verdade.

## Feito

- [x] estudo criado, com a distinção contra o `porting_validation` escrita ([`STUDY.md`](STUDY.md))
- [x] cinco itens achados durante o porte, medidos onde barato
      ([`../porting_validation/IMPROVEMENTS_BACKLOG.md`](../porting_validation/IMPROVEMENTS_BACKLOG.md))
- [x] **triagem das três fontes fechada** → [`PLAN.md`](PLAN.md). ~30 DONE-BY-PORT · 10 OBSOLETE ·
      **7 IMPLEMENTATION** · 8 RESEARCH · 4 SUPERSEDED. Nada descartado em silêncio: toda ideia tem
      uma linha na tabela

## Feito (cont.)

- [x] **Fase 1 · fatorial A2 × A3 executado** (AL, 1 réplica, aninhado) →
      [`evidence/FASE1_FATORIAL_A2xA3.md`](evidence/FASE1_FATORIAL_A2xA3.md).
      **Região: nenhum dos três resolvido. Categoria: A2 e A3 reais, a combinação NÃO — e menor que
      qualquer um sozinho.** Candidato limpo: **A3 sozinho**. ⚠ falta a réplica de sementes/sorteios
      que o passo 2 pede, então **não congela nada**.
      Contém a correção de um erro de grandeza (piso de substrato × erro-padrão pareado) que passou
      por dois revisores e chegou a contaminar o `v19_defence/STUDY.md`.

## Próximo

Três passos, nesta ordem (detalhe e justificativa em [`PLAN.md`](PLAN.md)):

1. **A5 — política de retenção de checkpoint.** Sobe sozinha e **sem versão de receita**:
   `retain_checkpoints` está em `TELEMETRY_FIELDS` e o `science_digest` a remove, então ligar não
   invalida célula bancada nenhuma. Destrava a decomposição a1/b1/b2 do §8a.
2. **Wave de medição em Alabama.** ⚠ **PARCIAL.** O fatorial 2×2 rodou a **1 réplica e 1 sorteio de substrato**
   (resultado acima); falta a A1 a 4 réplicas e os **≥2 sorteios de substrato por braço** que o piso
   de 0,034 pp e o R16 exigem. Foi despriorizado em 21-08 a favor da campanha `v19_defence`, que tem
   prazo de defesa (28-08) — a GPU é o recurso disputado.
3. **Congelar a v20 = v19 + mae7 + o que sobreviver da wave.** Uma versão de receita, um rebuild de
   substrato em todos os estados, artefatos da v19 nunca sobrescritos.

⚠ Todo número da v20 é **coluna 3** do [`DIVERGENCE_REGISTER`](../../docs/DIVERGENCE_REGISTER.md):
a comparabilidade com a dissertação é quebrada por declaração.

## Bloqueios

⚠ ~~**DECISÃO DO AUTOR PENDENTE, com prazo**~~ — **RESOLVIDA por medição em 21-08**, ver abaixo e
`PLAN.md` §3.1. Era: sob qual objetivo construir os substratos de CA e TX. O `p2r_hard_neg_size_gate` tem default que **liga** o negativo
duro em todos os estados; a referência o **desliga** acima de 50 000 lugares, e FL/CA/TX estão
acima. Em AL/AZ/IST os dois objetivos coincidem, e é por isso que nunca apareceu.

⚠ **RESOLVIDO 2026-08-21 por medição** — ver `PLAN.md` §3.1. A Flórida foi construída nas duas
configurações e os quatro Δ ficaram dentro do erro-padrão e abaixo do piso de 0,034 pp: ligar ou
desligar o negativo duro num estado grande **não move nada mensurável**. Fica o objetivo único da
v19, declarado na receita.

⚠ E a premissa de urgência caiu junto: **CA e TX não são reserva intocada** — o batch size foi
buscado neles sob o protocolo antigo.

**Bloqueio corrente: nenhum técnico.** O estudo está pausado por prioridade (a GPU é do
`v19_defence` até a defesa), e a decisão de eixo da v20 é do autor — ver
[`RETOMADA.md`](RETOMADA.md) §2, que a enuncia com os números.

## O que já foi tentado e não funcionou

- Aplicar uma melhoria avulsa (`mae_poi_target_dim`) antes de ter a leva: exigiria uma v20 para um
  campo só, com v21/v22 vindo atrás.
