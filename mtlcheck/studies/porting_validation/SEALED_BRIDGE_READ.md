# Primeira leitura selada — 2026-08-18

> **O conjunto externo de AL/AZ/IST foi lido nesta data.** Ato deliberado, autorizado pelo autor,
> registrado aqui porque o §5 do protocolo exige que seja datado. A partir de agora, **qualquer
> mudança de receita, arquitetura, hiperparâmetro, cabeça ou regra de seleção escolhida à luz destes
> números converte estas execuções em exploratórias** (critério de auditoria 7), e Istambul é a mais
> cara — o §9.4 lhe atribui o peso confirmatório justamente por nunca ter sido estado de tuning.
>
> Mudanças de telemetria, instrumentação e correção de bug **não** contaminam: não tocam no modelo,
> nos dados, na receita nem no estimando.
>
> Dados: `evidence/sealed_bridge_tier_a.json`. Wave: `waves/sealed_bridge.toml`, 36 células,
> 13 141 s, 0 falhas. R = 4 réplicas (`model_seed ∈ {0,1,7,100}`) sobre partição congelada
> `split_seed = 0`.

## 1 · O resultado

Tier A, bootstrap pareado por usuário, 10 000 réplicas, BCa 95 %, permutação sign-flip estudentizada
10 000. Δ = joint − dedicado, em pontos percentuais. Margem pré-registrada δ = 0,4 pp.

| estado | tarefa | dedicado | joint | Δ | BCa 95 % | meia-largura | p | veredito |
|---|---|---:|---:|---:|---|---:|---:|---|
| alabama | cat | 30,3389 | 30,0788 | −0,2727 | [−0,500, −0,056] | 0,222 | 0,0239 | inconclusivo |
| alabama | reg | 69,0060 | 68,0533 | **−0,9528** | [−1,149, −0,751] | 0,199 | 0,0001 | **inferior** |
| arizona | cat | 34,3167 | 34,2010 | −0,1201 | [−0,249, +0,009] | 0,129 | 0,0657 | não-inferior |
| arizona | reg | 58,6961 | 58,2243 | −0,4718 | [−0,636, −0,295] | 0,171 | 0,0001 | inconclusivo |
| istanbul | cat | 35,1320 | 35,3022 | **+0,1640** | [+0,049, +0,272] | 0,111 | 0,0032 | **superior** |
| istanbul | reg | 74,9726 | 74,8202 | −0,1524 | [−0,282, −0,080] | 0,101 | 0,0005 | não-inferior |

⚠ **Multiplicidade ainda não aplicada.** São seis comparações com p brutos. O §5 prevê Holm na
família manchete e o §3 prevê o gatekeeping sequencial NI → superioridade. Os vereditos acima são
por-célula, no nível nominal.

## 2 · A ressalva que governa a leitura inteira

**Esta comparação não é diag-best contra diag-best.** O braço dedicado é avaliado na época que a
validação *interna daquela tarefa* escolheu (o estimador **b1** do §8a). O braço joint é avaliado na
única época `geom_simple` (o estimador **b2**). Logo

> Δ medido = (interferência multi-tarefa) + (custo de comprometer-se com um único checkpoint)

e o §8a diz explicitamente que essa assimetria **corre contra o braço joint**: "a comparação
deployable legada deixava cada braço STL colher o próprio máximo por época enquanto o braço joint se
comprometia com um checkpoint".

Os dois termos **não são separáveis com o que está bancado**. Separá-los exige o **b1 do joint** —
escore externo na época que a val interna escolheu *para cada tarefa* — que é exatamente o pedido (c)
do autor e exige a passagem em quarentena do §8a sobre checkpoints por época retidos. Ou seja: o
pedido (c) deixou de ser desejável e passou a ser **necessário para interpretar este resultado**.

Enquanto isso não existir, a frase defensável é "o checkpoint joint único entrega X pp a menos que
dois modelos dedicados, cada um no seu melhor" — não "a MTL custa X pp".

## 3 · O diagnóstico obrigatório do §3 — passa

O §3 exige, no primeiro estado regenerado: "reportar a meia-largura realizada do IC pareado contra a
projeção de 0,05–0,3 pp e o benchmark não-pareado de ≈ 0,5 pp".

Meia-larguras realizadas: **0,101 a 0,222 pp**, todas dentro da faixa projetada, e todas bem abaixo
do benchmark não-pareado. **O ganho do pareamento materializou-se.** Alegações sub-0,3 pp e o TOST a
δ = 0,4 continuam de pé.

## 4 · Um erro no próprio protocolo, achado por esta leitura

O §9.2 afirma: "o piso de usuários de Alabama é irredutível: ~0,25–0,3 pp sob reamostragem de
usuário **a 3 858 usuários**". A contagem real do substrato v18 é:

| estado | janelas | usuários | usuários no OOF agrupado |
|---|---:|---:|---:|
| alabama | 96 326 | **1 101** | 1 101 |
| arizona | 200 895 | 2 136 | 2 136 |
| istanbul | 271 666 | 14 530 | 14 530 |

Alabama tem **1 101** usuários, não 3 858 — fator 3,5. O OOF agrupado cobre cada usuário exatamente
uma vez, como o desenho manda. Hipótese (não verificada): 3 858 vem da janelagem v17
(`MIN_SEQUENCE_LENGTH = 5`, stride 9), enquanto v18 exige ≥ 10 check-ins com stride 1 e portanto
elimina usuários curtos.

Consequência para o §9.2: o piso projetado deveria ser ~1,87× mais largo. **Mas a meia-largura
medida em AL (0,199–0,222 pp) é melhor que a projeção original**, então a projeção era pessimista por
outro motivo — provavelmente por não creditar todo o ganho do pareamento. O número "3 858" precisa de
correção; a conclusão do §9.2 (existe um piso, e AL é o estado mais apertado) sobrevive.

## 5 · O padrão, e o que ele sugere

O déficit da região encolhe monotonicamente com o tamanho do estado:

| estado | usuários | Δ reg |
|---|---:|---:|
| alabama | 1 101 | −0,95 |
| arizona | 2 136 | −0,47 |
| istanbul | 14 530 | −0,15 |

E **em Istambul — o estado que o §9.4 designa como portador do peso confirmatório, por nunca ter
sido estado de tuning — a alegação co-primária do §3 se sustenta**: região não-inferior **e**
categoria superior, no mesmo contrato de checkpoint.

Em Alabama ela falha (região inferior à margem). Em Arizona a região fica inconclusiva: o intervalo
inteiro abaixo de zero, mas atravessando −0,4.

⚠ Isto é observação, não achado. Com k = 3 estados e o confundimento tamanho×estado, "o déficit
encolhe com o tamanho" é uma hipótese que a §4 do protocolo trata explicitamente como **não
defensável como confirmatória** com este k. Não a promova a resultado.

## 6 · O que não foi possível medir

O propósito (2) da bridge — medir o otimismo de seleção do protocolo legado — **não é computável com
o que foi bancado**. O estimador **a1** do §8a é "máximo sobre épocas ≥ 5 do escore externo", que
exige checkpoints por época pontuados pós-hoc. Nenhum foi retido. Depende de T3 do
[`TELEMETRY_GUIDE.md`](../../docs/TELEMETRY_GUIDE.md).


---

## 7 · Adendo 2026-08-19 — as três regras do protocolo que não existiam em código

Uma auditoria adversarial descobriu que três regras **pré-registradas** não estavam implementadas.
As três foram implementadas e aplicadas retroativamente a esta leitura. **Nenhum veredito muda.**

Isto é registrado como adendo datado, e não como edição silenciosa, porque a distinção importa: se
algum veredito tivesse mudado, isto seria uma **reinterpretação de resultado selado**, não um
conserto.

| regra | onde estava | efeito nos seis vereditos |
|---|---|---|
| **piso de re-execução** (§3: \|Δ\| ≤ 0,05 pp nunca é reivindicado) | em lugar nenhum | **nenhum** — o menor \|Δ\| é 0,1201, 2,4× o piso |
| **gate de permutação** (§3: superioridade = NI **e** permutação) | o veredito só olhava o intervalo | **nenhum** — o único "superior" (IST/cat) passa com p = 0,0032 |
| **canário de vazamento** (§1: `ood_hit_rate > 1 %` reprova a execução) | código morto — um chamador, o próprio teste | **nenhum** — 60 folds, 0 disparos |

### O canário, em detalhe

Ele era inalcançável por três motivos somados, cada um inócuo sozinho: `ood_diagnostics` só era
chamado pelo próprio teste; `_align_one` chamava `region_counts` sem `train_labels`; e
`_Aligned.metric` reconstruía os contadores com `np.zeros_like` nos campos de OOD. O caminho de
comparação **não conseguia ver OOD nem se quisesse**.

Aplicado agora às 12 células de região seladas, por fold, com os `train_labels` daquele fold:

| estado | `ood_fraction` máx | `ood_hit_rate` máx | limite |
|---|---:|---:|---:|
| alabama | 0,0111 | **0,00000** | 0,01 |
| arizona | 0,0050 | **0,00000** | 0,01 |
| istanbul | 0,0015 | **0,00000** | 0,01 |

O valor não é "abaixo do limite" — é **exatamente zero** nos 60 folds. Com 1,1 % das linhas de
Alabama fora de distribuição, havia oportunidade de sobra para disparar. Isso é evidência positiva
de ausência de vazamento, não só ausência de alarme.

Evidência: [`evidence/leak_canary_sealed.json`](evidence/leak_canary_sealed.json).
