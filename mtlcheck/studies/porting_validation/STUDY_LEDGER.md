# Ledger de estudos — o que cada `runs/<estudo>` é, e se dá para rastreá-lo

**2026-08-19.** 46 estudos bancados contra 9 manifestos, achado ao auditar por que a campanha de
medição não passou pela wave. Este arquivo é a triagem: para cada estudo, o que ele é e o que se pode
afirmar a partir dele.

> **Por que importa.** Um número num documento sem estudo rastreável não é resultado, é lembrança.
> A tarefa #17 — avaliar contra a dissertação — precisa atribuir diferenças, e não dá para atribuir o
> que não se consegue apontar.

## O critério

Um estudo é **rastreável** quando existe manifesto commitado e ele resolve para os mesmos
`science_fingerprint` que as células bancadas gravaram. É a mesma barra do retrofit da campanha:
manifesto que não reproduz o banco descreve outro experimento.

Estudos anteriores ao campo `science_fingerprint` (gravam `""`) **não podem** passar por essa barra.
Para eles a honestidade é dizer isso, não escrever um manifesto que parece prova e não é.

---

## Rastreáveis — manifesto commitado e verificado

| estudo | o que é | sustenta |
|---|---|---|
| `sealed_bridge` | 36 células, AL/AZ/IST × 3 famílias × 4 réplicas | a **primeira leitura selada** |
| `probe_cost` | 4 braços em AL: compilado/eager × com/sem sonda | o custo da sonda em AL (**+14,0 %**) e o valor do `compile` (**24,4 %**) |
| `probe_cost_scaling` | os mesmos braços em AZ e IST | o custo da sonda escala (**+6,9 %** AZ, **+5,0 %** IST) |
| `l1_large_states` | 1 fold × 3 famílias em FL/CA/TX | o harness aguenta a escala |
| `gate_al_cat_schedule`, `gate_joint_schedule` | varredura de épocas | as decisões D1/D2, adiadas |
| `az_ist_validation`, `profile_1fold` | validação e perfil | — |
| `ref_parity_al` | paridade contra a referência | reg reproduz (**+0,054 pp**) |
| **campanha de 19-08** (10 estudos) | ver `waves/campaign_2026_08_19/` | o veredito do construtor e a atribuição das divergências do POI2Vec |

⚠ `sealed_bridge` e `ref_parity_al` leram o substrato **bancado da referência**, que não tem
`manifest.json` porque não foi construído por este pacote. A identidade dele **não é estabelecível** —
inclusive para as células da primeira leitura selada.

---

## Documentados — sustentam algo, não são reverificáveis

Anteriores ao `science_fingerprint`. O número vale como foi registrado na época; o que não existe é a
possibilidade de conferir que o manifesto descreve a execução.

| estudo | o que foi | disposição |
|---|---|---|
| `sealed` | a primeira leitura selada, antes da `sealed_bridge` | **superado** por `sealed_bridge`; mantido como histórico |
| `profile_1fold_after` | baseline compilado, 3 estados × 3 famílias | **citado** em `BASELINE_1FOLD.md` e `BACKLOG.md` — é contra ele que a próxima medição de perf compara |
| `sched_probe*`, `probe_ep35`, `probe_ep50`, `rev_sched_*` | sondagens de schedule e de época | alimentaram D1/D2, que estão **adiadas**; nenhum número citado |
| `probe_ab_stock`, `probe_ab_noprobe` | a tentativa de inferir o custo do `compile` de duas células bancadas | **falsificados por si mesmos**: deram 0,4 %, o A/B controlado do `probe_cost` deu 24,4 %. Ficam como o registro do erro |

---

## Descartáveis — nomeados para que a contagem pare de sugerir proveniência perdida

`scratch`, `scratch_bf16`, `scratch_eager`, `review_scratch`, `report_check`, `contract`,
`verify_reuse`, `jointcheck`, `memcheck`, `memprobe_bare-compiled`, `memprobe_bare-eager`,
`repr_seed_rs0`, `repr_seed_rs1`.

Depuração e verificação de encanamento. Nenhum sustenta afirmação em documento nenhum — conferido por
busca do nome do estudo em `studies/` e `docs/`.

Os dois `repr_seed_rs*` são o começo do sweep que foi **cancelado e refeito** sobre o caminho
unificado; os que valem são `rs{0,1,7}_v18region`.

---

## O que esta triagem mudou nos documentos

Os números citados no `TELEMETRY_GUIDE.md` e no `STATE.md` não nomeavam o estudo que os produziu.
Passam a nomear. A conclusão não muda — `probe_cost` e `probe_cost_scaling` têm manifesto e são
rastreáveis — mas a cadeia deixa de depender de alguém lembrar.
