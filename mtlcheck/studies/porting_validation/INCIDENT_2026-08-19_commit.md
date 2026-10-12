# Quase-acidente: um commit capturou seis mutações de auditoria

**2026-08-19, 19:16 → 19:25 local. Janela de 9 minutos. Nenhuma medição contaminada.**

## O que aconteceu

O commit `a85a42f4` ("abre o estudo improvements") gravou **seis mutações** em cinco arquivos de
`src/`, feitas por agentes de auditoria que estavam testando testes por mutação:

| arquivo | o que o commit gravou | o que isso desfazia |
|---|---|---|
| `substrate/poi2vec.py:337` | `n_negatives = NEGATIVES_PER_CONTEXT` | divergência 3 |
| `substrate/poi2vec.py` | linha `loss + model.hierarchy_loss()` **apagada** | divergência 2 — **−0,282 pp em região** |
| `substrate/delaunay.py:195` | `np.concatenate([...])` | divergência 0 — 2,3 % das arestas invertidas |
| `config.py:113` | `mae_poi_target_dim = 7` | veredito era "entra na leva", não "muda o default" |
| `data/dataset.py` | `provenance = {}` | o conserto da tarefa #20 |
| `cli.py` | `produced_by: "wave"` incondicional | o guard de linhagem |

Em dois casos o **comentário logo acima explicava por que o código tinha de ser o oposto** do que
ficou ali.

## Por que passou

`git add -A && git commit` enquanto agentes mutavam `src/`. Eles restauram ao terminar — e eu
commitei no meio. Mesma classe do `rsync --delete` malformado de mais cedo: comando amplo, sem
olhar o que ia junto.

**E a suíte não moveu um número.** `pytest` deu o mesmo resultado com e sem as seis mutações. Esse é
o achado que sobrevive ao incidente: **os testes cobrem os consumidores e não a fiação.** Cinco
achados independentes da auditoria descreveram, cada um, uma linha de produção sem teste; o commit
mutou seis de uma vez e o gate ficou verde.

## O que NÃO aconteceu, verificado

- **A A40 nunca recebeu.** Os arquivos lá têm mtime anterior à janela e contêm o código correto nas
  seis linhas. A ablação `mae7`, que rodou depois, usou código correto.
- **Nenhum artefato bancado é suspeito.** Todas as medições da campanha são anteriores à janela.
- **HEAD e árvore de trabalho estão corretos** nas seis linhas, e a árvore está limpa.

## O que muda por causa disto

1. **Nunca `git add -A` com agentes rodando.** Se um agente pode tocar `src/`, o commit é por
   caminho explícito, e o `git diff --stat` é lido antes.
2. **Testes de FIAÇÃO nas seis linhas** — não cobertura genérica. Um teste que exija que
   `_draw_negatives` seja chamado; que `hierarchy_loss` entre no laço; orientação de aresta
   verificada **aresta a aresta** em vez de por fração agregada; `provenance` não vazia; a saída do
   carimbo de linhagem alimentada no `assert_comparable`.
3. **Um commit é o entregável, não a árvore de trabalho.** "O porte está pronto" é uma afirmação
   sobre o que está commitado.


---

## Adendo — várias sessões, uma identidade, uma árvore

**2026-08-20.** Duas sessões tentaram estabelecer, pelo git, qual delas escreveu um commit. **Não é
possível:** todas commitam como o mesmo autor, na mesma árvore de trabalho. As duas descreveram o
mesmo diff como próprio, com detalhe correto, e a evidência é compatível com qualquer das duas.

Isso **não importa** para o registro — e é intencional que não importe. Os documentos deste
repositório registram **o que o sistema faz e por quê**, nunca quem escreveu. Daqui a seis meses a
autoria não ajuda ninguém; o mecanismo, sim.

**Mas tem uma consequência que importa, e é a deste incidente:** quando mais de uma sessão escreve na
mesma árvore, a chance de um `git add -A` capturar trabalho alheio em voo **aumenta**, e a origem do
que foi capturado fica ilegível depois. Foi assim que seis mutações de auditoria entraram num commit.

A defesa continua a mesma, e agora com um motivo a mais:

* **commit por caminho explícito** quando houver qualquer agente ou sessão ativa;
* **`git diff --stat` lido antes**, não depois;
* e a única pergunta que decide, que não é "quem escreveu" mas **"isto que estou commitando é o que
  eu pretendia commitar?"**.


---

## Varredura do histórico — feita em 2026-08-20, e o que ela fecha

A verificação original conferiu **as seis linhas** que a auditoria apontou. Não conferiu se **outros**
commits capturaram trabalho em voo. A sessão parceira varreu os dela e perguntou; varri os meus.

Método, que é a regra deste documento aplicada retroativamente: para cada commit, **a contagem de
arquivos em `src/` é compatível com o que a mensagem descreve?** Um commit que abre um estudo ou
corrige documentação e toca cinco arquivos de código é a assinatura.

**Duas anomalias, e são o par conhecido:**

| commit | arquivos | em `src/` | mensagem |
|---|---:|---:|---|
| `a85a42f4` | 9 | **5** | "abre o estudo improvements" |
| `1d9d5dad` | 8 | **5** | "triagem das três fontes fechada" |

O primeiro capturou as mutações; o segundo as desfez. **O par cancela exatamente**: `git diff
a85a42f4~1 1d9d5dad -- src/` é **vazio**, e são os mesmos cinco arquivos nos dois lados. Sem resíduo.

**Nenhuma outra.** Todos os demais têm contagem compatível — o canário toca dois arquivos de `src/`,
os gates do §3 tocam um, as cinco alegações sobre o otimismo tocam três. Nenhum commit de prosa
mexendo em código.

O que isto acrescenta ao registro: a contaminação foi **um evento, não um padrão**, e a janela foi de
nove minutos. Antes desta varredura isso era uma suposição razoável; agora é verificado.
