# Backlog — o que falta, por que ainda não foi feito, e o que desbloqueia

> Atualizado 2026-08-17. Existe para que nada dependa de memória de conversa. Cada item diz **por que
> está aberto**, porque "adiado por decisão" e "não chegamos lá" exigem respostas diferentes.
>
> Fases e evidência: [`PLAN.md`](PLAN.md). Estado do dia: [`STATUS_2026-08-16.md`](STATUS_2026-08-16.md).
> Achados de review ainda abertos: [`REVIEW_LEDGER_2026-08-16.md`](REVIEW_LEDGER_2026-08-16.md).

## 1 · Decisões do autor — custo zero, bloqueiam adoção

| # | Item | Evidência | Recomendação |
|---|---|---|---|
| D1 | Adotar categoria @20 épocas em Alabama | +0,354 ± 0,095 pp, 7× o piso de ruído ([GATES](GATES_2026-08-17.md) §1) | adotar — é ganho de qualidade |
| D2 | Adotar joint @30 ou @35 épocas | 8 comparações, nenhuma negativa; 60 % / 69 % do wall (§2) | adotar 30 pelo custo, 35 se preferir conservador |
| D3 | Assimetria de tuning STL × joint | consequência de D1: mover o teto STL de AL em +0,35 pp | decidir junto com D1 |

**D3 não é detalhe.** Se a categoria dedicada de AL for tunada e o joint não, a comparação principal
vira STL-tunado contra joint-não-tunado. Ou os dois recebem a mesma consideração de schedule, ou a
diferença de orçamento entra por escrito.

## 2 · Execução longa — adiada por custo, não por dúvida

| # | Item | Custo | Pré-requisito |
|---|---|---|---|
| L1 | Validação FL/CA/TX (3 famílias × 4 seeds) | ~1 dia de A40 | nenhum — cabe em memória desde a correção do P5 |
| L2 | Rebuild dos 6 substratos pelo CLI novo | horas | só HGI — o join espacial deixou de ser bloqueio |
| L3 | Gate de estado grande para D1/D2 | ~4 h | antes de os schedules virarem default global |

L3 importa: "converge cedo" é o argumento mais fraco justamente onde há mais dados.

## 3 · Implementação restante

| # | Item | Estado | Nota |
|---|---|---|---|
| I1 | ~~Join espacial de regiões~~ | ✅ **feito 2026-08-17** | resta só o HGI (POI2Vec + Delaunay) como dependência externa |
| I2 | Lane Modal (fase 10) | não iniciada | por ordem de prioridade |
| I3 | P3 — `torch.compile` refeito por fold | não feito | correção arrisca fidelidade; só custa wall |

## 4 · Achados de review ainda abertos

- **Grupo A de performance não implementado** (máscara de padding, syncs do contador de ambiguidade).
  Motivo: **duas magnitudes deste ciclo de review não reproduziram** — o `isin` foi reportado como
  1,1–1,5 s por fold e mede 1,4 ms (~1000× menor), e os cronômetros foram reportados como 20 % errados
  e já contabilizavam 95,5 % do wall. Os *achados* são reais; os números anexados a eles, não. Medir
  antes de implementar.
- **`enable_determinism` usa `warn_only`** — hoje as ops que caem no caminho não-determinístico são
  gravadas no manifesto (`nondeterministic_fallbacks`), mas não há teste que falhe se a lista crescer.

## 4b · Nomenclatura — corrigida 2026-08-17

O que este projeto chamava de **seed** é, na literatura, uma **repetição** de k-fold CV: cada seed
gera uma **partição nova** de usuários (verificado: 4 seeds → 4 partições distintas). E o mesmo
inteiro também semeia a inicialização, então **um botão move dois fatores experimentais** e nada do
que já rodou consegue separar variância de partição de variância de otimização.

Regras e vocabulário: [`../../docs/NOMENCLATURE.md`](../../docs/NOMENCLATURE.md), com teste que falha
se `n=20` voltar a aparecer como tamanho amostral no pacote.

**Pendência que isso abre:** separar `split_seed` de `model_seed` é pré-requisito para essa
decomposição, e casa com o trabalho de protocolo de avaliação.

## 5 · Fatos medidos que qualquer trabalho futuro deve respeitar

Estes custaram tempo para descobrir e são fáceis de reintroduzir:

- **Execuções compiladas não são bit-reprodutíveis entre sessões.** Duas execuções da mesma config
  diferem 0,02–0,05 pp. Nenhum delta abaixo disso é interpretável.
- **O substrato não é reprodutível nem na referência** (R16). Reconstruir move o macro-F1 ~0,18 pp
  (amplitude de n=3). Determinismo ligado resolve para builds novos, não recupera os bancados.
- **Folds dentro de uma seed não são réplicas** (~80 % de treino em comum). A banda de aceitação é o
  desvio dos deltas pareados **por seed**; usar a dispersão entre folds infla a tolerância ~2×.
- **`--diagnostics` roda compilado** desde a separação da sonda de geometria. O baseline eager de
  `BASELINE_1FOLD.md` **não** é comparável a execuções novas; use `runs/profile_1fold_after`.
- **GPU a 98–100 % de utilização** numa célula de categoria. Perseguir overhead de lançamento
  persegue ~0 %.
