# EXECUTION_WAVE.md — a onda fechada de California e Texas

**Trilha minha.** Desenho conhecido antes de rodar, cada arm preenche uma celula, o valor esta na
auditoria. A trilha de hypertuning (o agente no host) e separada e corre nos intervalos desta.

**Estado da GPU, medido 2026-08-12:** A40 com 46 GB, 0 processos de treino, 0% de uso, **37 GB
livres em disco** (91% ocupado — e o unico limite real da onda).

---

## 1 · O que cada arm fecha, e por que ele existe

Todos os arms usam `--seed 0 --folds 5` e a engine `check2hgi_v18`, o que os torna **pareaveis fold
a fold contra as celulas ja bancadas** em `joint_best_perfold.json`. Isso foi verificado: as celulas
bancadas sao por fold, semente 0, mesma engine, mesma receita.

> ## PENDENCIA QUE BLOQUEIA O ARM 1 EM TODOS OS DATASETS
>
> **Medido em 2026-08-13, e mais grave do que parecia.** A auditoria de parametros publicada em
> `storyline/audit/capacity_baseline_experiment.md:78-86` — de onde saem as larguras `d_model=480`
> (AL), `352` (CA), `hidden_dim=672` (AL), `752` (CA) — mediu a arquitetura **v17 dualtower**, como a
> propria tabela declara no cabecalho da coluna. Reconstruindo o modelo conjunto **atual**
> (`mtlnet_crossattn_dualtower`, com os defaults de treino: `feature_size=64`,
> `shared_layer_size=256`, `num_heads=8`, `num_layers=4`, `num_shared_layers=4`, blocos de
> cross-attention 2x4) as contagens sao outras:
>
> | dataset | n_regioes | conjunto v17 (publicado) | conjunto atual (medido) |
> |---|--:|--:|--:|
> | Alabama | 1.109 | 4.197.621 | **6.909.789** |
> | California | 8.501 | 5.151.189 | **8.809.533** |
> | Texas | 6.553 | — | **8.308.897** |
>
> Nenhuma decomposicao por submodulo do modelo atual reproduz o alvo de via de regiao de 2.466.542
> que o `POSTPONED.md` cita para Alabama (a via `next_poi` da 1.864.533).
>
> **Consequencia:** as larguras publicadas **nao pareiam capacidade no modelo atual**, nem em
> California. O arm executado com `d_model=352` em CA nao e um controle pareado.
>
> ## RESOLVIDO (decisao do autor, 2026-08-13): o alvo e o MODELO CONJUNTO INTEIRO
>
> Larguras derivadas contra o modelo atual, por busca sobre a contagem de parametros treinaveis:
>
> | dataset | alvo (conjunto inteiro) | `d_model` pareado | contagem | % do alvo |
> |---|--:|--:|--:|--:|
> | Alabama | 6.909.789 | **624** | 6.978.702 | 101,0% |
> | California | 8.809.533 | **528** | 9.004.686 | 102,2% |
> | Texas | 8.308.897 | **544** | 8.354.882 | 100,6% |
>
> ---
>
> ## 🔴 CORRECAO 2026-08-27 — a coluna "conjunto atual (medido)" NAO foi medida
>
> **Os numeros `6.909.789` (AL), `8.809.533` (CA) e `8.308.897` (TX) sao uma RECONSTRUCAO** feita a
> partir de defaults assumidos (`num_layers=4`, `num_shared_layers=4`, cross-attention 2x4), **nao
> uma leitura de execucao**. Os logs das corridas entregues dizem outra coisa:
>
> | dataset | tabela acima ("medido") | log de execucao v18_2 | razao |
> |---|--:|--:|--:|
> | California | 8.809.533 | **5.151.189** | 1,71x |
> | Texas | 8.308.897 | **4.899.897** | 1,70x |
>
> Fonte, verbatim, `v18_2/modal_runs/california_s7_lane_*/logs/california_s7_joint.out`:
> `('cat', …, 1731079) ('reg', …, 1835982) ('shared', …, 1584128)` — soma **5.151.189**, que e
> exatamente o valor que esta tabela rotula como *"v17 (publicado)"*.
> Texas, mesmo formato: `1731079 + 1584690 + 1584128 = 4.899.897`.
>
> 🛑 **As duas colunas estao trocadas de rotulo.** O que a tabela chama *"conjunto v17
> (publicado)"* e o que o modelo entregue **de facto executa**; o que ela chama *"conjunto atual
> (medido)"* e uma reconstrucao com hiperparametros que nao correram.
>
> ⚠ **CONSEQUENCIA QUE PRECISA DE DECISAO — nao e correcao de numero.** As larguras pareadas
> `d_model` **624 (AL) · 528 (CA) · 544 (TX)** foram derivadas por busca **contra estes alvos
> inflados**. Se o alvo real e ~1,7x menor, entao o braco dedicado chamado *"pareado"* recebeu
> **cerca de 1,7x o orcamento do modelo conjunto, nao o mesmo**.
>
> **Isso muda a leitura do controle de capacidade** (`P1_capacity_region.md`, e o slide `B-P1` da
> Serie B): *"capacidade pareada remove a vantagem em California"* passaria a ser *"um dedicado com
> ~1,7x o orcamento supera o conjunto em California"* — **afirmacao diferente, e mais fraca contra o
> modelo conjunto**. ⚠ **Vai na mesma direcao do Apendice G**, que ja registra que o braco largo
> recebeu *"mais que o dobro"* e ainda assim pontuou **abaixo**.
>
> 🛑 **NAO alterado aqui:** as larguras, o veredito do controle, nem os slides. **Isto e
> registro do defeito e da sua consequencia; a decisao e do autor.**
>
> ---
>
> E o alvo mais conservador dos dois: da ao dedicado **todo** o orcamento do modelo conjunto, de modo
> que qualquer folga remanescente nao possa ser atribuida a parametros.
>
> **O arm de 352 continua ate o fim, como ponto de curva.** Ele fica em 5.014.942 parametros, 1,54x o
> dedicado estreito e 57% do alvo. Se a folga do conjunto sobreviver **a 352 e a 528**, a afirmacao e
> uma curva e nao um ponto, o que e mais forte. Ele nao e citado como o controle.

| # | arm | flag | h (CA) | h (TX) | fecha |
|---|---|---|--:|--:|---|
| 1 | dedicado regiao, cabeca alargada | CA `--override-hparams d_model=352`; **TX a derivar** | 2.3 | 2.6 | **P1**: a vantagem de regiao e capacidade ou partilha |
| 2 | trunk com KV destacado | `--model-param detach_crossattn_kv=True` | 4.9 | 6.2 | **CONTRATO**: isola a direcao da transferencia |
| 3 | trunk severado | `--model-param disable_cross_attn=True` | 4.9 | 6.2 | **P4**: substitui a triagem de 1 fold |
| 4 | mistura identidade | `--model-param identity_cross_attn=True` | 4.9 | 6.2 | decompoe o arm 3, so importa se ele mover |
| 5 | joint ref + diagnostico | `MTL_TRAIN_DIAGNOSTICS=1` | 5.6 | 7.2 | cobertura do apendice do cosseno em CA/TX |
| 6 | dedicado categoria alargado (so TX) | **largura a derivar** (`752` e a de California, nao a de Texas) | — | 2.4 | completa o controle de capacidade |

**Total dos seis, uma semente: 53,4 h.** E por isso que a ordem importa mais que a lista.

**Uma economia verificada:** os arms 2, 3 e 4 nao precisam do arm 5 como comparador. A celula
bancada de v18 ja e o comparador pareado, por fold, na mesma configuracao. O arm 5 so existe pelo
diagnostico de gradiente, que e uma pergunta diferente (cobertura do apendice) e nao um controle.

---

## 2 · A ordem, por valor decidido por hora

**Bloco A — 9,8 h. Fecha a pergunta que muda a interpretacao do resultado principal.**

Fila enfileirada em `wave_logs/driver_capacity_v2.sh`, **sequencial de proposito**: os arms nao
disputam a GPU entre si, e o driver espera a sonda terminar antes de comecar.

1. **P1 California, `d_model=528`** (~2,3 h) — o controle pareado. CA e onde a vantagem de regiao e
   maior.
2. **P1 Texas, `d_model=544`** (~2,6 h) — o segundo dataset com vantagem. Sem ele, P1 e um dataset so.
3. **KV destacado em California** (~4,9 h) — isola a direcao da transferencia. Nao depende de largura
   nenhuma: e um flag de ablacao sobre a receita conjunta ja fixada, comparado fold a fold contra a
   celula bancada.

Em curso e fora da fila: o arm de `d_model=352` em CA, mantido como ponto de curva (ver acima).

**Guardas no driver** (`wave_logs/driver_capacity_v2.sh`), e o que elas de fato garantem:

- **Disco.** Cada arm mede o espaco livre **antes** de comecar e devolve 9 sem iniciar se estiver
  abaixo de 15 GB. O retorno **e checado pelo chamador** (`if run_arm california 528; then ...`), de
  modo que Texas so comeca se California tiver concluido com retorno zero.
- **Falha propaga.** Um arm que termine com retorno diferente de zero, por qualquer motivo, encerra a
  fila em vez de deixar o proximo subir sobre um estado desconhecido.
- **Registro.** Inicio, fim, codigo de retorno e disco livre em cada transicao, em
  `wave_logs/DRIVER_capacity.log`.

> **Correcao de 2026-08-13.** A primeira versao deste driver anunciava a guarda de disco mas nao a
> aplicava: `run_arm` devolvia 9, e como o script nao tinha `set -e` e as duas chamadas eram
> instrucoes consecutivas sem checagem, o retorno era descartado e Texas subiria de qualquer forma.
> A versao em uso checa o retorno. O defeito foi encontrado por revisao, nao por ter disparado.

Se so houver tempo para um bloco, e este. Ao fim dele voce sabe se a vantagem de regiao e capacidade
ou construcao, e sabe em que direcao (se alguma) a transferencia corre.

**Bloco B — mais 17,3 h (cum. 27,1 h). Fecha P4 no lugar certo.**

4. Trunk severado em CA (4,9 h) e em TX (6,2 h) — cinco folds sobre a preparacao atual, substituindo
   a triagem de uma dobra que rodou sobre o substrato com o vazamento.
5. KV destacado em TX (6,2 h) — confirma a direcao no segundo dataset.

**Bloco C — mais 12,8 h (cum. 39,9 h). Fecha a cobertura do apendice do cosseno.**

6. Joint de referencia com diagnostico em CA (5,6 h) e TX (7,2 h).

**Bloco D — mais 13,5 h (cum. 53,4 h). Marginal.**

7. Mistura identidade em CA e TX; categoria alargada em TX. So valem se o Bloco B mover algo, e o
   controle de capacidade em categoria ja tem Alabama e California dando o mesmo sinal.

---

## 3 · O que cada resultado obriga a dizer, escrito ANTES de rodar

Isto existe para que a escolha de redacao seja pela medida e nao pelo enquadramento preferido.

### P1 (arms 1)

- **Se o dedicado alargado chegar a menos de 0,3 pp do conjunto:** a vantagem de regiao e capacidade.
  A leitura honesta passa a ser *consolidacao*, nao sinergia: um modelo faz o trabalho de dois com o
  mesmo orcamento de parametros. **Isto e um resultado mais limpo que o atual**, porque hoje a
  discussao hedgeia entre duas explicacoes.
- **Se persistir folga de 1 pp ou mais:** a construcao conjunta acrescenta algo em vocabularios
  grandes que largura sozinha nao alcanca, e essa e a unica razao com evidencia para continuar
  estudando o desenho conjunto.
- **Entre 0,3 e 1,0 pp:** inconclusivo, e diz-se isso. Nao se promove a leitura preferida.

### O contrato do trunk (arms 2, 3, 4)

- **Se severar o trunk nao mover e o KV destacado tambem nao mover:** o trunk nao contribui nem
  aprende. A afirmacao defensavel passa a ser que a arquitetura **consolida** duas tarefas sem
  transferencia mensuravel. Isso e limpo, e nao uma derrota.
- **Se severar mover mas o KV destacado nao:** o que o trunk contribui e capacidade e caminho, nao
  gradiente compartilhado.
- **Se o KV destacado mover:** ha transferencia, e ela tem **direcao** — o que hoje a discussao so
  consegue hedgear.

---

## 4 · Limites operacionais

- **Disco em 37 GB.** Cada rundir do modelo conjunto em TX e o maior da casa. `--no-checkpoints` esta
  no comando do driver e deve continuar.
- **Nao escrever** em `output/check2hgi_dk_ovl/` nem em
  `output/check2hgi_design_k_resln_mae_l0_1/`, que o README de v18 protege.
- **Logs usam retorno de carro.** Um log lido cru parece vazio; passar por `tr '\r' '\n'`.
- **Checagem de sanidade de v18:** um numero de categoria proximo do valor anterior ao conserto
  indica caminho quebrado, nao resultado.
- **Veredicto so por teste pareado sobre os folds**, com condicoes, n, folds, sementes, teste, p e
  direcao. Nunca por media isolada.
