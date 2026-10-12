# A escada dimensiona contra o ruído do próprio medidor — recomendação para o v20

**Aberto em** 2026-08-25, durante a campanha `v19_ladder`.
**Estado:** diagnóstico medido, corretor nomeado e citado. **Não aplicável ao v19** — a regra é
pré-registrada, o ciclo começou, e o `EVALUATION_PROTOCOL_CHANGES.md` é explícito que emenda que
altera decisão invalida o ciclo em curso.

## A recomendação, em uma linha

**Trocar `σ̂` observado por um limite superior de confiança sobre a COMPONENTE de variância** —
intervalo MLS (*Modified Large-Sample*) — de modo que a escada dimensione contra a dispersão do
procedimento e não contra ela somada ao ruído de amostragem da validação interna.

## O que foi medido

Dois conjuntos subiram a escada até o teto (P=6). Decompondo a dispersão entre execuções — dentro de
cada execução o delta varia entre os 5 folds, e essa variação sobre √5 estima o erro-padrão da média
daquela execução:

| | sd entre execuções | ruído do estimador | fração da variância que é ruído |
|---|---:|---:|---:|
| alabama cat | 0,068 | 0,176 | ruído > total |
| alabama reg | 0,212 | 0,184 | ~75 % |
| istanbul cat | 0,065 | 0,081 | ruído > total |
| istanbul reg | 0,126 | 0,110 | ~76 % |

**E o piso de ruído acompanha o tamanho do split interno, que é a assinatura do mecanismo.** Medido
no primeiro degrau de cada conjunto, à medida que a campanha avançou:

| conjunto | usuários | piso de ruído (cat / reg) | degraus que ele torna inalcançáveis |
|---|---:|---|---|
| alabama | 1 101 | 0,176 / 0,184 | 2, 3, 4 |
| arizona | 2 136 | 0,134 / 0,110 | 2, 3 |
| istanbul | 14 530 | 0,081 / 0,110 | 2, 3 |
| **florida** | **10 622** | **0,063 / 0,074** | **só o 2** |
| **california** | **~22 000** | **0,045 / 0,043** | **só o 2** |

Não é conjectura mais: o piso cai por um fator de **~4** do menor conjunto ao maior,
monotonicamente, e com ele cai o número de degraus que a aritmética elimina.

**E a lei é a certa.** Ancorando no Alabama e prevendo os demais por `1/√n` sobre os usuários:

| conjunto | usuários | piso medido | previsto por 1/√n | razão |
|---|---:|---:|---:|---:|
| alabama | 1 101 | 0,180 | *(âncora)* | 1,00 |
| arizona | 2 136 | 0,122 | 0,129 | 0,94 |
| florida | 10 622 | 0,069 | 0,058 | 1,19 |
| california | ~22 000 | 0,044 | 0,040 | 1,09 |

Quatro conjuntos, faixa de 20× em tamanho, e o desvio fica em ±20 %. **É a assinatura de ruído de
amostragem de um estimador** — e sensibilidade genuína à partição não teria motivo nenhum para
depender do tamanho do split interno, muito menos com esse expoente.

⚠ **Istambul é o desvio, e ele confirma o mecanismo em vez de contradizê-lo.** Com 14 530 usuários a
lei preveria ~0,050, e o medido é 0,081/0,110. Mas Istambul é o conjunto de "muitos usuários, poucas
janelas" (§12.6c) — e o que o estimador amostra são **janelas**, não usuários. O desvio aponta na
direção que a contagem de janelas prevê.

E a condição de parada, invertida para σ̂ (`pilot.sd_maximo`), diz o que isso custa:

| degrau | maior sd que ainda resolve |
|---|---:|
| P=2 | 0,0113 |
| P=3 | 0,0761 |
| P=4 | 0,1455 |
| P=6 | 0,2608 |

**Com um piso de ruído de 0,184, os degraus 2, 3 e 4 são inalcançáveis qualquer que seja a dispersão
verdadeira.** O teto estava decidido por aritmética antes de a primeira execução terminar.

## Por que o alvo é outro, e por que isso é estrutural

O delta **externo** é censo: sob o OOF agrupado do §1, todo usuário pontua exatamente uma vez. Então
a variância entre execuções no externo **não contém** o termo de amostragem da validação interna de
10 %. O alvo correto da escada é `σ_proc` (mais um resíduo de heterogeneidade de fold ÷ 5), e a regra
atual dimensiona contra `σ_proc ⊕ ruído-do-medidor`. No Alabama/região isso é ~0,21 contra um alvo em
[0,065, 0,21]: compra contra duas a três vezes a dispersão relevante.

**A regra atual superdimensiona por viés do proxy, não por conservadorismo escolhido.** A distinção
importa: conservadorismo escolhido se defende; viés não declarado, não.

## ⚠ O que NÃO fazer: o desconto ingênuo

`σ̂²_corrigido = max(σ̂²_observado − σ̂²_ruído, 0)` é o estimador ANOVA da componente entre-grupos, e
tem linhagem legítima (Searle, Casella & McCulloch 1992) — mas **não pode entrar numa regra de
parada**, por quatro razões, e a primeira sozinha basta:

1. **Ele zera.** Em duas das quatro séries acima o desconto colapsa a zero. Com `σ̂ = 0` o fator de
   Browne multiplica zero, e a escada para no primeiro degrau permitido — P=3, com **2 graus de
   liberdade e t₀.₉₇₅,₂ = 4,30**. É exatamente o cenário contra o qual o §2a construiu três guardas,
   reintroduzido pela porta lateral.
2. **Browne não se aplica ao estatístico corrigido.** Os fatores são derivados para `s² ~ χ²`; a
   diferença `MSB − MSW` é uma combinação de χ² com sinal trocado, com massa enorme em zero quando
   P ≤ 4.
3. **O alvo fica incompleto.** O externo retém a parte *genuína* da heterogeneidade entre folds
   (÷ 5). Subtrair todo o spread de fold subtrai também ela, e o alvo vira um colchete
   `[σ²_exec, σ²_exec + MSW/5]` em vez de um ponto.
4. **O próprio `σ̂²_ruído` é suspeito.** `fold_sd/√5` só estima o erro-padrão da média sob
   independência entre folds — que Bengio & Grandvalet (2004, *JMLR* 5:1089) provam inverificável em
   validação cruzada, porque os treinos se sobrepõem em ~75 %, com viés de sinal desconhecido.

E há evidência empírica contra o modelo exatamente onde ele zera: a ANOVA em alabama/cat dá
`F = MSB/MSW = 0,133` com (5, 24) graus de liberdade, e `P(F ≤ 0,133 | σ_exec = 0) = 0,017`. Sob o
modelo que justifica a subtração, a variância entre execuções não pode ser sistematicamente **menor**
que o ruído da média.

## A assimetria de perdas, que é o que decide

O teste externo é lido **uma vez**. Se P sai pequeno e o intervalo publicado sai largo, **não existe
"comprar mais duas execuções e reler"**: uma extensão decidida depois de ver o intervalo é adaptação
dependente do efeito, e derruba precisamente a dispensa de correção de α (Kieser & Friede 2000) que
sustenta o desenho. Subdimensionar é irrecuperável; sobredimensionar custa GPU.

É por isso que o UCL de Browne existe, e é por isso que o corretor tem de preservá-lo.

## O corretor certo, com nome

**Limite superior de confiança sobre a componente de variância, pelo intervalo MLS:**

* Graybill & Wang (1980), *JASA* 75:869 — o método;
* Burdick & Graybill (1992), *Confidence Intervals on Variance Components*, Dekker, §3 — a
  sistematização;
* Ting, Burdick, Graybill, Jeyaratnam & Lu (1990), *J. Stat. Comput. Simul.* 35:135 — o caso
  não-balanceado, que é o nosso quando uma execução perde um fold;
* Patterson & Thompson (1971), *Biometrika* 58:545 — REML, a alternativa de estimação.

A regra vira

    t₀.₉₇₅,P−₁ · UCL₈₀_MLS(σ_exec ⊕ resíduo-externo) / √P  <  δ

o que **preserva Browne no nível da componente**: o limite superior é positivo com probabilidade 1,
então o colapso a zero desaparece por construção. E continua lendo só variâncias, o que mantém a
cegueira ao efeito e a forma do argumento de dispensa de α.

**Precedente da família:** re-estimação cega de componente de variância para dimensionamento é o que
ensaios cluster-randomizados fazem com o ICC — a mesma linhagem de piloto interno (Wittes & Brittain
1990; Kieser & Friede 2000; revisão em Friede & Kieser 2006).

## O que o v20 precisa fazer, em ordem

1. **Persistir estatística por usuário da validação interna.** O termo de resíduo externo não é
   estimável do que está em disco hoje — os `result.json` guardam agregados por fold. Sem isso o
   corretor honesto colapsa de volta na regra atual. É código novo, e é o pré-requisito de tudo.
2. **Implementar o UCL MLS** sobre o desenho execução × fold.
3. **Re-simular α** para a regra nova. A simulação de 2026-08-25 (2,56 % contra 2,5 % nominal) vale
   para a regra atual; a corrigida é outra regra.
4. **Piso explícito de P ≥ 4.** Com o corretor, P=3 deixa de ser improvável e passa a ser comum, e 2
   graus de liberdade não sustentam a banda do §10.2.
5. **Simetrizar o proxy interno.** Hoje o braço de região dedicado é lido em `joint_convention` — a
   época do argmax **não-gateado** da série `indist`, que não é a época do checkpoint selado nem o
   estimando do §1 (`top10_raw`), enquanto o conjunto é lido na época do seletor, gateada. O proxy
   compara "conjunto como desplega" contra "dedicado num diagnóstico que não desplega". Ler
   `joint_best.top10_raw` contra a lane crua gateada do dedicado é mudança de **entrada da regra**,
   e por isso mora aqui e não no ciclo corrente.

## O que foi rejeitado, e por quê

**Escalada por tarefa.** A escada só para quando todas as tarefas resolvem, e nos dois conjuntos
medidos `cat` resolveu cedo (P=3 em Istambul, P=4 em Alabama) e foi arrastado por `reg` até o teto.
Seria tentador deixar cada tarefa comprar o seu. **Não dá:** as execuções são compartilhadas — o
braço `joint` produz as duas tarefas — e `assert_ladder` exige que todos os braços tenham as mesmas
execuções, porque é isso que torna o pareamento válido. Escalada por tarefa quebraria a simetria que
o estimando pareado depende.

## O que já foi feito no ciclo corrente, e é diagnóstico e não regra

* `pilot.sd_maximo(P, margem)` — a condição de parada invertida para σ̂;
* `cli._ruido_interno` — o piso de ruído, só dispersão, nunca a média;
* a escada denuncia em WARNING, no primeiro degrau, quando o ruído sozinho torna um degrau
  inalcançável;
* `wave run --preflight` — roda o piso e para, para o caso em que a pergunta "este desenho consegue
  resolver?" é genuína. **Não usado na campanha v19**, onde a resposta já é conhecida e a decisão de
  pagar já foi tomada.

## Leia também

- [`../plans/EVALUATION_PROTOCOL.md`](../plans/EVALUATION_PROTOCOL.md) §2a e §10.2
- [`../plans/EVALUATION_PROTOCOL_CHANGES.md`](../plans/EVALUATION_PROTOCOL_CHANGES.md) — a entrada de
  25-08 que registra a decisão de não reiniciar
- [`banda_da_ponte_transfere.md`](banda_da_ponte_transfere.md) — o memo que originou a escada
