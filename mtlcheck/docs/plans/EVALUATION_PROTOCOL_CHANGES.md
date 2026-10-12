# Registro de emendas ao protocolo de avaliação

O `EVALUATION_PROTOCOL.md` é pré-registro, e a defesa dele é a **data**. Este arquivo existe para
que a pergunta *"você mudou as regras depois de ver os resultados?"* tenha resposta com registro em
vez de com palavra. Uma linha por emenda, com o que mudou, quando, e o que a motivou.

O regime anterior — com a ponte de calibração — está preservado sem edição em
[`../v19_RECORD.md`](../v19_RECORD.md), e todo o histórico está no git.

---

## 2026-08-25 · a partição deixa de ser congelada, e a ponte sai

**O que mudou.** O estimando do §1 passa de condicional a uma partição para **marginal sobre o
sorteio de partição**. Cada execução é um par `(split_seed, model_seed)` com os dois botões sorteados
juntos, e o número de execuções deixa de ser pré-registrado: a **escada do §2a** o decide medindo a
dispersão na validação interna, que não gasta leitura.

**O que motivou.** Não foi mudança de ideia — foi **uma regra pré-registrada disparando**. O §10.4
escrevia, antes de rodar: *"if the partition axis exceeds 0.15 pp, the freeze is unsafe and §2
reopens before any large-state fit"*. Medido em 23-08 em quatro conjuntos, o eixo de partição em
região deu **+0,366 pp no Alabama** e **+0,306 no Arizona** — os dois abaixo de 2 200 usuários — e
caiu abaixo do limiar, com sinal invertido, nos dois acima de 10 mil. O limiar foi excedido e o §2
reabriu.

E o achado moldou o substituto: um eixo que é fenômeno de conjunto pequeno não pode ser tratado
medindo-o nos pequenos e transferindo para os grandes — que é exatamente o que a ponte fazia, e é
exatamente ao contrário. Tem de ser medido **por conjunto**.

**Onde isso está escrito.** §1 (estimando), §2a (a escada), §10 inteiro (a decisão e o teste que a
reverteu), §2 tabela (linha `Outer folds`), §4c (âncora da dose–resposta), §9 checklist, §10.5
(campos).

**Quando, contra quando o ciclo começou.** A emenda foi commitada em **25-08 01:02** (`d67716c4`). O
primeiro fold do ciclo `v19_ladder` foi treinado em **25-08 16:28**. A emenda precede o ciclo em
quinze horas, e **nenhuma leitura confirmatória havia ocorrido** — o teste externo dos seis conjuntos
está intocado neste ciclo.

**A propagação, e por que ela é posterior.** Seis passagens continuaram descrevendo o regime antigo
depois da emenda — a mais visível sendo a tabela do §2, que dizia `split_seed=0 frozen` numa linha e
`both drawn fresh` na seguinte. Foram reescritas em 25-08, **depois** do primeiro fold, por decisão
do autor: o documento é para ser lido, e um leitor que caísse numa daquelas passagens aplicaria a
regra errada. Nenhuma decisão foi alterada nessa passagem — só a descrição alcançou o que já valia.

## 2026-08-25 · três coisas que a auditoria acrescentou ao §2a

Não são emendas de regra; são o que uma auditoria externa mediu e o protocolo passou a declarar.

- **A dispensa de correção de α passa a ser quantificada.** Simulação Monte-Carlo da escada exata:
  **2,56 % de erro tipo I contra 2,5 % nominal** em parâmetros realistas. O texto agora pede que isso
  seja reportado como "inflação da ordem de 0,1 pp de α", com a simulação, em vez de como dispensa
  sem número.
- **A cegueira ao efeito passa a ser obrigação explícita.** A dispensa vale porque a regra lê só
  `stdev`. Nenhum log, artefato intermediário ou relatório pode carregar a **média** dos deltas
  internos antes da leitura — o `ladder_<estado>.json` grava `sd`, o limite superior e a meia-largura,
  e não os deltas.
- **O carimbo "partition-limited" ganha a leitura correta.** Ele diz *"não resolveu nesta margem, pelo
  proxy interno"* — não *"este efeito é sensível à partição"*. Nos conjuntos pequenos a dispersão
  interna é dominada pelo ruído do split de 10 %.

## 2026-08-25 · correção de datas na primeira entrada, e uma janela de exposição declarada

Duas correções à entrada de hoje. A regra deste arquivo é que uma entrada não se edita — se
corrige com outra, datada.

**As datas estavam erradas, e neste documento isso importa mais que em qualquer outro.** A entrada
acima diz que o primeiro fold do ciclo foi treinado às **16:28** e que a emenda o precede em **quinze
horas**. Ambos errados. `16:28` é o timestamp de uma escada em **miniatura** — estudo `scratch`, duas
épocas, para validar o laço — que confundi com a campanha. Os números verificados no disco:

| | quando (UTC) | fonte |
|---|---|---|
| emenda `d67716c4` | 2026-08-25 **04:02:47** | `git log --date=iso-strict-local` |
| a wave da campanha sobe | 2026-08-25 **17:14:34** | primeira linha de `ladder_alabama.log` |
| primeira célula grava `result.json` | 2026-08-25 **17:15:38** | mtime em `runs/v19_ladder/cat-alabama-p0s0/` |

**A emenda precede o primeiro fold do ciclo em 13 h 12 min**, não quinze horas. A alegação portante
— a emenda precede o ciclo, e nenhuma leitura confirmatória ocorreu nele — continua verdadeira e
verificada: o `READ_LEDGER.json` tem apenas as 36 leituras da campanha da ponte, e nada de
`v19_ladder`.

**Uma janela em que o carimbo carregou os deltas internos.** O `ladder_<estado>.json` passou a existir
em `875ca05e` gravando a lista de deltas por execução, e `af054252` os removeu 50 minutos depois. A
wave de Istambul subiu **quatro minutos antes** do segundo commit, e gravou seu veredito às 19:48:01
UTC. Se a árvore sincronizada ainda era a primeira, aquele arquivo carregou o efeito interno por
**3 min 24 s**, até ser sobrescrito às 19:51:25 pela re-execução com o código corrigido. Não é
determinável pelo disco se o sync levou a correção antes de ser commitada — a exposição é **provável,
não provada**. O arquivo do Alabama nunca teve deltas (a wave dele antecede o `_carimba` inteiro).

Por que isso não afeta a validade: a dispensa de correção de α do §2a depende de a **regra** ser cega
ao efeito, e ela é — `avalia()` lê só `stdev`, e as oito decisões de degrau dos dois conjuntos foram
recomputadas dos logs e conferem. O que a janela expõe é um artefato em disco, não a regra. Fica
declarado aqui porque uma janela conhecida e datada é defensável e uma descoberta pela banca não é.

## 2026-08-25 · quatro consertos antes da primeira leitura, e a decisão de NÃO reiniciar

Um parecer externo avaliou se a campanha devia reiniciar com um estimador corrigido, e a resposta
foi **não**. Registro aqui porque a decisão e o motivo importam para quem ler os números.

**Por que não reiniciar.** Alabama e Istambul **resolveram** no teto (meias-larguras abaixo de δ nas
quatro séries, nenhum carimbo `partition-limited`), então P=6 é superconjunto de qualquer regra
corrigida — descartá-los compraria um desenho idêntico ou pior. E o corretor ingênuo
`max(σ̂² − σ̂²_ruído, 0)` **zera** em duas das quatro séries; com σ̂ = 0 o fator de Browne multiplica
zero e a escada para em P=3, publicando com 2 graus de liberdade — exatamente o que o §2a construiu
três guardas para impedir, pela porta lateral. Os fatores de Browne, além disso, são derivados para
`s² ~ χ²`, e `MSB − MSW` não é isso. A assimetria de perdas decide: subdimensionar é irrecuperável
(o teste é lido uma vez, e estender depois de ver o intervalo é adaptação dependente do efeito, que
derruba a dispensa de α), enquanto sobredimensionar custa GPU.

**O diagnóstico continua válido.** O delta externo é censo — todo usuário pontua uma vez — então a
variância externa entre execuções **não** contém o termo de amostragem da validação interna de 10 %.
A regra atual dimensiona contra `σ_proc ⊕ ruído-do-medidor`, e superdimensiona por **viés do proxy**,
não por conservadorismo escolhido. O corretor certo tem nome: limite superior **MLS** sobre a
componente de variância (Graybill & Wang 1980, *JASA* 75:869; Burdick & Graybill, *Confidence
Intervals on Variance Components*, Dekker 1992, §3), que preserva Browne **no nível da componente** e
por construção nunca colapsa a zero. É trabalho do próximo ciclo: exige estatística por usuário da
validação interna que não está em disco, re-simulação de α, e — decisivo — emenda que altera decisão
invalida o ciclo em curso.

**Os quatro consertos, nenhum deles mudança de regra:**

1. **A chave do livro de leituras passa a incluir o estudo.** As células `(0,0)` desta campanha
   resolvem para o mesmo `science_fingerprint` das da campanha da ponte — a receita de treino não
   mudou — e o livro já as registra como lidas em 24-08. Com a chave antiga a leitura nova seria
   engolida como idempotente: o livro afirmaria para sempre que aqueles seis pares foram lidos pela
   ponte, e uma reconciliação acharia 30 registros onde a campanha teve 36 células. A pergunta
   científica — "este teste externo já foi olhado?" — continua ignorando o estudo, e agora avisa em
   voz alta que é segunda olhada.
2. **A série por fold da escada recusa contagem incompleta.** Um fold sem `joint_best` encolhia a
   amostra em silêncio, e a guarda conferia execuções e não folds.
3. **A banda do eixo de execução passa a ser publicada** — ver §10.2. O §10.2 prometia ao revisor que
   "o intervalo carrega os graus de liberdade do P final" e o código publicava o bootstrap por
   usuário, que promedia as execuções e não encolhe com P. As duas agora saem lado a lado, com a
   manchete fixada **antes** de qualquer leitura.
4. **Diagnóstico do piso de ruído**, no primeiro degrau e em `wave run --preflight`: se o ruído do
   estimador já excede o limiar de um degrau, aquele degrau é inalcançável qualquer que seja a
   dispersão verdadeira, e a escada avisa. Em 25-08 isso era computável em quatro minutos e custou
   duas horas de GPU descobrir.

## Regra

Nada neste documento pode ser editado depois do primeiro fold do ciclo que ele governa ser treinado
(§9.6). Uma emenda depois disso é uma **entrada nova aqui**, datada, dizendo o que mudou e por quê —
e, se ela alterar uma decisão e não apenas a descrição, ela invalida o ciclo em curso.
