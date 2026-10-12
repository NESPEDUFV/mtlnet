# Estado — porting_validation

**Última atualização:** 2026-08-19 (noite)

> Retomando? Leia este arquivo, depois [`../../docs/QUAL_CONJUNTO_USAR.md`](../../docs/QUAL_CONJUNTO_USAR.md)
> (curto, e resolve a dúvida que mais custou tempo) e
> [`../../docs/RUNNING_STUDIES.md`](../../docs/RUNNING_STUDIES.md) antes de executar qualquer coisa.

## 1 · Onde estamos, em uma frase

**Ainda em desenvolvimento.** Nenhum número gerado até aqui vai para a dissertação — o objetivo
corrente é validar que a máquina está correta, otimizada e cientificamente defensável. O porte está
completo e standalone, e **duas famílias reproduzem a referência** sob protocolo pareado, cada uma
com manifesto e evidência commitados.

## 2 · O que está provado

### Reprodução contra a referência, sob protocolo pareado

| família | Δ contra a referência | proveniência |
|---|---:|---|
| **região** | **+0,054 pp** | ✅ `waves/ref_parity_al.toml`, partição verificada IDÊNTICA por hash nos 5 folds |
| **categoria** | **+0,031 pp** (AL) · **+0,058 pp** (AZ) | ✅ `waves/parity_cat_flat{,_az}.toml` + `evidence/parity_cat_flat.json` |

Os dois Δ estão dentro do piso de ruído (0,034 pp entre sorteios de substrato; 0,02–0,05 pp entre
sessões compiladas). A referência sai dos rundirs que o `PROVENANCE.md` do v18 lista, com os valores
por fold lidos deles — o Δ é a subtração de dois artefatos nomeados, não de um JSON e de uma
lembrança.

> **Nota de processo, mantida de propósito.** Esta alegação foi publicada em 19-08 **sem manifesto e
> sem evidência**, rebaixada no mesmo dia quando uma auditoria apontou, e reposta aqui por uma wave
> **prospectiva** — manifesto commitado antes da execução, rodada por `wave run`, substrato
> declarado, comparador nomeado. Os números novos batem com a prosa antiga (+0,03/+0,06 contra
> +0,031/+0,058), o que é sorte e não método: se não tivessem batido, teríamos descoberto que a
> prosa estava errada. A ordem certa é medir e então afirmar.

### Independência do repositório antigo

Do corpus bruto + shapefile até modelos treinados, sem nada produzido pelo `PoiMtlNet`. Auditado:
zero import, zero `sys.path`, zero caminho fixo. Os dados primários (gowalla, massive steps,
shapefiles, check-ins) vivem numa fonte única em `/Users/vitor/Desktop/mestrado/data/`, consumida por
symlink pelos dois repos.

### Um substrato só (v19)

A torre de região lê o **mesmo** substrato forward-only que a de check-in. Antes lia um substrato
bidirecional separado (v14) — herança da referência, onde isso era um symlink. Autorizado por
medição ANTES de deletar: efeito do grafo +0,122 pp (erro-padrão 0,108), indistinguível de zero. O
v14 ficou **arquivado** em `576f7b85`, não amputado, porque a avaliação contra a dissertação precisa
poder atribuir diferenças.

### O déficit de região, achado e fechado

A validação encontrou −0,9 pp em região com substrato construído do zero. Rastreado até ser **do
construtor, não do sorteio** (4 sorteios, desvio entre eles 0,034 contra distância 0,78), e daí até
três divergências do POI2Vec — corrigidas e atribuídas uma a uma:

| divergência | ganho |
|---|---:|
| 3 · ponderação do objetivo | +0,012 (ruído) |
| 1 · negativos duros | **+0,563** |
| 2 · regularizador de hierarquia | **+0,282** |

Região saiu de 73,84 para 74,70 contra o incumbente de 74,64. **Isso é paridade, não superioridade:
foram correções de migração — bugs meus — e não melhorias sobre a dissertação.**

A DIVERGÊNCIA 0 do Delaunay também fechou, e é a primeira parte do substrato que reproduz o artefato
bancado **bit a bit**: 35 519 arestas, orientação idêntica, zero invertidas.

## 3 · Infraestrutura de proveniência (construída em 19-08, depois de uma auditoria constrangedora)

A campanha de medição inteira rodou de scripts de shell **fora do repo**. 46 estudos bancados contra
9 manifestos. O `test_studies_contract.py` não pegou porque guarda o conteúdo de `studies/`.

Consertado, e o princípio vale mais que as peças: **guarda em tempo de criação é disciplina, e
disciplina falha; guarda em tempo de consumo é prova.**

- **identidade de substrato** — a célula grava qual substrato leu; o resume invalida quando muda.
  Antes, duas células sobre substratos diferentes tinham fingerprints idênticos e o resume servia
  número velho como novo.
- **linhagem** — a célula grava se saiu de uma wave; o `assert_comparable` **recusa** as que não.
- **substrato declarado** — o manifesto diz qual substrato exige e a wave recusa rodar sobre outro.
- **manifestos retroativos** — 10, verificados: cada um resolve para o fingerprint que a célula
  bancada gravou. 13 conferem, 0 divergem.
- **artefatos congelados** — um teste varre TODA receita e TODO manifesto, em vez de listas à mão.
- **predições sempre guardadas** — desde 19-08, `train` com `--split-seed` grava as linhas do fold
  externo automaticamente. Só o escore é racionado. Não existe mais "queria o número e tenho que
  rodar tudo de novo".

⚠ Migrações assimétricas de propósito em todos: ausente avisa, presente-e-diferente invalida. Sem
isso, toda célula bancada antes do campo — as **seladas** inclusive — seria retreinada, gastando uma
segunda leitura do teste externo.

## 4 · Aberto

1. **`mae_poi_target_dim` (#19) e o fatorial A2×A3 — MEDIDOS, decisão pendente.** Veredito do mae7:
   CORRIGIR. Do fatorial (Alabama, 1 semente, `studies/improvements/evidence/`): em **região nada é
   resolvido** contra o erro-padrão pareado; em **categoria** os três braços são reais e a combinação
   é MENOR que qualquer um sozinho — A2 e A3 **interferem**. Candidato limpo: **A3**. Entram na v20,
   que é decisão do autor e **não** entra na campanha `v19_defence` (ela afasta da dissertação de
   propósito).
2. ~~**Contrato de checkpoint (#12).**~~ **FEITO** — `docs/TELEMETRY_GUIDE.md`, seção "O contrato de
   checkpoint": oito garantias e quatro coisas que um consumidor não pode assumir.
3. ~~**Registro de divergências em três colunas (#9).**~~ **FEITO** —
   `docs/DIVERGENCE_REGISTER.md`. Correção de migração ⧸ defeito reproduzido ⧸ melhoria real, com o
   caso do POI2Vec como exemplo do erro que ele impede.
4. **Avaliação contra a dissertação (#17).** Desbloqueada — todo número citado hoje sai de estudo
   com manifesto.
5. **Backlog pré-campanha (#23 fechado, resíduo).** ~25 estudos anteriores ao campo de fingerprint,
   triados em `STUDY_LEDGER.md`. Deliberadamente **não** manifestados: não passam na barra que deu
   sentido ao retrofit, e manifesto que parece prova sem ser é pior que nenhum.

6. **⚠ `--confirmatory` nunca rodou em dado real (21-08).** O caminho de RECUSA está testado por
   unidade e por mutação; o caminho **feliz não** — nenhum par está no livro, porque nenhum `compare`
   aconteceu, então a pontuação do fold externo e a impressão do número **nunca foram exercitadas**.
   "Construído e nunca executado" é o estado que envelhece mal, e este está nele.

   O teste é barato e a ordem é forçada: rodar uma célula com `--split-seed` (predições ligadas),
   um `compare` — que registra o par —, e então `train --confirmatory` no mesmo par, conferindo que
   o número sai e bate com o do `compare`.

7. **⚠ `mtlcheck data fetch` só teve UM caminho exercitado (21-08).** O download de geometria do
   Census foi verificado com download real e os arquivos saem **bit-idênticos** aos que já estavam em
   disco (`.shp`, `.dbf`, `.prj` de Alabama).

   **Não exercitados:** `--city` (Massive-STEPS, precisa do pacote `datasets` e nunca foi chamado) e
   `--gowalla` (SNAP, ~1 GB, nunca foi chamado). As contagens do Massive-STEPS estão conferidas
   contra o repositório — Istambul dá 544 471, igual ao corpus local — mas conferir a tabela não é
   exercitar o download.

8. **Campanha `v19_defence` — pronta, aguardando substratos.** Manifesto de 54 células escrito e
   verificado (`studies/v19_defence/waves/campaign.toml`). Falta o bloco `[substrate.identity]` com
   os fingerprints de IST/FL/CA/TX, que a sessão parceira está construindo. ~33–35 h com a sonda.

9. **Datasets de desenvolvimento e validação — DECIDIDOS e documentados** (`EVALUATION_METHOD_GUIDE`
   §7.5b). Dev: AL + IST + FL + CA. Fechados para o ciclo v21: AZ + TX + Jakarta. **Jakarta não está
   em disco** — precisa de `mtlcheck data fetch --city Jakarta`, caminho nunca exercitado (item 7).

## 4.1 · Decisões do autor, 2026-08-21

| decisão | veredito |
|---|---|
| **etapa 3 da campanha (`mtlcheck compare`)** | **PROPÓSITO aprovado, DISPARO ainda não.** ⚠ corrigido 23-08 — ver a nota abaixo, a linha anterior dizia "AUTORIZADA" e contradizia o `AGENT_PROMPT.md` §5 |
| **v20** | **congelada como decisão futura.** Documentar em `studies/improvements/`, não mexer em mais nada agora |
| **errata do R14** | corrigir no ledger. Nota do autor: **a errata não é usada no documento principal**, então o custo de não corrigir era menor do que parecia |
| **emenda datada ao protocolo congelado** | **pendente** — ver abaixo |

### ⚠ A etapa 3: o que o autor autorizou, textualmente

Corrigido em **2026-08-23**, e a correção veio de outra sessão indo à fonte primária depois que eu
afirmei a ela que a etapa 3 "já estava autorizada". Não estava, não daquele jeito.

O que o autor escreveu, na íntegra, em 21-08:

> "Uai a etapa 3 fazer o compare é o esperado, queremos reportar esses dados nad defesa com o novo
> protoloco de evaliaçõa mais correto."

Isso **aprova o propósito** e responde a uma pergunta minha que tratava a etapa 3 como se fosse
dúvida — o "Uai" é justamente ele dizendo que não era. **Não é um disparo**, por dois motivos que
não se resolvem por leitura generosa: foi dito **antes de a campanha existir**, sobre uma matriz que
ninguém tinha visto; e o ato é a **leitura do teste externo dos seis conjuntos, uma vez, sem
desfazer**. Aprovar o plano e liberar o gatilho são coisas diferentes quando o gatilho é de via
única — é para isso que o livro de leituras e o `--confirmatory` existem.

**A regra que vale é a estrita**, que já estava certa em `studies/v19_defence/AGENT_PROMPT.md` §5:
não rode `compare` sem autorização explícita do autor, dada com a matriz completa à vista.

A lição, e ela é a mesma que o guia §0.2 registra: **eu comprimi "o autor quer isso e é o objetivo"
em "AUTORIZADA"**, e a versão comprimida foi a que viajou para outra sessão como fato. A frase
original estava a um `grep` de distância o tempo inteiro.

### A emenda, para quem retomar isto

O `docs/plans/EVALUATION_PROTOCOL.md` é o pré-registro, e a defensibilidade dele vem de **não ter
mudado** — o git prova a data. Mas ele afirma (§9.4, §4b) que CA/TX estão intocados e carregam peso
confirmatório, e isso é **falso**: a nota da tabela da dissertação diz que o batch size foi buscado
em todos os conjuntos, e a busca de LR cobriu quatro dos seis, **incluindo o Texas**.

O §12 do próprio protocolo manda registrar qualquer mudança como emenda datada, porque um
pré-registro que muda em silêncio não é pré-registro.

**As duas saídas:** emendar (admite por escrito um erro de premissa, e demonstra o mecanismo
funcionando) ou não emendar (o documento fica literalmente intocado, e passa a conter uma afirmação
falsa que a banca pode encontrar).

**Recomendação registrada:** emendar. A emenda é o mecanismo que o próprio protocolo especifica para
este caso, e "achamos um erro na nossa premissa e registramos" responde melhor que ser perguntado
sobre a contradição. O guia já sinaliza o conflito; o protocolo continua intocado à espera desta
decisão.

## 4.2 · Tarefas futuras — o que fica para depois da defesa

1. **Testar o caminho feliz do `--confirmatory`.** Só o caminho de RECUSA está exercitado. O feliz
   depende do primeiro `compare` existir, então ele **fecha sozinho** na etapa 3 da campanha — mas
   trate a primeira execução como teste, não como rotina.

2. **Exercitar `mtlcheck data fetch --city` e `--gowalla`.** Nunca chamados. O `--state` (geometrias
   do Census) foi verificado com download real e sai bit-idêntico ao disco. **A Jakarta depende do
   `--city`**, e ela é o único conjunto de validação genuinamente limpo do desenho de §7.5b do guia.

3. **Backfill do livro de leituras.** AL/AZ/IST foram lidos em 2026-08-18, antes do livro existir, e
   não estão registrados — aquelas células antecedem o campo `science_fingerprint`. A recusa do
   `--confirmatory` já diz isso e aponta o `SEALED_BRIDGE_READ.md`, mas a regra de backfill
   (§7.10 do guia) nunca foi aplicada.

4. **A decomposição do §8a.** `eval/optimism.py` existe, tem dez testes, e **nunca rodou** — exige
   `retain_checkpoints = "every"`, que a campanha não usa. Enquanto não rodar, a frase defensável
   continua sendo "o checkpoint joint único entrega X pp a menos que dois dedicados, cada um no seu
   melhor", e **não** "a MTL custa X pp".

5. **Limpar os restos de célula parcial.** `cat-alabama-p0s0`, `cat-arizona-p0s0` e `cat-texas-p0s0`
   têm checkpoints órfãos sem `result.json`, das ondas mortas ao serializar em 21-08. O resume os
   trata corretamente como não-feitos; é disco, não correção.

   **Por que é seguro re-executar por cima** (verificado em 21-08, duas leituras independentes):
   `_already_done` só pula com `result.json` presente e parseável; `_train_cell` não tem resume por
   fold, itera os cinco incondicionalmente; `_write` é atômico em nome fixo (`fold{N}_selected.pt`),
   então sobrescreve. **Mas isso se apoia em duas condições, e vale saber quais são**, porque a
   frase "nada do estado parcial sobrevive" é mais forte que o código:

   - `write_manifest` funde por fold-id e **só despeja a entrada velha se a nova for não-vazia**
     (`if entry:`). Sob `retain_checkpoints = "selected"` o `selected()` sempre dispara, então toda
     entrada é não-vazia e a fusão de fato substitui as cinco. Com uma política que possa não
     reter nada num fold, a linha velha sobreviveria ao lado das novas.
   - `write_manifest` **retorna cedo quando `policy == "none"`**. Se um dia uma célula parcial for
     re-executada com retenção desligada, o índice velho fica intacto em disco descrevendo pesos
     que ainda existem — e um leitor confia no índice, que é justamente o que ele existe para
     evitar. Não é o nosso caso (as três células declaram `"selected"` nas duas execuções), e
     **não se mexe nisso com campanha rodando**; fica registrado para quando mexer for barato.

   Na prática o caso concreto é ainda mais simples que as duas condições: a `wave-19` verificou em
   disco que as células parciais têm **só os `.pt`** — sem `predictions.parquet`, sem
   `checkpoints/manifest.json`. A fusão nem chega a rodar contra um índice velho, porque índice
   velho não existe. `predictions_mod.write` e `write_manifest` são chamados **depois** do laço de
   folds (`cli.py:452-485`), e o processo morreu dentro dele.

   **E isso enuncia uma propriedade da campanha que vale saber:** o comentário em `cli.py:429`
   registra a intenção de que "a cell that dies at fold 4 keeps folds 0-3". Os **pesos** de fato
   sobrevivem, escritos por fold. Mas as predições, o `result.json` e o índice não — e como não há
   resume por fold, os pesos retidos **não têm caminho de resgate**. Uma célula é tudo-ou-nada: o
   que morre no fold 4 de 5 refaz os cinco. Não é bug, e não muda nada do que está rodando; muda o
   que se deve esperar de uma queda no TX, que é a célula mais longa da fila.

## 5 · Fatos medidos que qualquer trabalho futuro deve respeitar

- **Piso de ruído entre sorteios de substrato: 0,034 pp.** Nada abaixo disso é interpretável.
- **Execuções compiladas não são bit-reprodutíveis entre sessões** — 0,02–0,05 pp.
- **O protocolo aninhado e o plano não se comparam.** Em AL/região a diferença é 3,66 pp, nove vezes
  a margem de equivalência. Só subtraia células que compartilham `eval_stream`.
- **Dispersão entre folds não é comparável entre estados.** A de AZ/categoria é 2,26 no aninhado e
  1,18 no plano; a de AL faz o caminho inverso. Investigado: não é `lr`, não é partição, não é ruído.
- **A representação varia enormemente entre sementes e o desempenho a jusante não.** Cosseno ~0,4
  entre sorteios, e 0,03 pp de diferença no fim. Por isso cosseno não responde "o substrato serve".
- **"O substrato é causal" é FALSO** e continua sendo. O forward-only fecha o canal linha a linha
  (os 28,63 pp); o substrato segue treinado uma vez sobre o corpus inteiro, sem split de fold.

## 6 · O que já foi tentado e não funcionou

- Rodar a main da referência sem `MTL_RAM_HEADROOM_GB=2`: o guard exige 16 GB fixos (R13).
- Inferir custo de `compile` de duas células bancadas: deu 0,4 %, o A/B controlado deu 24,4 %.
- Comparar substratos por cosseno: mede se é o mesmo sorteio, não se serve.
- Verificar uma mudança de dataclass importando o `cli`: ele importa o `result` preguiçosamente, o
  import passou, e o erro só apareceu na GPU depois de 8 min construindo substrato.
