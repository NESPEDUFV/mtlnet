# Rodar na `nespedgpu` — o que já deu errado, e como não repetir

> Cada item aqui é um erro que **aconteceu neste projeto**, com o custo que teve. Não é conselho
> genérico de SSH. Se algo parecer óbvio demais para estar escrito, é porque custou tempo a alguém.

---

## 0 · O mapa

| | |
|---|---|
| host | `nespedgpu` (`ssh nespedgpu`) |
| GPU | NVIDIA RTX 6000 Ada Generation, 46 GB, `sm_89` — **trocada em 25-08**; era uma A40 (`sm_86`) |
| driver | 580.173.02, CUDA 13.0 |
| deploy do código | `/dados/poimtlnet/mtlcheck` |
| dados brutos | `/dados/poimtlnet/data` |
| execuções | `/dados/poimtlnet/runs` |
| substratos | `/dados/poimtlnet/artifacts*` |
| venv | `~/.venv` — Python 3.12, torch 2.11.0+cu128 |

⚠ **O `arch_list` do torch não lista `sm_89`, e mesmo assim a placa nova funciona.** O torch de lá foi
compilado para `['sm_75','sm_80','sm_86','sm_90','sm_100','sm_120']` e a RTX 6000 Ada é `sm_89` — ler
essa lista e concluir "incompatível" seria errado. O CUDA garante compatibilidade binária **para
frente dentro da mesma major**, então o cubin de `sm_86` roda em `sm_89`. Verificado em 25-08 com
kernel de verdade, não com `is_available()`: matmul 8192², backward, 20 passos de AdamW, autocast
bf16 e TF32, todos limpos, e uma célula `cat` do Alabama a 100 % de util / 4006 MiB / 299 W.

**Ao trocar de GPU, não confie em `torch.cuda.is_available()`.** A falha de arquitetura
(`sm_XX is not compatible with the current PyTorch installation`) às vezes só aparece no **primeiro
kernel**, e a suíte de testes roda em CPU — ela não prova nada sobre isto. O teste que vale é uma
célula curta num estudo `scratch*`, com `nvidia-smi` amostrando em paralelo.

⚠ **Amostre `nvidia-smi` no MESMO shell da execução, num laço de ~0,3 s.** Um `ssh` separado com
`sleep 4` mediu **0 % e 8 MiB** durante uma célula que de fato saturou a placa — a janela de 15 s
passou inteira entre duas amostras, e o resultado parecia prova de que a GPU estava ociosa.

⚠ **`/home` está a 91 % de 393 GB. `/dados` tem 2,5 TB a 11 %.** Nada de execução escreve em `/home`.
Exporte sempre os três roots:

```bash
export DATA_ROOT=/dados/poimtlnet/data
export ARTIFACTS_ROOT=/dados/poimtlnet/artifacts_<seu-escopo>
export RUNS_ROOT=/dados/poimtlnet/runs
```

**O `DATA_ROOT` esquecido já quebrou uma execução completa de Alabama** depois de o substrato estar
pronto — o erro só aparece na etapa de treino.

⚠ **`ARTIFACTS_ROOT` decide QUAL substrato os números descrevem, e há onze candidatos.** Para a
campanha `v19_defence` o certo é **`/dados/poimtlnet/artifacts_final`** — conferido em 25-08 como o
único cujos seis substratos batem com as seis identidades que os manifestos declaram, sob
`substrate/check2hgi_v18/`. Os outros dez
são sósias com identidade diferente, e `/dados/poimtlnet/artifacts` — o nome óbvio — é pior: um
andaime de **symlinks** para `output/check2hgi_design_k_resln_mae_l0_1/`, um engine **diferente**,
sem `manifest.json`.

Até 25-08 apontar para ele apenas **avisava**, porque a conferência de identidade degradava para
WARNING quando o disco não tinha manifesto; a wave treinaria sobre o substrato errado sob o nome do
estudo e não falharia. Hoje isso levanta `SystemExit`. Se você receber essa recusa, o conserto é
apontar `ARTIFACTS_ROOT` para o substrato que este código construiu — não tirar a conferência.

Descubra qual raiz é qual sem adivinhar:

```bash
~/.venv/bin/python -c "
import json, glob, sys; sys.path.insert(0, 'src')
from mtlcheck.substrate.identity import digest
for p in sorted(glob.glob('/dados/poimtlnet/artifacts*/substrate/*/alabama/manifest.json')):
    print(f'{p.split(chr(47))[3]:24s} {digest(json.load(open(p)))}')
"
```

---

## 1 · Invocação: use `python -m`

```bash
PYTHONPATH=src ~/.venv/bin/python -m mtlcheck.cli wave run studies/<x>/waves/<y>.toml
```

**NÃO** use isto, que circulou nos drivers por herança e não faz nada a mais:

```bash
~/.venv/bin/python -c "import sys; from mtlcheck.cli import main; sys.exit(main())" wave run ...
```

O idioma longo veio de um driver antigo e foi copiado por inércia por mais de uma sessão. Existe
inclusive um console script `mtlcheck` declarado no `pyproject`, só não instalado no venv de lá.

---

## 2 · ⚠ O venv da `nespedgpu` NÃO é o do projeto

| | Python | pandas | numpy | sklearn |
|---|---|---|---|---|
| `~/.venv` na `nespedgpu` | 3.12 | 2.2.3 | 2.0.2 | 1.8.0 |
| `uv sync` local | 3.12 | 2.3.3 | 2.4.6 | 1.9.0 |

São da mesma família (pinado em 20-08 justamente para isso), mas **não são idênticos**. Antes disso a
divergência era grave — o lock entregava Python 3.14 e pandas 3.0.5, uma pilha que **nunca produziu
número nenhum deste projeto**.

**Consequência prática:** um teste que passa aqui pode falhar lá, e vice-versa. Ver
[`RUNNING_STUDIES.md`](RUNNING_STUDIES.md) §7.

---

## 3 · ⚠⚠ `rsync` — o comando que mais estragou coisa

**O erro, real:**

```bash
rsync -a --delete src/ tests/ nespedgpu:/dados/poimtlnet/mtlcheck/     # ☠ NÃO
```

Com múltiplas origens, o `rsync` copia o **conteúdo** de cada uma para o destino. Isso:

1. despejou `src/mtlcheck/` na **raiz** do repo remoto, criando um pacote-sombra que passou a
   preceder o `src/mtlcheck` no `sys.path` (o `cwd` vem antes do `PYTHONPATH`);
2. e o `--delete` **apagou todo o resto** da árvore de deploy — `recipes/`, `studies/`,
   `pyproject.toml`, os drivers.

Nada científico se perdeu, porque `runs/` e `artifacts/` moram **fora** de `mtlcheck/`. Mas custou a
execução em curso e uma hora de reconstrução.

**A forma correta — uma origem, a árvore inteira, exclusões ANCORADAS, comparação por conteúdo:**

```bash
rsync -a --checksum \
      --exclude '/.git' --exclude '/.venv' --exclude '/runs' --exclude '/artifacts' \
      --exclude '__pycache__' --exclude '/data' --exclude '/scratch' --exclude '.DS_Store' \
      ./ nespedgpu:/dados/poimtlnet/mtlcheck/
```

⚠ **As barras iniciais não são estilo — são o conserto de um defeito que já custou um lançamento.**
Em rsync, um padrão sem barra casa **qualquer** diretório com aquele nome, em qualquer profundidade.
`--exclude 'data'`, escrito para o corpus bruto da raiz, casa também `src/mtlcheck/data/` — onde
`splits.py` mora. Em 25-08 o diretório inteiro ficou fora da sincronização, o remoto rodou com um
`splits.py` de outra revisão, e as seis células da wave morreram em 1 s cada com
`TypeError: build() got an unexpected keyword argument 'split_seed'`. O mesmo vale para `runs`,
`artifacts` e `.venv`: âncore todos.

⚠ **`--checksum` porque `-a` sozinho compara mtime e tamanho.** Uma edição que preserve os dois
passa despercebida.

**Confira depois por hash, nunca por `grep` de nome de campo** — um `grep` pelo símbolo novo diz
"consertado" com as duas árvores diferentes:

```bash
ssh nespedgpu 'sha256sum /dados/poimtlnet/mtlcheck/src/mtlcheck/data/splits.py'
shasum -a 256 src/mtlcheck/data/splits.py
```

**E nunca sincronize no meio de uma execução.** Cada nova invocação do CLI relê o disco, então uma
sincronização no meio troca o código entre etapas do mesmo driver.

---

## 4 · Execuções longas: destacadas, sempre

```bash
ssh nespedgpu 'cd /dados/poimtlnet/mtlcheck && \
  setsid nohup /dados/poimtlnet/<driver>.sh > /dados/poimtlnet/<driver>.log 2>&1 </dev/null &'
```

Sem `setsid nohup ... </dev/null &`, a execução morre quando o SSH cai. Para esperar, use um laço
`until` sobre um marcador no log — nunca `sleep` em primeiro plano.

Termine todo driver com uma linha-marcador (`echo "X DONE"`) e faça o laço procurar **ela e os erros**:

```bash
until ssh nespedgpu 'grep -q "X DONE\|Traceback" /dados/poimtlnet/x.log'; do sleep 60; done
```

Procurar só o sucesso deixa o laço rodando para sempre quando o driver estoura.

---

## 5 · Matar processo: o shell morre, o filho não

```bash
pkill -f driver.sh          # mata o shell; o python continua rodando e segurando a GPU
```

**Aconteceu**: um processo órfão de um sweep cancelado ficou competindo por CPU e fez o POI2Vec
levar **25 minutos onde leva 98 segundos** — 15× mais lento, e eu quase diagnostiquei como bug de
desempenho. Confira e mate o filho:

```bash
ssh nespedgpu 'pgrep -fa "driver.sh|mtlcheck.cli"'
ssh nespedgpu 'kill -9 <pid-do-shell> <pid-do-python>'
```

**Uma execução de cada vez.** O POI2Vec é CPU-bound e satura os núcleos; dois em paralelo não
dividem o tempo, multiplicam.

---

## 5b · ⚠ O orçamento de memória da GPU — build e treino COMPETEM

**A afirmação que custou 97 minutos:** *"o treino é GPU-bound, o build de substrato é CPU-bound,
então não competem pela GPU."* **É falsa.** O build tem duas fases e só a primeira é de CPU:

| fase do build | recurso |
|---|---|
| corpus, Delaunay, **POI2Vec** | **CPU** — satura ~12 núcleos, não toca a GPU |
| **treino do encoder Check2HGI, 500 épocas** | **GPU** — 10,9 M parâmetros, até ~18 GB |

A placa tem **46 GB** — a A40 tinha, e a RTX 6000 Ada que a substituiu também, então os números
abaixo seguem valendo. Medido em 2026-08-21:

| | pico |
|---|---:|
| uma wave de campanha (FL, três famílias) | **27,1 GB** |
| build do substrato da Califórnia (169 k lugares) | **~18,2 GB** |
| soma | **45,3 GB — não cabe** |

Os **27,1 GB da wave são estáveis entre as famílias** — medido ao longo de `cat`, `reg` e as duas
células `joint` da Flórida, o uso não se moveu. É contra-intuitivo (a `joint` custa ~4× o tempo de
parede por fold) e vale saber: **o que a família muda é o wall-clock, não a memória.** Planeje o
orçamento pela wave, não pela célula. (Medido pela sessão `wave-19`, 2026-08-21 — a cautela oposta,
minha e dela, estava errada e só a medição resolveu.)

O build da Califórnia morreu de `torch.OutOfMemoryError` aos **5826 s (97 min)**, pedindo 776 MiB
com 524 MiB livres — depois de já ter passado por toda a fase de CPU. **O trabalho perdido é
integral: não há retomada.**

**Antes de lançar um build junto com um treino, meça:**

```bash
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader   # quem está segurando
```

Regra prática: um estado grande (>150 k lugares) precisa de ~18 GB e **não** cabe ao lado de uma
campanha. Um estado pequeno (Istambul, 42,8 k) cabe em ~19 GB livres com folga.

`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` reduz a fragmentação do **seu** processo e compra
alguma margem — não resolve falta real de memória.

⚠ **E lembre da contenção de CPU junto (§5): dois POI2Vec simultâneos dividem os 32 núcleos pela
metade.** Num mesmo dia estes dois erros custaram, somados, mais de duas horas: o de CPU dobrou o
tempo de dois builds, o de GPU apagou um build inteiro perto do fim.

---

## 5c · ⚠ Rodar células em paralelo NÃO acelera nada — mede-se pior

A pergunta aparece toda vez que se olha para 46 GB e uma célula que usa 4: *dá para rodar o `cat` e o
`reg` juntos?* **Dá, e não adianta.** Medido em 25-08 na RTX 6000 Ada, Alabama, 5 folds:

| arranjo | paralelo | sequencial equivalente | veredito |
|---|---:|---:|---|
| `cat` + `reg` (AL) | 106 s | 103 s | 3 % **pior** |
| `reg` + `joint` (AL) | 164 s | 166 s | empate |
| `cat` AL + `cat` AZ | 236 s | 229 s | 3 % **pior** |
| 2 × `cat` (AL) | 162 s | 148 s | 9 % **pior** |
| 3 × `cat` (AL) | 242 s | 222 s | 9 % **pior** |
| 4 × `cat` (AL) | 319 s | 296 s | 8 % **pior** |

A concorrência é real, não um erro de medição: os processos foram contados vivos ao mesmo tempo e a
memória somou (4054 MiB para uma célula, 8097 para duas, 12140 para três, 16184 para quatro). O que
acontece é que **uma única célula já satura a placa** — o driver reveza os contextos, o trabalho
total se conserva e você paga a troca de contexto por cima. A curva é plana em ~80 s por célula de
`cat` para qualquer N.

**Consequência para a campanha: enfileire, não paralelize.** O único ganho possível seria por CPU
(há 32 núcleos e 125 GB), e a fase de CPU — corpus, Delaunay, POI2Vec — não é onde o tempo está.

⚠ **E o `joint` sozinho já pede 21,6 GB no Alabama**, o menor conjunto. Dois `joint` concorrentes
seriam 43 dos 46 GB — cabe na régua e não compra nada, com risco de OOM se o conjunto for maior.

---

## 6 · Aspas em `ssh` + `python -c`

Aninhar aspas em `ssh host 'python -c "..."'` quebra de formas silenciosas e confusas. **Escreva o
script num arquivo, copie e execute:**

```bash
cat > /tmp/x.py <<'PY'
...
PY
scp -q /tmp/x.py nespedgpu:/tmp/ && ssh nespedgpu '~/.venv/bin/python /tmp/x.py'
```

O `<<'PY'` com aspas impede a expansão local de `$`. Sem elas, o shell come as variáveis do script.

⚠ **O shell que o `ssh` abre lá é `dash`, não `bash`.** `time` é palavra-chave do bash e **não
existe** em dash; `bc` não está instalado. Um `ssh nespedgpu 'time ...'` falha com
`sh: 1: time: not found` **antes de rodar qualquer coisa** — o que parece a execução ter quebrado.
Para cronometrar, embrulhe em `bash -lc` ou marque com `date +%s`.

---

## 6b · Duas armadilhas do CLI que custam uma execução cada

**Os folds são 1-indexados.** `--only-folds 0` não é o primeiro fold: é
`ValueError: --only-folds [0] out of range for a 5-fold split`. O canônico de 5 folds é `1..5`.

**`DATA_ROOT` não exportado produz uma falha de teste que parece defeito de código.** Sem ele,
`test_the_region_join_is_derived_per_state_and_guarded` falha com
`FileNotFoundError: shapefile de alabama não encontrado em .../data/miscellaneous/...` — o caminho
relativo cai dentro do repo, onde não há shapefile. Diagnosticado em 25-08 como fantasma: com os
três roots exportados a suíte de lá fecha em **724 passando, 77 pulados, 1 xfail, 0 falhas**. Rode
sempre a suíte com o mesmo ambiente com que rodaria um treino, ou ela mente sobre o que está quebrado.

---

## 7 · Predições: sondagem × campanha

Este é o mais caro de errar, porque só aparece no fim.

| o que você está fazendo | flag |
|---|---|
| **sondagem** — viabilidade, 1 fold, "cabe na GPU?" | `--no-save-predictions` |
| **campanha** — a execução cujo número vai ser lido | **nada** (ligado é o default com `--split-seed`) |

Guardar as linhas do fold externo **não é ler o teste** — o ato racionado é o `compare`. Mas se a
campanha rodar com `--no-save-predictions` por cópia do driver da sondagem, ela produz **zero
material legível** e a leitura exige **retreinar tudo**.

**Teste de sanidade antes de qualquer campanha longa:** rode uma célula pequena e confirme que
`predictions.parquet` apareceu no rundir. Dois minutos.

---

## 8 · Tempos medidos, para planejar

Por fold, 5 folds por semente (`l1_large_states` e a campanha de 19/08) — **medido na A40**, a placa
que saiu em 25-08:

| estado | cat | reg | joint | por semente |
|---|---:|---:|---:|---:|
| Alabama | ~20 s | ~12 s | ~90 s | ~10 min |
| Florida | 258 s | 170 s | 1 093 s | 2,1 h |
| California | 599 s | 413 s | 2 504 s | 4,9 h |
| Texas | 783 s | 522 s | 3 244 s | 6,3 h |

**Na RTX 6000 Ada, medido em 25-08** (receitas `v19`, `split_seed = 0`, `seed = 0`; folds de regime,
sem o primeiro):

| estado | cat | reg | joint | por semente | razão vs A40 |
|---|---:|---:|---:|---:|---:|
| Alabama | 14 s | 5 s | 64 s | 8,4 min (504 s, medido) | **1,21×** |
| Florida | 189 s | 75 s | 770 s | 1,46 h (5 264 s, extrapolado de 2 folds) | **1,53×** |

⚠ **A razão cresce com o tamanho do conjunto — não reescale a tabela toda por um fator só.** O
Alabama ganha menos não porque a placa renda menos ali, mas porque o custo que **não** é fold — subir
o processo, `torch.compile`, escrever predições, ~17 s por célula — não encolhe com o hardware, e num
conjunto cujos folds duram 5 a 64 s ele é quase um quinto do relógio. Na Florida esse custo some no
ruído e o ganho por fold aparece limpo: `cat` 1,37×, `reg` 2,3×, `joint` 1,42×. Conjuntos maiores que
a Florida devem ficar em 1,5× ou melhor.

⚠ **O primeiro fold de cada célula paga o `torch.compile`.** No braço `joint` do Alabama o fold 1
levou 122 s contra 64 s dos demais — quase um minuto de compilação. Ao cronometrar, use os folds de
regime, não o primeiro, e lembre que o custo de compilação é pago **uma vez por célula**.

Memória medida na placa nova, para planejar: `joint` do Alabama **21,6 GB**, `joint` da Florida
**27,3 GB** — este último bate com os 27,1 GB que a wave da Flórida marcou em 21-08 na A40, o que
confirma que a troca de placa não mexeu no orçamento de memória do §5b.

Build de substrato: Alabama ~2 min; Florida ~25 min ponta a ponta (o treino do encoder é só ~2,5 min
— o resto é scaffolding e materialização, que escalam por número de **lugares**).

---

## 9 · Antes de commitar, depois de rodar

Se houver **qualquer** agente ou sessão ativa na mesma árvore, `git add -A` captura trabalho alheio
em voo. Já aconteceu: um commit gravou seis mutações de auditoria em `src/` e a suíte **não moveu um
número**. Ver [`../studies/porting_validation/INCIDENT_2026-08-19_commit.md`](../studies/porting_validation/INCIDENT_2026-08-19_commit.md).

Commite por caminho explícito, e leia o `git diff --cached --stat` **antes**. A pergunta é: *isto
que estou commitando é o que eu pretendia commitar, e nada mais?* Se aparecer arquivo que você não
tocou, **pare** — é trabalho de outro agente em voo.

> ⚠ **Esta regra não basta sozinha, e existe a prova.** Horas depois de eu escrever o parágrafo
> acima, eu e outra sessão rodamos `git add -A` na mesma árvore e **os commits cruzaram nos dois
> sentidos**: o conserto do `cli.py` foi parar dentro do meu commit sobre `identity.py`, e o commit
> que anuncia esse conserto não contém uma linha dele. Duas mensagens descrevendo conteúdo que não
> está nelas — inclusive uma que **afirma** excluir um arquivo que ela inclui.
> Registro: [`../studies/porting_validation/INCIDENT_2026-08-21_commits_cruzados.md`](../studies/porting_validation/INCIDENT_2026-08-21_commits_cruzados.md).
>
> O aviso estava escrito, era meu, e era daquela manhã. Não impediu nada. Junto com as outras quatro
> instâncias do dia — um aviso de `save_predictions` escrito duas horas antes da omissão, um teste de
> sanidade na família errada, uma conferência que olhava só a primeira célula, um digest constante —
> a lição é uma: **conhecimento não age; verificação age.** Rode o `--stat`; não confie em lembrar.
