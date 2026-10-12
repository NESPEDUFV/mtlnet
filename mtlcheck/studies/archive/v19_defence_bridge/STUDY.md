# Estudo `v19_defence` — os dados da dissertação, reexpressos no protocolo novo

**Aberto 2026-08-21.** Decisão do autor. Defesa em **2026-08-28**.

## A pergunta

> Os mesmos seis conjuntos da dissertação, sob a **v19 congelada** e o protocolo de avaliação do
> mtlcheck — o que eles dizem?

Não é uma versão melhorada. É a versão **mais próxima da dissertação** que o mtlcheck produz, medida
com o instrumento correto.

⚠ **É a v19 e NÃO a v20, e a razão importa.** A v20 (`mae_poi_target_dim` 7 + o fatorial
Delaunay × POI2Vec) **afasta da dissertação de propósito** — é a terceira coluna do
[`DIVERGENCE_REGISTER`](../../docs/DIVERGENCE_REGISTER.md), melhoria real que quebra comparabilidade
por declaração. Aplicá-la aqui sabotaria o objetivo. Fica para depois.

Evidência de que a decisão não é hipotética — **fatorial completo, corrigido 2026-08-21**:

| braço (Alabama, 1 réplica) | região Acc@10 | categoria macro-F1 |
|---|---|---|
| A2 · unidades do Delaunay | −0,178 (ep 0,163) | **+0,141** (ep 0,059) |
| A3 · simetriza o POI2Vec | +0,162 (ep 0,134) | **+0,170** (ep 0,057) |
| A2 × A3 | +0,073 (ep 0,182) | **+0,116** (ep 0,108) |

⚠ **Uma versão anterior deste parágrafo dizia que os dois efeitos do A2 estavam "acima do piso de
ruído e em direções opostas". A metade da região não se sustenta.** O piso de 0,034 pp é entre
*sorteios de substrato*; a grandeza certa para um delta pareado é o seu erro-padrão, e −0,178 ± 0,163
é ~1,1 desvio — indistinguível de zero. **Em região, nenhum dos três efeitos é resolvido.** Em
categoria os três são reais, e a combinação (+0,116) é **menor que qualquer um sozinho**: os dois não
compõem, interferem.

Continua valendo que a v20 exige uma **decisão** e não uma aplicação — mas o eixo da decisão é
categoria, e o candidato limpo é o **A3**, não o A2. Ressalva que impede fechar: uma réplica, um
estado.

---

## 1 · ⚠ Esta campanha GASTA a leitura do teste nos seis conjuntos

Dito aqui, na abertura, e não em nota de rodapé.

É a leitura confirmatória do ciclo: **uma por braço, uma vez**. Depois dela, os seis conjuntos estão
lidos para a v19 e qualquer número novo sobre eles é reprodução, não leitura.

É o momento certo — v19 congelada, migração fechada, nada pendente que mudaria a receita. Mas é uma
vez, e o `POR_QUE_O_TESTE_ESPERA.md` explica por que não há segunda.

---

## 2 · Escopo

Alabama, Arizona, Istambul, Flórida, Califórnia, Texas. Os seis do artigo, nenhum a mais.

Os seis já informaram decisões — não é leitura sobre dado intocado, é leitura sob o protocolo correto
sobre os dados de desenvolvimento do programa. Quem citar estes números precisa dizer isso
([`EVALUATION_METHOD_GUIDE.md`](../../docs/EVALUATION_METHOD_GUIDE.md) §7.6).

---

## 3 · As quatro etapas

### Etapa 0 · Congelar a v19

Um commit datado fixando: a receita, a lista de braços, a lista de conjuntos, e as hipóteses da
família manchete com a ordem do gatekeeping (não-inferioridade → superioridade).

**Precede qualquer build.** É o que torna a leitura da etapa 3 confirmatória em vez de exploratória.

### Etapa 1 · Substratos — quatro faltam

`artifacts_final` tem **alabama** e **arizona** construídos por este pacote. Istambul, Flórida,
Califórnia e Texas hoje leem substrato **da referência**, não nosso.

Custo medido: a **Flórida levou ~25 min** ponta a ponta (corpus, Delaunay, POI2Vec, 500 épocas de
encoder, materialização de 1,27 M janelas). O treino do encoder foi ~2,5 min; o resto é scaffolding.
Istambul é menor; CA e TX escalam por número de lugares (169 145 e 160 938 contra 76 544 da FL).

**Estimativa: ~2 a 3 h para os quatro.**

### Etapa 2 · Treino

Três famílias × seis conjuntos, `inner_validation`, predições do fold externo persistidas e **não
lidas**.

> ### ⚠ NÃO passe `--no-save-predictions` aqui
>
> A sondagem do gate na Flórida usou esse flag, e estava **certo** lá: era uma medição de
> viabilidade e não havia motivo de tocar o fold externo.
>
> **Na campanha é o oposto, e é fatal.** Sem as predições persistidas, as 31 h produzem **zero
> material legível** e a etapa 3 exige retreinar tudo. É precisamente o custo que o desenho de
> persistir-mas-não-ler existe para eliminar.
>
> * **sondagem** (viabilidade, 1 fold) → `--no-save-predictions`
> * **campanha** (estas 31 h) → predições **LIGADAS**, que é o default quando há `--split-seed`.
>   Não passe flag nenhum.
>
> **Teste de sanidade — FEITO 2026-08-21, e a família importa.**
>
> ⚠ A versão anterior mandava rodar **AL/`cat`**. Esse teste **passa e não vê o modo de falha que
> importa**: o risco registrado no `EVAL_LAYER_REVIEW.md` era a família **joint** — duas correntes,
> caminho de captura próprio — produzir zero linhas enquanto `cat` grava normalmente. Um teste em
> `cat` não toca esse código.
>
> Executado na família certa (AL, `joint`, semente 0, fold 1, 94 s):
> `predictions.parquet` com **cat 19 265 + reg 19 265 = 38 530 linhas**, 222 usuários, uma única
> `selected_epoch` para as duas tarefas, `sealed: true`, `partition_hash` fixado e `train_labels`
> bancados por tarefa e por fold. **O bloqueio do `EVAL_LAYER_REVIEW` está fechado por execução.**
>
> Nota operacional: `--only-folds` é **1-based** (`--only-folds 1` é o primeiro fold); passar `0` dá
> "out of range for a 5-fold split".

**Réplicas — pela regra pré-registrada, não por escolha.** `docs/plans/EVALUATION_PROTOCOL.md:75`
fixava FL/CA/TX em **2** (`{0,7}`) *travado pela calibração da ponte*; AL/AZ/IST em **4**.
⚠ **A calibração foi computada em 24-08 e REPROVOU em região** — os três grandes vão a `{0,1,7,100}`
(protocolo §12.7, receita `recipes/analysis/v19_headline_s4.toml`). Ver [`STATE.md`](STATE.md). A justificativa é
medida: o desvio entre réplicas é 20–50× menor que a componente de fold/usuário nos grandes, então ir
a 4 encolheria a meia-largura em ≤ 0,06 pp e dobraria o wall-clock dominante.

Custo medido por réplica (do `l1_large_states`):

| conjunto | cat | reg | joint | por réplica |
|---|---:|---:|---:|---:|
| Flórida | 258 s | 170 s | 1 093 s | **2,1 h** |
| Califórnia | 599 s | 413 s | 2 504 s | **4,9 h** |
| Texas | 783 s | 522 s | 3 244 s | **6,3 h** |
| Alabama | — | — | — | ~10 min |

**Total ≈ 31 h de GPU** no desenho de duas réplicas, **+27 h** na escalada para quatro que o gate impôs em 24-08.

### Etapa 3 · A leitura

`mtlcheck compare`, uma vez, com Holm na família manchete e o gatekeeping sequencial.

✅ **DESBLOQUEADA 2026-08-21 — a flag `--confirmatory` existe** (`mtlcheck train --confirmatory`,
entregue pelo mtlcheck-2: declarada, verificada contra o livro de leituras, recusada na segunda para
um par (receita, conjunto) já lido). O texto abaixo descrevia o bloqueio quando ele existia.

~~BLOQUEADA até a flag confirmatória existir.~~ Sem ela a campanha termina em `inner_val` e alguém
cita como resultado — exatamente o que o §8 do guia descreve. Desenho fechado: declarada, verificada,
livro de leituras, recusa na segunda.

---

## 4 · O que este estudo NÃO faz

* **Não compara célula a célula com a tabela da dissertação.** Protocolo diferente e substrato
  corrigido; o §8 do guia existe para impedir a subtração.
* **Não valida em dado intocado.** Os seis são de desenvolvimento.
* **Não substitui a dissertação entregue**, que mantém os números do v18.

⚠ **Cuidado de defesa.** Se estes números forem à banca, não leve junto o vocabulário deste protocolo
("reserva", "selado", "gasto"). Um avaliador que ouvir "CA e TX são a nossa reserva" e ler a nota de
rodapé sobre o batch size encontra a contradição ao vivo — a mesma que foi corrigida em 21-08.

---

## 5 · Estado

| etapa | estado | bloqueio |
|---|---|---|
| 0 · congelar a v19 | **fechada** | — |
| 1 · seis substratos | **fechada** — identidades no `AGENT_PROMPT.md` §2 | etapa 0 |
| 2 · treino | **fechada** 23-08, 54/54 células | etapa 1 |
| 3 · leitura | **EXECUTADA em 3 de 6** (AL/AZ/IST, 24-08) · os grandes bloqueados pela escalada S=4 | etapa 2 |

> O estado corrente, com o resultado e o próximo comando, vive em
> [`STATE.md`](STATE.md) — esta tabela é o desenho, não o placar.

### A sequência, e por que ela não é só uma saída de prazo

As etapas **0 a 2 rodam agora**; a **3 espera** a flag confirmatória. Isso não é concessão ao
calendário — é o desenho funcionando. **Guardar as linhas nunca foi ler o teste**; o ato racionado é
o `compare`. Separar as duas coisas é exatamente o retorno da mudança que tornou as predições
persistidas por padrão.

Consequência prática: nenhuma das 31 h é desperdiçada se a flag atrasar. As predições ficam em disco,
não lidas, e a etapa 3 é uma pontuação sobre o que já existe — sem retreinar nada.
