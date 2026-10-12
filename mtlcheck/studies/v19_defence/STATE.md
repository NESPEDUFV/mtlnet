# Estado — v19_defence (a vitrine, refeita sob a escada)

> Contrato com quem retoma: humano ou agente. Quem encerra uma sessão atualiza este arquivo.
> Se estiver desatualizado, ele é pior que inexistente.

**Última atualização:** 2026-08-25, com dois dos seis conjuntos fechados.

## Onde estamos

**A CAMPANHA FECHOU.** Os seis conjuntos, **81 células, zero falhas** em qualquer célula de
qualquer estado. Todos **resolveram** — meia-largura abaixo de δ = 0,4 nas duas tarefas em todos —
e **nenhum** levou o carimbo `partition-limited`. Os 81 têm `result.json` e `predictions.parquet`;
nenhum veredito ficou `incompleto`.

**Os seis ensaios de leitura passam** (27-08): sete guardas em cada, canário do §1 sem disparar em
nenhum, e a escada reconhecida com o degrau certo — de P=3 no Texas a P=6 no Alabama e Istambul.

**O degrau final cai com o tamanho do conjunto**, que é o que a teoria de estabilidade prevê e o
§10.4 já sugeria no eixo de partição: Alabama (1 101 usuários) e Istambul foram ao teto; Arizona,
Florida e California pararam em 4; o Texas — o maior, 3,8 milhões de janelas — parou em **3**, com o
menor desvio da campanha (`cat` sd = 0,0096 no piso).

Custo real: ~32 h de GPU, contra os ~47 h projetados na abertura e o pior caso de ~54 h que se temeu
em 25-08. Pico de memória: Texas 38,8 GB de 46, sem OOM em nenhum momento. A anterior — que demonstrava a ponte, aposentada — está em
[`../archive/v19_defence_bridge/`](../archive/v19_defence_bridge/ARQUIVADO.md).

| conjunto | P | cat (sd · meia) | reg (sd · meia) | desfecho | relógio |
|---|---:|---|---|---|---:|
| alabama | 6 | 0,068 · 0,105 | 0,212 · 0,324 | **resolveu** no teto | 24 min |
| istanbul | 6 | 0,065 · 0,100 | 0,126 · 0,194 | **resolveu** no teto | 1 h 38 |
| arizona | 4 | 0,079 · 0,217 | 0,072 · 0,197 | **resolveu** | 42 min |
| florida | 4 | 0,092 · 0,253 | 0,028 · 0,078 | **resolveu** | 4 h 58 |
| california | 4 | 0,054 · 0,149 | 0,099 · 0,273 | **resolveu** | 11 h 37 |
| texas | **3** | 0,055 · 0,290 | 0,068 · 0,358 | **resolveu** | 11 h 13 |

Todos **pararam por resolver**, não por bater o teto — meia-largura abaixo de δ = 0,4 nas duas
tarefas em todos os cinco.

⚠ **O piso de ruído do estimador domina a dispersão medida, e isso apareceu nos três.** Em
`arizona/reg` o ruído (0,141) é o DOBRO do desvio total observado (0,072); em `alabama/cat` e
`istanbul/cat` ele também excede o total. O componente de partição está medindo perto de zero — o que
é um resultado, não um defeito, e é o que o §10.4 já sugeria nos conjuntos pequenos. A consequência
prática é que a escada compra mais execuções do que o eixo pediria; o corretor está nomeado em
[`../../docs/future_works/escada_mede_o_ruido_do_medidor.md`](../../docs/future_works/escada_mede_o_ruido_do_medidor.md)
e é trabalho do v20. Uma auditoria externa em 25-08 conferiu
1 514 checagens estruturais mais 624 profundas (partições rederivadas do corpus, fingerprints
recomputados, épocas de seleção reproduzidas) e as declarou **bancáveis**.

⚠ **A leitura ainda não aconteceu e depende de autorização explícita do autor, por conjunto.** O
procedimento está em [`LEITURA.md`](LEITURA.md) — leia antes, não improvise. O ensaio (`--dry-run`)
passa nas sete guardas em Alabama, Arizona e Florida, incluindo o caminho de conjunto grande com
10,2 milhões de linhas no braço conjunto.

**A leitura aconteceu em 27-08**, autorizada conjunto a conjunto. A co-primária **vale em 4 dos 6** —
os dois em que não vale são os dois menores. Payloads em [`leitura/`](leitura/); o procedimento que a
governou, em [`LEITURA.md`](LEITURA.md).

⚠ **Antes de citar qualquer número contra a dissertação, leia
[`CAP5_CONTRA_V19.md`](CAP5_CONTRA_V19.md).** O padrão de **região** do Capítulo 5 reproduz-se nos
seis conjuntos, sinal por sinal — o gradiente não é achado desta campanha, é achado da dissertação, e
esta o reproduz sob um protocolo mais estrito. Em **categoria** a concordância é bem mais fraca (3 de
6), e há **uma discordância real** em Texas. E as células **não se subtraem** em nenhum dos eixos.

Por que existe esta campanha e o que ela pode afirmar: [`STUDY.md`](STUDY.md).

## Feito

- [x] a ponte aposentada; o protocolo caiu de 1084 para 489 linhas · `d67716c4`
- [x] a escada implementada — lógica, `wave run`, gate do `compare` · `5a027e6f`, `e3021167`
- [x] nove achados de uma revisão adversarial, incluindo a escada estar **desligada dos dois lados**
      quando o commit dizia o contrário · `52bb551a`
- [x] a campanha da ponte arquivada, com o que dela continua valendo
- [x] os seis manifestos da escada, carregando e validados localmente
- [x] a escada validada de ponta a ponta em miniatura, e ela achou o defeito que a impedia de
      passar de P=3 · `fa0a8bf4`
- [x] a receita de análise da escada, `recipes/analysis/v19_ladder.toml` · `87de27ec`
- [x] o veredito da escada persistido e exigido na leitura · `875ca05e`, `af054252`
- [x] **alabama e istanbul executados e auditados**

## Próximo

**1 · Sincronizar — com a exclusão ÂNCORADA.** Feito em 25-08; confere por hash.

```bash
rsync -a --checksum \
      --exclude '/.git' --exclude '/.venv' --exclude '/runs' --exclude '/artifacts' \
      --exclude '__pycache__' --exclude '/data' --exclude '/scratch' --exclude '.DS_Store' \
      ./ nespedgpu:/dados/poimtlnet/mtlcheck/
```

⚠ **A barra em `/data` é o conserto, e não o `--checksum`.** O lançamento de 25-08 morreu com
`TypeError: build() got an unexpected keyword argument 'split_seed'` porque o `splits.py` do remoto
era o antigo. A causa não era mtime-versus-conteúdo: era `--exclude 'data'` **sem âncora**, que em
rsync casa qualquer diretório chamado `data` em qualquer profundidade — inclusive
`src/mtlcheck/data/`, onde o `splits.py` mora. O diretório inteiro ficava fora do rsync, e nenhuma
quantidade de `--checksum` o traria. Diagnosticado por hash em 25-08: 8 197 bytes aqui contra 7 847 lá.

Confira por hash depois, sempre — `grep` por nome de campo diria "consertado" com as árvores
diferentes:

```bash
ssh nespedgpu 'sha256sum /dados/poimtlnet/mtlcheck/src/mtlcheck/data/splits.py'
shasum -a 256 src/mtlcheck/data/splits.py
```

**1b · Apontar `ARTIFACTS_ROOT` para `artifacts_final`.** Não para `artifacts`:

```bash
export DATA_ROOT=/dados/poimtlnet/data
export ARTIFACTS_ROOT=/dados/poimtlnet/artifacts_final
export RUNS_ROOT=/dados/poimtlnet/runs
```

⚠ **Há onze `artifacts*` na `nespedgpu` e só um é o certo.** `artifacts_final` é o único cujos seis
substratos batem com as identidades que os manifestos declaram (conferido em 25-08, seis de seis,
sob `substrate/check2hgi_v18/`). Os outros dez são sósias com identidade diferente — e `/dados/poimtlnet/artifacts`, que é o nome
óbvio, é pior que sósia: é um andaime de **symlinks** para
`output/check2hgi_design_k_resln_mae_l0_1/`, um engine **diferente**, sem `manifest.json`. Sem
manifesto a conferência de identidade **degrada para aviso** (`wave.py`, ramo `if not actual`), então
a wave rodaria sobre o substrato errado sob o nome deste estudo, avisando num log e falhando em
nada. O `TypeError` de ontem foi a única coisa que impediu isso.

**2 · Rodar o que falta**, um por vez — concorrência é 3 a 9 % mais lenta:

```bash
mtlcheck wave run studies/v19_defence/waves/ladder_arizona.toml     # ≈ 1,6 h
mtlcheck wave run studies/v19_defence/waves/ladder_florida.toml     # ≈ 5,8 h a 8,8 h
mtlcheck wave run studies/v19_defence/waves/ladder_california.toml  # ≈ 9,6 h a 19,2 h
mtlcheck wave run studies/v19_defence/waves/ladder_texas.toml       # ≈ 12,4 h a 24,8 h
```

⚠ **A faixa dupla é a questão em aberto.** O custo projetado assumia 3 a 4 execuções nos grandes, e
os dois conjuntos já rodados foram a **6** — inclusive Istambul, com 14,5 mil usuários, que era a
aposta de parada em P=4. Se os grandes forem ao teto, o que falta passa de ~29 h para ~54 h. Para
parar em P=3 é preciso `sd₃ < 0,076 pp`, e nem a série mais estável já medida (o cat do Alabama,
sd₃ = 0,090) passou disso. **Depois da Florida haverá o primeiro `sd` de conjunto grande** — é ali que
California e Texas se reprojetam com medição em vez de esperança, antes de comprometer ~44 h.

**3 · A leitura**, uma vez, com autorização explícita do autor. Ensaie antes:

```bash
mtlcheck compare <runs>/v19_ladder --analysis <receita v20> --state alabama --dry-run
```

⚠ A receita de análise da escada usa `sd_source = "self"` e **não declara `bridge_states`** — as
duas coisas juntas são recusadas. Ela ainda não existe; criar é parte do passo 3.

## Se o Texas estourar a memória

Projeção: **~38,9 GB de 46**, folga de ~7 GB. Vem da âncora direta — o `joint` do TX foi medido em
**36,69 GB** na A40 (`studies/porting_validation/L1_LARGE_STATES.md`) e a placa nova usa 1,06× (CA
mediu 35,0 aqui contra 33,02 lá). Uma escala linear em janelas daria 45,8 GB, mas sobre-estima: o TX
tem **menos** classes de região que a CA (6 553 contra 8 501), o que encolhe os logits e a torre.

**De onde vem o pico:** `data/dataset.py:_stream` move o fold inteiro para o device, e o braço
conjunto segura **dois** streams. Só o `x` do TX são 8,8 GB por stream
(3 830 414 × 9 × 64 × 4 bytes).

**O lever, se for preciso:** manter o dataset residente em CPU e mover por batch, com `pin_memory`.
É **byte-idêntico** — fatiar um tensor que já está na GPU e copiar um batch de CPU para GPU produzem
os mesmos valores; muda só onde a cópia acontece. O repositório de referência fez exatamente isso
para CA/TX. **Não está implementado aqui**, e a decisão de implementar sob pressão é do autor: o
risco de introduzir defeito num sistema que produziu onze deles em 24 h compete com o risco de
perder o Texas.

⚠ **Se der OOM: parar e não relançar.** Um relance às cegas gasta horas e não muda nada. E o Texas
pode simplesmente não fechar antes de 28-08 sem contaminar coisa alguma — a escada fecha por
conjunto, e a leitura dos cinco que fecharam é válida sozinha.

## Pendências que não bloqueiam

- ~~**`test_the_region_join_is_derived_per_state_and_guarded` falha na `nespedgpu`.**~~ **FECHADA em
  25-08**: era `DATA_ROOT` não exportado, não shapefile faltando. Sem a variável o caminho relativo
  cai dentro do repo (`.../mtlcheck/data/miscellaneous/…`), onde não há shapefile; o arquivo existe
  em `/dados/poimtlnet/data`. Reproduzida nos dois sentidos — falha com a variável limpa, passa com
  ela posta. Com os três roots exportados a suíte de lá fecha em **724 passando, 77 pulados, 1 xfail,
  0 falhas** (o baseline de 702/1/98 foi colhido sem os roots). Lição registrada em
  [`../../docs/BEST_PRACTICES_NESPEDGPU.md`](../../docs/BEST_PRACTICES_NESPEDGPU.md) §6b: rode a
  suíte com o mesmo ambiente com que rodaria um treino, ou ela mente sobre o que está quebrado.
- **Duplicatas obsoletas em `studies/v19_defence/waves/` na `nespedgpu`.** O rsync não usa `--delete`, então
  os onze manifestos da campanha da ponte (`campaign.toml`, `slice_*.toml`, `escalation_*`,
  `s10_4_*`) continuam lá ao lado dos `ladder_*.toml` — conferidos byte a byte como cópias exatas do
  que está no arquivo. Não afetam a execução (nomes distintos), mas alguém que rode
  `slice_alabama.toml` de lá **re-treina célula selada**. Apagar por nome, não com `--delete`.

## Bloqueios

- **A receita de análise da escada não existe.** As `v19_headline*.toml` são da ponte e ficam
  congeladas para a campanha arquivada. Criar é parte do passo 3.

Não é mais bloqueio: a `nespedgpu` voltou em 25-08 às 13h26 UTC (`up 0 min`, GPU livre, 2,1 TB em
`/dados`). A árvore de lá foi sincronizada e confere por hash. **A decisão do autor em 25-08 é
validar primeiro no MacBook** — ver [`../scratch_ladder_local/`](../scratch_ladder_local/STUDY.md),
que exercita o laço da escada de ponta a ponta antes de a GPU gastar hora nele.

**A máquina está validada para a campanha (25-08).** A GPU foi **trocada** no reboot: saiu a A40
(`sm_86`), entrou uma **RTX 6000 Ada Generation** (`sm_89`), mesmos 46 GB, driver 580.173.02 /
CUDA 13.0. O torch de lá (2.11.0+cu128) **não lista `sm_89`** no `arch_list` e ainda assim roda — o
cubin de `sm_86` é compatível para frente dentro da mesma major. Exercitado com kernel de verdade e
com uma célula `cat` do Alabama, que saturou a placa (100 % util, 4006 MiB, 299 W de 300 W) e fechou
em 15 s por fold. Alabama e Florida foram remedidos: a campanha cai de **≈ 47 h para ≈ 32 h**, e a
razão contra a A40 **cresce com o tamanho do conjunto** (1,21× no Alabama, 1,53× na Florida), então
as 32 h devem sobrar. Tabela e derivação em [`STUDY.md`](STUDY.md).

## O que já foi tentado e não funcionou

- **Reaproveitar células da campanha arquivada.** Só a execução `(0,0)` serviria — as outras são
  todas de `split_seed = 0`, e a escada precisa dos dois botões juntos. Decisão do autor em 25-08:
  do zero, e o `study = "v19_ladder"` existe para que o resume não reaproveite em silêncio.
- **`rsync -a` sem `--checksum`** numa renomeação que atravessa arquivos. Ver passo 1.
- **Deixar o Texas da campanha antiga terminar.** Ele treinava `p0s1` e `p0s100` — partição 0 — e a
  escada usa `(1,1)`, `(100,100)`. Nenhuma das duas células entraria. Morto em 25-08 com ~12 h de
  A40 poupadas.
