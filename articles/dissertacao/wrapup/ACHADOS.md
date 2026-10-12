# ACHADOS — pasta da dissertação

> **Movido da raiz para `wrapup/` em 2026-10-01.** E o inventario da organizacao pos-defesa (28/08 a 01/10), nao lei: o que decidiu esta no `VEREDITOS.md`.

> **Escopo:** `articles/dissertacao/` e **só**. O resto do repositório fica para a fase seguinte;
> o que apareceu de fora está na **Parte B**, apenas anotado, sem ação.
>
> **Data:** 2026-08-28 (dia da defesa — aprovada). **Estado:** nada foi apagado, movido ou
> commitado. Este documento é a primeira passagem: **inventário e verificação**.
>
> **Como ler a coluna de origem:** `[V]` = eu verifiquei contra os ficheiros agora.
> `[R]` = relatado pela sessão `gate` ou `ppt` e **não** reverificado. Onde eu corrigi um
> relato, está marcado **CORREÇÃO**.

---

## 0 · Decisões do autor — tomadas em 28/08

| # | assunto | decisão | estado |
|---|---|---|---|
| **D1** | `presentation/exemples/` — gravação de 6,6 GB | **apagar de vez**, reafirmada com os factos corrigidos | ✅ feito · 6,6 GB libertados · ver **A2** |
| **D2** | rastrear o deck congelado e as figuras | **sim** (implícito em *"vamos subir tudo isso no git"*) | ✅ feito · ver **A1** |
| **D3** | erratas ERR-1…ERR-7, Apêndice G, proveniência do `.bib` | **só registar, não mexer no texto** | ✅ registado · ver **A3** |
| **D4** | profundidade desta passagem | **README de entrada + commit de tudo**, sem apagar nem mover | ✅ `README.md` escrito |

**Adiado por escolha do autor:** destilar o `considerations.md` e podar o `presentation/` item a
item. A base para isso — inventário, citações e armadilhas — está neste documento.

---

# PARTE A — dentro da pasta

## A1 · 🔴 O achado mais grave: o deck congelado não existe para o git

`presentation/slides/slide_final.pdf` — o deck que a banca viu, congelado a pedido do autor e
registado em `slides/SLIDE_FINAL.md` — está **gitignorado e não rastreado**. `[V]`

```
slides/slide_final.pdf      >>> UNTRACKED + ignored <<<
figures/plates/*.pdf        >>> UNTRACKED <<<     (visíveis, mas nunca adicionados)
SPEECH.pdf                  TRACKED               (este está bem)
```

Ele desaparece de `git status`. Um `git clean -xfd` apaga-o **sem aviso e sem diff**.

**E isto já aconteceu uma vez nesta mesma pasta.** O próprio `presentation/.gitignore` documenta
o acidente, nas linhas 27-30:

> *"Em 2026-08-21 ele foi apagado por engano justamente porque a regra `*.pdf` acima o tornava
> invisível ao `git status`."*

E as linhas 33-35 do mesmo ficheiro dão a instrução para evitar a repetição:

> *"Quando o deck final existir, rastreie-o explicitamente: `git add -f presentation/<nome-do-deck>.pdf`"*

**A instrução nunca foi executada.** As chapas TikZ têm o mesmo problema por outra via: a exceção
`!figures/plates/*.pdf` existe no `.gitignore` (linha 41), portanto elas **não** estão ignoradas —
mas também nunca foram adicionadas. Estão como `??`, recuperáveis; o `slide_final.pdf` não.

✅ **Feito nesta passagem** (aditivo e reversível, alinhado com *"vamos subir tudo isso no git"*):

```bash
git add -f presentation/slides/slide_final.pdf   # o deck congelado, 1,0 MB
git add    presentation/figures/plates/          # as 4 chapas TikZ, 88 KB
```

### E o espelho do mesmo problema: as figuras existiam sem as suas fontes `[V]`

A `tikz` apontou, e confirmei: antes desta passagem o git tinha **quatro PDFs e mais nada** em
`presentation/figures/`. Os `.tex` que os geram, os scripts de build e o README **não estavam
ignorados — estavam por adicionar**.

> Quem clonasse recebia quatro imagens e **nenhuma forma de as alterar** — o oposto exato do que
> o autor quer (*"outras pessoas podem querer usar as imagens"*).

✅ Adicionados: `src/*.tex` (8), `preview.tex`, `standalone.tex`, `build.sh`, `export.sh`,
`nesped.sty`, `README.md`. **Fora, de propósito:** `build/` (ignorado) e `png/` (3 MB de renders,
regeneráveis por `build.sh`).

**Duas notas sobre o relato da `tikz`:**

- ✅ **correta** na largura: `slides/main.tex:841` diz `width=0.80\textwidth` (alvo ~302 pt),
  não os 0,85/~321 pt que o `gate` tinha dito;
- 🔴 **e aqui errei eu, e a correção é dela.** Eu disse que ela estava errada ao chamar
  `figures/superseded/_hgi_flow_v1_376pt.pdf` de duplicata do `plates/hgi_flow.pdf`, porque os md5
  divergem (`b57b48b2…` vs `97964125…`). **O md5 não responde a essa pergunta.** Refiz o teste
  pelo método que a própria pasta manda usar:

  | teste | resultado |
  |---|---|
  | `pdfinfo` — tamanho de página | `377,87 × 164,53 pt` **nos dois** |
  | `pdftotext` — texto extraído | **idêntico** |
  | render a 600 dpi (`gs -sDEVICE=ppmraw`), raster cru | md5 `6bb9868e…` **nos dois — idêntico pixel a pixel** |
  | `pdfinfo` — `CreationDate` | 26/08 20:06 vs 27/08 17:40 ← **a única diferença** |

  **São o mesmo desenho, compilado duas vezes.** E isto está escrito como lei em `CLAUDE.md:109`:
  *"To verify a rebuild, compare `pdftotext` output, **not** md5: there is no `SOURCE_DATE_EPOCH`,
  so every rebuild differs in `/CreationDate` and md5 can never match."* **Eu não a li antes de
  contradizer quem tinha razão.**

  > **A regra geral, e vale para o resto desta limpeza:** o md5 prova **cópia**, não prova
  > **conteúdo**. Para "estes dois PDFs são versões diferentes?", comparar **render ou texto
  > extraído**. Um md5 divergente aqui é o carimbo de data, não desenho novo.

  A ação não muda — **não apagar**, e isso ficou acordado com a `tikz`: está debaixo do `*.pdf` do
  `.gitignore`, logo se sumir do disco some sem aparecer em diff. Mas o ficheiro **é** redundante
  por conteúdo, e apagá-lo passa a ser decisão do autor, não um defeito a corrigir.

---

## A2 · 🔴 Um erro meu, e o que se perdeu com ele

**Eu disse ao autor que nada no repositório citava a gravação de 6,6 GB. Estava errado**, e ele
decidiu apagá-la com base nisso. Verifiquei tarde, antes de executar, e voltei a perguntar com os
factos corretos — **ele reafirmou o apagar com o quadro completo**, e só então apaguei.

**O que a gravação era** `[V]`: a defesa de **uma defesa anterior do mesmo programa** (mesmo programa, mesmo
template NESPeD), 61 min, 4K. Era a **base empírica** contra a qual o deck foi reescrito a
2026-08-24 — as medições de forma (mediana 21 palavras de ecrã, média 28, máx ~71) saem dela.
Citada em quatro documentos:

- `BOAS_PRATICAS_SLIDES.md §3` — a referência de forma medida;
- `APRESENTACAO_DEFESA_GUIDE.md §4.0` — a tabela de timing slide-a-slide, lida do relógio do Meet;
- `HANDOFF.md (anexo, sec. `HANDOFF_SLIDES.md`)` — o alvo empírico do deck;
- `HANDOFF.md` — o método de extração de frames.

**Não havia cópia** `[V]`: o tarball `~/Backups/dissertacao_exemples_2026-08-20.tgz` (43 MB) **não**
a continha, e `/Volumes/linux/VIDEO/` já não a tinha. O próprio `BOAS_PRATICAS_SLIDES.md:254`
avisava: *"se o arquivo sumir do disco, some de vez."*

✅ **Anotado nos documentos, 2026-08-28.** O `gate` escreveu a linha e autorizou os três dele;
aplicada em `HANDOFF.md`, `HANDOFF.md (anexo, sec. `HANDOFF_SLIDES.md`)` e `APRESENTACAO_DEFESA_GUIDE.md §4.0`, ancorada no
caminho do ficheiro e não em número de linha:

> ⚠ *A gravação que sustenta esta medição foi apagada em 28/08/2026, por decisão do autor
> (conteúdo pessoal de terceiro, cópia única). O método e os valores ficam; a evidência primária
> não é reverificável.*

✅ **`BOAS_PRATICAS_SLIDES.md §3` — a `ppt` escreveu a dela, e é melhor que a linha que recebeu.**
Foi o certo ter-lhe perguntado em vez de aplicar: ela é dona do ficheiro e sabia duas coisas que a
nota genérica escondia.

**1 · Havia uma frase que passou a ser falsa.** O `§3` abria com *"É uma GRAVAÇÃO, e ela agora está
dentro do repositório"*, com o caminho. Uma nota ao lado deixaria o documento a **afirmar a
presença do ficheiro e a negá-la três linhas abaixo**. Ela reescreveu a abertura.

**2 · E "o método e os valores ficam" era generoso demais.** É aqui que está o custo real do
apagamento, e é mais fundo do que eu tinha escrito:

> O `§3.1` valia por **três leituras de ritmo que convergiam em ~40–48 s/slide e não partilhavam
> instrumento**. Duas delas — os 45/37 s por bloco e os ~11 min do slide final — vinham de quadros
> amostrados da gravação, e **morreram com ela**. O `§3.2` inteiro (títulos, ausência de bloco
> colorido) era observação direta, e **morreu também**. Sobrevive uma: os 48 s/slide, que vêm do
> `APRESENTACAO_DEFESA_GUIDE.md §4.0` — documento, não vídeo.
>
> **O alvo de ~48 s/slide continua defensável. Mas deixou de ser triangulação, e o `§3` dizia que
> era.** Quem citar o `§3.1` precisa de saber isso; está lá em tabela agora.

**3 · E ela preservou o aviso que ela própria tinha escrito semanas antes** — *"se o arquivo sumir
do disco, some de vez"* — agora entre aspas, com **`Sumiu.`** a seguir.

> 🔴 **Isso é o achado do dia, e é a mesma classe do `slide_final.pdf` da §A1: um aviso registado
> não é uma salvaguarda.** Nos dois casos o risco estava escrito, no sítio certo, com a instrução
> para o evitar ao lado — e nos dois casos ninguém a executou. Aconteceu **duas vezes no mesmo dia,
> no mesmo repositório**. O `slide_final.pdf` sobreviveu por acaso: bastou olhar. O vídeo não.
>
> Argumento a favor da decisão, para o registo: era a defesa **de outra pessoa** e continha
> **conteúdo pessoal do autor** (61 min do ecrã dele, com outras janelas). Sob o critério novo
> — *"colegas do departamento vão poder ler e usar isto"* — não é um ficheiro que se queira
> preservar e partilhar.

### O resto do disco `[V]`

Depois do apagar, `presentation/` passou de **6,6 G para 17 M**; o espaço livre da máquina foi de
13 GiB para 19 GiB. O que resta ignorado no disco, dentro do escopo, é pequeno e regenerável:

| tamanho | caminho | o que é |
|---|---|---|
| 49 M | `exemples/` | dissertações de exemplo · **tem** backup (`~/Backups/…2026-08-20.tgz`) |
| 16 M | `src/build/` | saída de build |
| ~4 M | builds de `presentation/` e `wrapup/material_extra/` | saída de build |
| 3 M | `presentation/figures/png/` | renders das chapas, regeneráveis por `build.sh` |
| ~1 M | `.DS_Store` (19×), `__pycache__` (2×) | cruft |

## A3 · Pendências reais do depósito

### ERR-1 … ERR-7 — sete erratas, todas abertas `[V]`

> ✅ **Fechadas todas a 2026-09-06** (actualizado 2026-10-02): ERR-1 não era defeito, ERR-2
> ratificada sem mudança, ERR-3/6/7 aplicadas, ERR-4 decidida, ERR-5 fechada em falha-segura no
> `holm1979`. O estado de cada uma está no bloco "ESTADO A 2026-09-04" do §3 de
> `wrapup/open_points/LACUNAS.md` e na linha ERRATA da tabela do §4 do `CLAUDE.md`. O resto desta subsecção é o
> registo de 28/08, quando estavam abertas.

Em `wrapup/open_points/LACUNAS.md`, todas marcadas `[ABERTO]`, com rascunhos `.tex` em
`wrapup/erratas/`. A `AUT-35` decidiu adiá-las para depois da defesa — **é agora**.

| | linha | assunto |
|---|---|---|
| ERR-1 | 336 | normalização de "multi-task" entra na coluna de prosa **publicada** |
| ERR-2 | 356 | títulos dos cap. 3 e 5 desidratam o hífen de títulos citados |
| ERR-3 | 373 | nota de anotação interna imprime **dentro** de uma referência |
| ERR-4 | 386 | 2 entradas do `.bib` não citadas (`belkin2003laplacian`, `santos2024urban`) |
| ERR-5 | 402 | 6 entradas sem identificador; 3 resolvíveis já |
| ERR-6 | 427 | atribuição errada da origem da taxa de aprendizado de FL e CA |
| ERR-7 | 450 | a mesma frase grada Florida como "fewer folds" |

`LACUNAS.md:51` regista que **ERR-6 e ERR-7 não vinham de registo nenhum** — foram encontrados na
auditoria. Vale ler antes de fechar os outros cinco.

### Apêndice G do suplemento imprime colunas de parâmetros erradas `[V]`

> ✅ **Corrigido** (recontagem de 2026-09-02; verificado a 2026-10-02 no fonte sem comentários): a
> tabela do `apx_i_parameter_count_control.tex` imprime hoje 1,433,863 / 9,634,471 / 12,044,791, e
> 644,359 já só aparece nos comentários de proveniência. O resto é o registo de quando estava errado.

`wrapup/material_extra/chapters/apx_i_parameter_count_control.tex:101-102` ainda imprime:

```
Alabama    & 4,197,621 & 644,359 & 4,207,399 (h=672)   -> rotulado "100,2%"
California & 5,151,189 & 644,359 & 5,249,719 (h=752)   -> rotulado "101,9%"
```

O defeito **já está registado** em `CLAUDE.md §5 item 6`, que mede outra coisa
(1.433.863 / 9.634.471 = 230 % / 12.044.791 = 234 %) e conclui: *"Do not say 100.2% aloud."*
Os resultados de macro-F1 estão bem e a conclusão **fortalece**. O que falta é o `.tex` refletir
isso. **Pendência viva do suplemento, não do volume principal.**

### Dívida aberta na chapa `hgi_flow` — decisão do autor, não defeito `[R, tikz]`

A chapa entra no deck reduzida (`slides/main.tex:841`, `width=0.80\textwidth`), o que afina os
traços ~20 %. Regenerá-la no tamanho final (**~302 pt** — o número certo; o `gate` tinha dito
0,85/~321 pt e está errado) **exige uma rodada de composição, não uma transformação mecânica**:
a `tikz` já tentou a via mecânica e falhou — os pictogramas não encolhem na proporção das caixas
e dois rótulos posicionados à mão encostam nos grafos. O porquê está no
`presentation/figures/README.md`.

Há também um limite estrutural que vale saber antes de alguém tentar: **traço em peso cheio *é*
altura extra**, logo uma chapa regenerada nunca reproduz a proporção da reduzida. Não existe
"traço cheio e a mesma altura" — só se escolhe de que lado fica o erro.

> **Nada a fazer sem o autor pedir.** Se ele quiser, a `tikz` regenera e manda o render **antes**
> de tocar em `plates/`. Se não quiser, o README já regista a dívida com o alvo medido e o
> resultado negativo, que é o bastante para alguém retomar daqui a um ano. **Pendência de decisão,
> não defeito por corrigir.**

### `banca.pdf` não reproduz do `src/` — e isso é de propósito `[V]`

```
src/banca.pdf        md5 5be69d1bf589e6fe5e794898a06306cf   <- congelado, o que a banca recebeu
src/dissertacao.pdf  md5 d7e85bb7a00911aa5a8a37eb4f51f76a   <- o que vai ao depósito
```

São ficheiros diferentes **por desenho** (`CLAUDE.md §1.2`). Quem auditar sem saber disto vai
reportar um defeito que não existe. **Nunca rebuildar o `banca.pdf`.**

---

## A4 · Documentos que induzem em erro

### NORTH_STAR.md — **CORREÇÃO ao relato do `gate`** `[V]`

O `gate` disse que a escada superada está nas linhas **26, 43, 175, 330, 394** e que "ninguém deve
copiar uma alegação de lá". **Duas correções:**

1. **O ficheiro não mente em silêncio.** Tem um banner nas linhas 15-27 com o veredito entregue
   (categoria: **só Florida**, +0,19, Holm p 0,011; região: **não-inferior nos seis**, TX +1,21,
   CA +1,06) e diz explicitamente que a faixa real é **+0,23…+2,81**, não "+28…+40" (dizia +6,29
   até 2026-10-02; a célula de Istambul não era pareada).
2. **As linhas que ele deu não são onde o texto está hoje.** Os sítios vivos são **21, 22**
   (o próprio banner), **49** (marcada `[SUPERADO 2026-08-20]`) e **67**.

🔴 **A linha 67 é o problema real, e ninguém a tinha apontado.** É a linha da tabela dos três
papers — o sítio mais copiável do ficheiro — e carrega `+28…+40 macro-F1` **e** *"category
outperforms the dedicated model at all six datasets (+5.3…+9.4)"* **sem marcador `[SUPERADO]`
nenhum**. As outras estão todas marcadas; esta escapou.

✅ **RESOLVIDO 2026-08-28, com a decisão do `gate` (dono do ficheiro): marcar, não reescrever** —
que é a política declarada pelo próprio banner (*"ficam como estão, marcadas… porque reescrever o
corpo apagaria o registro de qual era a tese quando o arco foi desenhado"*).

E o `gate` derrubou o meu "pode ser legítimo como descrição do paper submetido": o `+28…+40` é
número de substrato **pré-v18, com vazamento** — não é uma tese anterior que foi revista, é uma
geração que foi **invalidada**. Não há leitura em que seja citável.

**Feito, com o corpo intocado:**
1. a linha 67 recebeu dois marcadores `[SUPERADO 2026-08-20]`, um por alegação (a faixa e o "all
   six datasets"), cada um com o valor entregue ao lado;
2. 🔴 **o banner deixou de apontar por número de linha.** Este era o defeito maior: ele nomeava as
   linhas 26/175/330/394 — e o texto **já não estava em nenhuma delas**. Um guarda que aponta para
   portas limpas manda o leitor conferir quatro sítios certos e falha o único errado; foi assim que
   o briefing me chegou com as linhas trocadas. Agora aponta por **conteúdo** (*"onde aparecer
   `+28…+40`, `category everywhere` ou `region at four of six`…"*).

   > ⚠️ **CORRIGIDO 2026-09-08 — a minha explicação da causa estava errada, e a verdadeira é pior.**
   > Eu escrevi que o ponteiro *apodreceu* quando o ficheiro se mexeu, o que pressupõe que já esteve
   > certo. A `mobiwac` foi ao commit em que o aviso nasceu (`dce51d9b`, 2026-08-20) e mediu; eu
   > confirmei por caminho independente:
   >
   > | ficheiro nesse commit | linhas | das 5 apontadas, quantas continham a escada |
   > |---|---|---|
   > | `docs/NORTH_STAR.md` | 525 | **0** |
   > | `articles/dissertacao/NORTH_STAR.md` | 415 | **2** |
   >
   > Duas leituras. Primeira: **o aviso sempre apontou para este ficheiro** — é o único onde alguma
   > linha bate; a hipótese de estar a apontar para o outro `NORTH_STAR.md` (são dois, e são
   > documentos diferentes) **não se confirma**. Segunda, e é a que importa: **o ponteiro nasceu a
   > 40% e decaiu daí.** Não passou de correto a podre — já estava 60% errado no dia em que foi
   > escrito.
   >
   > **A lição fica mais forte, não mais fraca.** Não é só que ponteiros de linha apodrecem: é que
   > **ninguém os verifica no instante em que os escreve**, porque não há nada que os teste. Um
   > ponteiro por conteúdo não precisa dessa verificação — é essa a razão de o ser, e não a
   > resistência a mudanças futuras que eu tinha dado.

Conferido depois: as três ocorrências restantes estão ou dentro do banner, ou marcadas. Nenhuma
sem marcador.

> ⚠ Fica uma coisa **não** corrigida, de propósito: a coluna de Status da linha 67 diz *"Submitted,
> under review"*, e o `gate` informa que o MobiWac **aceitou** o paper depois do depósito. É registo
> desatualizado, não alegação superada — e mexer nisso é decisão de conteúdo do autor.

### `references.bib` — 20 comentários de proveniência apontam para um caminho que não existe `[V]`

```
citado:   articles/dissertacao/fundamentals/_bib/new_references_ch2.bib   <- NÃO EXISTE
real:     articles/dissertacao/science/fundamentals/_bib/new_references_ch2.bib
```

20 ocorrências exatas. A pasta `fundamentals/` na raiz da dissertação não existe — o ficheiro
vive sob `science/`. A trilha de proveniência do `.bib` está **partida desde a reorganização**.
Correção mecânica e segura (é tudo comentário `%`; não toca em campo nenhum do BibTeX), mas é
edição no source entregue — **fica para depois de D3**.

### `AGENT_GUARDRAILS.md §N1` aponta para fora `[R, não verificado]`

> ✅ **Verificado a 2026-10-02: já não aponta.** O §N1 foi repontado a 2026-08-20 (commit `401c45ab`)
> para as tabelas do Cap. 5, e hoje cita o `RESULTS_BOARD.md` só para dizer que não se lá vai.

O ponteiro é da pasta; o alvo (`docs/studies/closing_data/RESULTS_BOARD.md`) é da raiz do repo e
está **fora do escopo**. Ver **B1**.

---

## A5 · O que parece lixo e **não é** — armadilhas confirmadas

**`src_utils/_round6` … `_round14` — NÃO APAGAR.** `[V]` Confirmado por dois caminhos:
- `src_utils/check.sh:345-346` **executa** `python3 $UTILS/_history/_round9/35_wave_a_render_check.py`;
- `check_audit_claims.py` **lê os `.md` como dados** — tem uma tabela de regexes que casa contra
  `_history/_round9/37_reviewer_gate_round9.md`, `_history/_round9/47_applied_check.md` e outros. Apagar um `.md`
  do `_round9` faz o gate de auditoria falhar, não avisar.

**`science/` — CORREÇÃO ao relato do `gate`.** `[V]` Ele disse "o source entregue cita `science/`
19 vezes". A contagem está certa (19), mas o que importa é isto: **as 19 estão todas dentro de
comentários LaTeX (`%`)**. Não há uma única referência em código ativo.

> **Consequência prática:** apagar `science/` **não parte o build**. O argumento para manter é
> "preserva a proveniência", não "senão quebra". É um argumento mais fraco — e portanto uma
> decisão diferente da que o briefing sugeria. `science/` são 15 MB.
>
> Nota separada: as **ferramentas** (`check_wordcount_claims.py`, `sync_deliverables.py`,
> `verify_format.py`, `mkformat.py`, …) referem `science/AGENT_HANDOFF.md`, e o
> `sync_deliverables.py:40` **mapeia-o**. Esse ficheiro é vivo. `science/` inteiro não é o mesmo
> que `science/AGENT_HANDOFF.md`.

**`src/figures/` — o deck da defesa depende dela.** `[V]` `presentation/slides/main.tex:14`:

```latex
\graphicspath{{img/}{../figures/plates/}{../../src/figures/}{../../src/figures/mobiwac/}{../../src/figures/courb/}}
```

Quatro das figuras do deck vivem na árvore entregue. `\includegraphics` que não resolve produz
**caixa vazia, não erro** — parte em silêncio. `[R]` do `ppt`, caminho verificado por mim.

**`src/banca.pdf`** — ver A3. **`exemples/`** — ver A2.

---

## A6 · Armadilhas de mecânica — uma delas está mal documentada

### 🔴 `git check-ignore` **mente em caminhos já rastreados** — CORREÇÃO importante `[V]`

A regra escrita em `CLAUDE.md §5 item 7` e repetida pelo `gate` é *"antes de apagar, corre
`git check-ignore -v <path>`"*. **Essa forma do comando dá a resposta errada:**

```
docs/results  (default):     NOT IGNORED
docs/results (--no-index):   .git/info/exclude:9:results   docs/results
```

`git check-ignore` consulta o índice: se o caminho **já está rastreado**, reporta "não ignorado"
mesmo estando coberto por uma regra. Foi exatamente isto que me deu leituras contraditórias
(`docs/results` "não ignorado" com 4 169 ficheiros rastreados, mas `.../rundirs/results`
"ignorado" — a diferença é o índice, não a regra).

**A sonda correta é uma destas duas:**
```bash
git check-ignore --no-index -v <path>     # a regra, sem o índice
git status --ignored --porcelain <dir>    # o que existe no disco e o git não vê
```

✅ **E a boa notícia:** **não há nenhuma pasta chamada `results` dentro de `articles/dissertacao/`**
`[V]`. **A armadilha do `docs/results/` não dispara no nosso escopo.** O que dispara é a lista da
**A2** — e é essa que interessa antes de qualquer limpeza aqui.

### 🔴 O md5 prova cópia, não prova conteúdo — e nestes PDFs mente `[V]`

Os PDFs desta pasta **não fixam `SOURCE_DATE_EPOCH`**, então cada recompilação muda o
`/CreationDate` e o md5 — **mesmo sem alterar um byte de desenho**. Dois ficheiros com hashes
diferentes podem ser a mesma figura compilada duas vezes, como se provou em **A1**.

**Está escrito como lei em `CLAUDE.md:109`**, e eu contradisse quem tinha razão por não a ter lido.

| a pergunta | o teste certo |
|---|---|
| "são o mesmo ficheiro?" (cópia) | **md5 serve** — foi o que usei para conferir os blobs commitados contra o disco, e essa verificação é válida |
| "são a mesma figura?" (conteúdo) | **`pdftotext`, ou render** e comparar o raster |

```bash
# a forma preferida: o hash do raster cru e' um numero comparavel e arquivavel
# (ppmraw nao carrega metadados, ao contrario do PNG)
gs -q -dNOPAUSE -dBATCH -sDEVICE=ppmraw -r600 -sOutputFile=out.ppm ficheiro.pdf && md5 -q out.ppm
```

---

### Cinco alvos do make sobrescrevem `dissertacao.pdf` `[V]` — `gate` correto

`src/Makefile`: `defense` (36), `all` → `defense` (33), `all3` → `defense` (52),
`fast`/`fast-defense` (59-60), `fast3` (66-69, `cp build/main.pdf dissertacao.pdf`).

**Um `make` pelado sobrescreve o PDF do depósito.** Seguro para conferir: `make check` (não
builda), `make academico`, `make ppgc` (não copiam).

### `make check` sai com código ≠ 0 mesmo imprimindo verde `[R]`

Relatado pelo `gate`; **não executei** (evito correr o harness sem necessidade). **Ler o exit
code, não a saída.** Registado como aviso, não como facto verificado.

### `Makefile.speech` diz `OK` sobre um intermediário velho `[V]` — `ppt` correto

```make
SPEECH.pdf: SPEECH.tex
	xelatex ... && echo "OK -- SPEECH.pdf (N paginas)"
```

O cabeçalho diz *"o roteiro de fala, **gerado do SLIDES.md**"*, mas a regra **só compila o
`SPEECH.tex` que já está no disco** — nunca chama `build_speech_1_extract.py` nem
`build_speech_2_emit.py`. Imprime `OK` na mesma. **Ou se corrige a dependência, ou se documenta.**

### Comentários LaTeX inflam qualquer grep `[V]` — `gate` correto

Cada tabela reescrita carrega um cabeçalho `EVIDENCE BASE REPLACED` que **cita os valores
superados verbatim**. Filtrar o **ficheiro**, não a saída:
`grep -v '^[[:space:]]*%' ficheiro.tex | grep <padrão>`. Foi assim que separei os 19 `science/`
(todos comentário) dos 0 ativos.

---

## A7 · Fio solto que o `gate` deu como aberto e **já está fechado** — CORREÇÃO `[V]`

O briefing lista como pendência: *"o `6.909.789` … não reconcilia com os `5.151.189`"*.

**Duas coisas:**

1. **Os dois números são de estados diferentes** — `6.909.789` é **Alabama**, `5.151.189` é
   **California**. Não deviam reconciliar. O par correto é **CA 8.809.533 (reconstruído) vs
   CA 5.151.189 (medido)**.
2. **O ficheiro já resolve isto**, e ontem. `wrapup/open_points/AUDITORIA_PRE_LEAK.md:149-157`
   tem um bloco `🔴 CORRIGIDO 2026-08-27`, com o `6.909.789` **riscado**:

   > *"O 6.909.789 **não foi medido** — é uma reconstrução com defaults assumidos, e os logs de
   > execução v18_2 a contradizem… **O 4.197.621 é o que o modelo entregue de facto executa.**"*

**Não é pendência.** O que sobra é consequência conhecida: a largura pareada `h=672` pareia o
orçamento da arquitetura **anterior** — que é precisamente o defeito do Apêndice G (A3).

**Duplicação real, essa sim:** `wrapup/post_submission_studies/EXECUTION_WAVE.md` e
`docs/studies/closing_data/v18/EXECUTION_WAVE.md` são **byte-idênticos**
(md5 `55070d377d380f33ecf27c7630ea92fb`). Um está dentro do escopo, o outro fora. Ver **B2**.

---

## A8 · `presentation/` — o que é registo e o que é andaime

A pasta do `gate` terminou o trabalho. **Nada aqui foi tocado**; é proposta para D4.

**Registo — fica** (`[R]` do `gate`/`ppt`, com o meu voto):
- `considerations.md` (394 KB) — decisões **AUT-1…AUT-36** com a razão de cada uma. **Destilar,
  não apagar.** O `gate` sabe quais foram revogadas;
- `HANDOFF.md (anexo, sec. `HANDOFF_GATE.md`)` — 12 classes de erro + 6 regras de medição que **não são sobre slides**;
  generalizam. **Candidato a subir para a raiz da pasta;**
- `HANDOFF.md (anexo, sec. `HANDOFF_PPT.md`)`, `BOAS_PRATICAS_SLIDES.md` — a forma medida do template;
- `slides/slide_final.pdf` + `slides/SLIDE_FINAL.md` — ver **A1**;
- `figures/plates/` — **zero ficheiros sem uso** `[R, ppt]`. Nada a podar.

**Instrumentos vivos — ficam** `[R, ppt]`:
- `canaria_coluna.py` — apanha duas classes que o `Overfull` dá como zero: coluna de `columns`
  que transborda (~11 frames de duas colunas) e botões do índice que não renderizam;
- `build_speech_1_extract.py` + `build_speech_2_emit.py` — a cadeia que gera o `SPEECH.pdf`;
- 🛑 **`SLIDES.md` (320 KB) não é andaime** — é a **fonte** do `SPEECH.pdf`. Apagá-lo não parte
  o deck: parte o roteiro, **em silêncio**, porque o `SPEECH.tex` continua no disco a compilar.

**Provável andaime — confirmar item a item com o `gate`:**
`SPEC_EXTRAS.md (anexo, sec. `CORTES_FALA.md`)`, `SPEC_EXTRAS.md (anexo, sec. `SPEC_RODADA_27AGO.md`)`, `SPEC_EXTRAS.md (anexo, sec. `FAIXA_VS_CORPO.md`)`, `hgi_draw.txt`, `SPEC_EXTRAS.md (anexo, sec. `andrej_mtl.md`)`,
`ink_sweep.py`, `diff_fala.py`, `archive/`, `slides_ux/`, `HANDOFF.md`, `HANDOFF.md (anexo, sec. `HANDOFF_SLIDES.md`)`,
`PLANO_FLUXO_DEFESA.md`, `APRESENTACAO_DEFESA_GUIDE.md`.

> O `gate` avisou que **alguns têm consumidores que não se veem**. Confirmado no caso do
> `SLIDES.md`. **Nenhum destes sai sem passar por ele primeiro.**

---

## A8b · ⚠ Risco de coordenação: três documentos a nascer sobre a mesma coisa

Levantado pelo `gate`, que é o único a ver os três ao mesmo tempo. Estão a nascer **três registos
sobre como os agentes se enganam a medir**:

| | onde | o quê |
|---|---|---|
| 1 | `presentation/_preparacao/HANDOFF.md (anexo, sec. `HANDOFF_GATE.md`)` | 12 classes de erro + 6 regras de medição |
| 2 | (em curso, pedido à `ppt`) | as regras de medição dela — custo em linhas e não em caracteres, altura de `columns` ser o máximo, instrumento que reporta sucesso parcial |
| 3 | `wrapup/ACHADOS.md §A6` + a tabela do rodapé | as armadilhas que apanharam esta passagem |

**Os três dizem a mesma coisa por três caminhos — e isso é exatamente *"documento sobre
documento"*, o hábito que o autor nomeou.** Se ficarem os três, o próximo agente lê um e ignora
dois.

**Proposta (do `gate`, e concordo):** **um** ficheiro na raiz da pasta com as classes de erro e as
regras de medição — elas **não são sobre a defesa**, são sobre medir e concluir, e sobrevivem a
tudo o que se apague. Os outros dois apontam para ele ou desaparecem dentro dele.

> ⚠ **Separação que importa e que não se deve perder na fusão:** o `wrapup/ACHADOS.md` é sobre o **estado
> desta pasta**, que é outra coisa e tem outra validade no tempo. As classes de erro duram; um
> inventário não.
>
> **Não feito nesta passagem** — o autor pediu README + commit, e fundir três documentos é
> trabalho de item a item que ele não autorizou. **Fica como pendência com a razão escrita**, que
> é o ponto: daqui a uma semana ninguém percebe que os três eram um.

---

## A9 · Estado do git no escopo `[V]`

`19 modificados` + `16 não rastreados`, nenhum commitado. Inclui trabalho de conteúdo real
(`GLOSSARY.md`, `WRITING_LAW.md`, `AGENT_GUARDRAILS.md`, `SPEECH.*`, `slides/main.tex`,
`ESTUDOS_DEFESA.html`).

**Antes de qualquer limpeza, este trabalho devia estar commitado** — senão a limpeza e o trabalho
do dia misturam-se no mesmo diff e deixam de ser reversíveis em separado. **Push só no fim, com
o autor.**

---

# PARTE B — fora do escopo (só anotado, para a fase seguinte)

> **Nada aqui foi tocado, e nada aqui deve ser tocado nesta fase.**

**B1 · `docs/studies/closing_data/RESULTS_BOARD.md` está morto para a dissertação** `[R, gate]`
É v17, com categoria inflada por vazamento em 25-45 pontos (imprime AL 63,56 contra os 30,59
entregues) — e **chama-se a si próprio "single source of truth"**. `AGENT_GUARDRAILS.md §N1`
(dentro do escopo) aponta para ele. **O ponteiro é nosso, o alvo não.** `[V]` o ficheiro existe
e está rastreado; o conteúdo não foi auditado por mim.

**B2 · `EXECUTION_WAVE.md` duplicado** `[V]` Byte-idêntico em
`articles/dissertacao/wrapup/post_submission_studies/` (dentro) e `docs/studies/closing_data/v18/`
(fora). Decidir qual é o canónico quando a fase seguinte abrir — **não desduplicar agora**, porque
metade da decisão está fora do escopo.

**B3 · A armadilha do `results` nu é real fora do escopo** `[V]` `.git/info/exclude:9` tem um
padrão `results` sem barra. Não dispara em `articles/dissertacao/`, **dispara em `docs/`**: por
exemplo `docs/results/closing_data/v18_2/modal_runs/*/rundirs/results` está ignorado e invisível.
Levar a **A6** (a forma correta da sonda, `--no-index`) para a fase seguinte.

**B4 · `ARMADILHAS_DE_MEDICAO.md` na raiz do repositório** `[R, ppt]` Doze classes de erro em que
um instrumento devolve verde e mede outra coisa. **§7** (âncora ambígua devolve a primeira
ocorrência), **§9** (uma cópia é outro artefacto no instante em que a original muda) e **§12**
(uma alegação vive em várias superfícies) aplicam-se diretamente a uma limpeza. Não verificado
por mim; fica como leitura obrigatória da fase seguinte.

---

## A10 · Auditoria pós-limpeza — o que a esteira diz agora `[V]`

Um crítico de completude correu os verificadores depois das duas vagas. **Três classes de achado**,
e a primeira é minha.

### 🔴 O que a limpeza partiu, e é reversível por reconstrução

| apaguei | quem o lia por caminho | como voltar |
|---|---|---|
| `presentation/slides/main.pdf` | `build_speech_1_extract.py:19`, `canaria_coluna.py:30`, `ink_sweep.py` | `make -C presentation/slides` |
| `src/build/` | `sync_page_counts.py`, `check_extra_xrefs.py`, e o portão de render do `check.sh:344` | `cd src && make academico` |

**A cadeia que regenera o `SPEECH.pdf` e a canária de coluna estão não-executáveis até o deck ser
reconstruído.** Nenhum dado se perdeu — mas um portão que não pode correr é indistinguível de um
portão que passa, que é exatamente o comentário escrito por cima do `check.sh:344`.

### 🔴 A pasta `exemples/` era citada 61 vezes, e duas eram de carga

`NORTH_STAR.md §3` e `WRITING_LAW.md §5` **derivam as suas regras de estrutura** de
`exemples/viegas/VIEGAS_ANALYSIS.md`. Duas das quatro leis apoiavam-se num ficheiro que passou a
existir só no tarball. ✅ **Corrigido**: as duas linhas dizem agora onde está o backup.

### ⚠ Ponteiros mortos que **não** são meus — vêm de uma reorganização anterior

Estes já estavam partidos antes de hoje, e **desligam verificações em silêncio**:

- **9 sondas do `check_audit_claims.py`** procuram `../fundamentals/DEFINITIONS.md`; o ficheiro
  mudou para `science/fundamentals/` e nunca foi repontado. Dão `SKIP`, e os `SKIP` não entram em
  nenhum balde da manchete do próprio portão (`211+16+6+1 = 234` de 235);
- **`check_trapped_prose.py:96`** procura `src/main_extra.tex`, que mudou para
  `wrapup/material_extra/`. A função devolve conjunto vazio e o roteamento de dois volumes está
  morto, com o portão a verde;
- **`check_tracker_refs.py` FALHA agora**: `LACUNAS.md:314` e `:592` citam `PENDENCIAS §4.1` e
  `§4.2`, secções que já não existem;
- **`PLAN.md`** mudou para `archive/` e ficou citado da raiz em `NORTH_STAR.md:4`,
  `UFV_COMPLIANCE.md:99` e `:133`;
- **27 ponteiros de proveniência dentro do `src/` entregue** apontam para `fundamentals/` e
  `storyline/` sem o prefixo `science/`. Quatro dos cinco alvos curam-se com o prefixo; um
  (`AVAL_NECESSARIA_3_ptBR.md`, citado em `preamble.tex:216`) derivou dois níveis e não resolve
  assim. É a versão medida do que eu tinha registado na **§A4** como "20 comentários".

✅ **TODOS REPONTADOS 2026-08-28**, e o efeito está medido:

| ponteiro | antes | depois |
|---|---|---|
| 8 sondas → `../fundamentals/DEFINITIONS.md` | 9 `SKIP`; portão `exit=2` | **0 `SKIP`**; `exit=1` |
| 1 sonda → `chapters/apx_g_hgi_tuning.tex` | idem (mudou de volume) | resolve em `wrapup/material_extra/` |
| `check_audit_claims` manchete | **211** de 236 | **220** de 236 |
| `check_trapped_prose` volume extra | **0** ficheiros (silenciosamente) | **5** ficheiros, `0 skipped` |
| `check_tracker_refs` | **FAIL**, 3 citações | **OK**, `exit=0` |
| `check_comment_hygiene` âmbito | 13 examinados, 1 saltado calado | **14 examinados, 0 saltados** |
| 27 comentários de proveniência no `src/` | apontavam para `fundamentals/`, `storyline/` | prefixo `science/`, os 5 alvos resolvem |

> 🔴 **O achado que isto revelou, e é o melhor do lote:** o `exit=2` do `check_audit_claims` era a
> falha dura *"uma sonda cujo ficheiro sumiu NÃO é um passe"* — e ela **mascarava o bloco que nomeia
> as 16 falhas de conteúdo reais**. As 16 estavam contadas no cabeçalho antes e depois (não criei
> nenhuma), mas só agora o portão as **nomeia** e diz o que fazer. Um ponteiro morto não estava só a
> desligar uma sonda: estava a impedir o portão de reportar as outras.
>
> **E o `check_tracker_refs` não tinha citações erradas — tinha um parser cego.** O regex exigia o
> dígito logo após os `#`, e as secções escritas `## §4.1 · …` eram invisíveis. O portão acusava
> quem as citava **corretamente**. Corrigido o regex, não as citações.

**Só mudaram comentários no `src/`** — verificado linha a linha contra uma cópia anterior: nenhuma
das 27 alterações está fora de um `%`. O texto entregue não foi tocado.

**Fica em aberto, e não é meu:** as 16 alegações marcadas como APPLIED que não estão no documento
(`R8-head`, `A22-11`, `R13-aut37`, …). São conteúdo, e o portão diz o que fazer: *"Fix the source,
then re-run this."*

### ⚠ Ainda invisível ao git, e é a mesma classe da §A1

`presentation/nesped_slides_template/main.pdf` (536 KB) é a **linha de base de calibração** do
`ink_sweep.py` — e está **untracked e ignorado** pelo `*.pdf`. A exceção do `.gitignore` protege um
ficheiro com outro nome. Sobreviveu a esta limpeza por sorte; o próximo glob de `main.pdf` apanha-o.

### Correções que a auditoria me fez, já aplicadas

- **`README.md:49` repetia o defeito que eu tinha acabado de diagnosticar** — dizia "a linha 67 do
  NORTH_STAR ainda não está marcada" quando eu próprio a marcara 13 minutos antes, e o texto já
  tinha mudado de linha. **Ponteiro por número de linha, escrito por mim, no documento onde eu
  explico que ponteiros por número de linha apodrecem.** Trocado por ponteiro de conteúdo;
- **`CLAUDE.md:227` ainda ensinava `git check-ignore -v`** sem `--no-index` — a forma refutada na
  **§A6**. O ficheiro que todo o agente carrega primeiro carregava a instrução errada. Corrigido;
- **`CLAUDE.md:36-40` afirma que o `AGENT_GUARDRAILS §N1` encaminha para o `RESULTS_BOARD`** — o
  crítico leu a linha 73 e a única menção lá é um aviso *"Do not go there"*, numa regra já
  repontada a 20/08. **A minha §A4 e §B1 repetem essa alegação como `[R, não verificado]`; ela é
  falsa.** Não a apaguei do registo — fica aqui a correção, que é como este documento funciona.

---

## A11 · O que ficou por varrer, e as regras que saíram deste trabalho

### O buraco, dito antes que alguém assuma cobertura

O passe de validade (as tarjas de geração superada) varreu **só `src_utils/_*/`**. A peneira,
aplicada às outras árvores, devolve candidatos que **nunca foram olhados**:

| árvore | ficheiros que a peneira sinalizaria | estado |
|---|---|---|
| `science/` | 6 | **não varrido** |
| `wrapup/` | 6 | **não varrido** |
| `presentation/` | 7 | **não varrido** |

Com a taxa de falsos positivos medida (2,6×), isso são talvez sete verdadeiros. Não é urgente —
mas **ninguém deve ler "passe de validade concluído" como "a pasta está varrida"**.

### As quatro regras, que valem mais do que os lotes

**1 · O critério não é a idade, é o que o ficheiro FAZ com um número.** Um documento que *regista
uma decisão* envelhece bem. Um que *afirma uma célula medida* de uma geração superada envelhece
para veneno — não é neutro, é pior do que ausente, porque se lê como corrente.

**2 · A peneira é triagem, nunca veredito — e há um número.** Sobre-reportou **2,6×**: dos 16 do
segundo lote, seis verdadeiros e dez falsos. Os dez mediam *big points* tipográficos, passivas por
cem frases, a percentagem de um estudo externo, percentagem de comentários, cobertura de validação.
O caso que ensina é o `18_visual_ufv_latex.md`: **nove** correspondências, a maior densidade do
lote, e todas em `bp`. **Densidade alta não é sinal de verdade.**

**3 · Prefere o símbolo à frase, ao ancorar.** As âncoras da `mobiwac` resolveram todas — mas por
serem nomes de símbolo (`MIN_SEQUENCE_LENGTH`, `generate_sequences`), não por disciplina. Metade
das minhas são frases de prosa, e essas **movem-se com cada errata**. `\subsubsection{POI Encoder}`
e `\cite{menon2021logitadjustment}` são as âncoras mais seguras que escrevi, e não por acaso.

**4 · Verificar uma âncora é verificá-la em CADA ficheiro que ela reclama.** Usei uma frase para
dois alvos e confirmei-a num só; o segundo não a continha. É a mesma forma do defeito dos dois
`NORTH_STAR.md` — o certo no sítio errado.

### 🔴 E o padrão que atravessa tudo o resto

**Cinco vezes em quatro dias, uma medição corrigiu uma explicação plausível. Em nenhuma o problema
era o ficheiro — era o instrumento a responder à pergunta ao lado:**

| perguntei | o instrumento respondeu | onde |
|---|---|---|
| "estes dois PDFs são versões diferentes?" | "são ficheiros diferentes" (`/CreationDate`) | **A1** |
| "esta regra apanha este caminho?" | "este caminho está rastreado" (`check-ignore` sem `--no-index`) | **A6** |
| "de que geração é este conteúdo?" | "quando o ficheiro foi tocado" (data de commit ≠ data declarada) | **A10** |
| "este ficheiro afirma células mortas?" | "tem um número entre 60 e 79" | **A11 §2** |
| "quantos ponteiros estão partidos?" | "quantos apontam para ficheiros ausentes" (0,3%) | abaixo |

O último é o mais caro. A varredura **estrutural** dava 0,3% de ponteiros partidos. Medidos contra
o **conteúdo**, ~30% em 17 ponteiros apontavam para a frase errada. **A rotura não é rara, é
maioritária — só não é detetável**, porque um ponteiro que aponta para a linha errada de um
ficheiro que existe não falha em lado nenhum. A formulação é da `mobiwac` e é a melhor que saiu
deste trabalho.

> **A regra prática:** antes de citar uma medição, perguntar que pergunta o instrumento responde de
> facto. Nas cinco vezes, a resposta estava certa — para outra pergunta.

---

## A12 · Revisão do V12 — pesquisa e posição, DECIDIDA PELO AUTOR (2026-09-30/10-01)

> **Estado a 2026-10-02: decidido e executado** — ver "O que o autor decide", mais abaixo, e a §A13.
> O título dizia "À ESPERA DO AUTOR" até essa data. O parágrafo seguinte é o estado de 29/09.
>
> **Estado:** nada executado. O autor pediu (2026-09-08) que a revisão do critério de limpeza
> fosse investigada e passasse pelo Fable **antes** de decidir. Isto é a investigação. A decisão é
> dele. Feita a 2026-09-08, **remedida a 2026-09-29** antes de ser escrita — e a remedição apanhou
> dois erros meus, marcados abaixo.

### A pergunta

O V12 decide se um ficheiro de registo sai por quatro perguntas. A quarta — *"algo de carga cita-o?
→ veto, fica"* — trata **qualquer** ponteiro de entrada como dependência. O autor objetou a guardar
ficheiros inteiros só por serem ponto de referência de uma decisão escrita noutro ficheiro vivo
(*"não podemos ficar criando uma chain de dependência"*), e propôs: comentário directo no ficheiro
vivo; apagar quando a decisão se justifica sozinha no contexto; e que apagar seja o desfecho natural.

### O que medi (2026-09-29)

| ficheiros de registo em `src_utils/` + `science/` | n |
|---|---|
| citados por **código** (`.py`/`.sh`) — intocáveis | 35 |
| citados numa linha **viva** de um `.tex` | **0** |
| citados **só dentro de comentários** — a categoria do autor | **36** |
| não citados por nada | 93 |

- **O raciocínio já está inline.** Os blocos de comentário que citam esses 36 têm até **143 linhas**
  e já declaram o defeito, os números e a decisão. O ficheiro externo é rótulo de origem, não
  dependência. A sugestão "comentário directo no ficheiro vivo" está, na maior parte, já feita.
- **A camada de comentários é 52% do texto entregue** (5 348 de 10 210 linhas, 54 ficheiros). Há um
  tecto: escrever mais inline agrava-o.

> ❌ **Erro meu, corrigido.** A 08/09 eu disse **55%** ao autor e ao Fable. O comando contava os
> capítulos duas vezes (47 entradas, 36 únicas) e falhava 18 ficheiros mais fundos. A conclusão
> aguenta; o número não.

### A posição do Fable, e onde concordo

1. **Trocar a pergunta 4 — mas por um teste de DUAS faces:** *o texto que cita fica de pé sozinho?*
   **e** *o ficheiro carrega alguma coisa própria que nenhum citador absorveu* (pendências, método,
   tabelas)? O teste de uma face só interroga quem cita, nunca o ficheiro.
2. **O corte decisão/medição faz-se por secção, não por ficheiro** — os relatórios de auditoria são
   todos mistos. E os 35 citados por código são mais intocáveis do que parecem: o
   `check_audit_claims.py` fixa o **conteúdo** deles por regex, não só o caminho.
3. **Não escrever mais inline.** O trabalho real por ficheiro é: triar o que é próprio → repontar as
   citações → apagar num commit que diga, ficheiro a ficheiro, para onde foi a carga.
4. **Antes do primeiro apagamento:** saber se a migração para o GitHub do departamento **preserva a
   história** (se não preservar, "restaura-se do git" morre nesse dia) e **criar uma tag**, para que
   todo o ponteiro pendurado tenha um endereço permanente.
5. **Começar pelos 93 que ninguém cita**, não pelos 36. É lá que o "apagar como desfecho natural"
   paga com risco quase nulo.

### ❌ O exemplo que sustentava a primeira face estava parcialmente caducado

O Fable ilustrou a segunda face com `src_utils/_history/_round14/80_apx_check2hgi_audit.md`, que declara duas
pendências "não aplicadas". Eu verifiquei a 08/09 que a frase **existia no ficheiro** e levei ao autor
que o **T2** — "nenhum capítulo aponta para o Apêndice E" — era um defeito aberto no volume.

**Não era.** O T2 foi verdadeiro no dia em que o ficheiro nasceu (2026-08-04: zero referências), e
foi corrigido até 2026-08-20: `2_fundamentals.tex` tem desde então
`Appendix~\ref{apx:check2hgi-joint-model} gives the exact composition and its width`. O ficheiro
continuou a dizer *"NOT APPLIED"*. Verifiquei que o ficheiro **dizia** que a pendência estava aberta,
não que **estava**. O **T1** (o `science/mtl_v17_complete_picture.md` ainda diz *"2-layer GRU"*)
continua aberto, mas numa nota da geração v17 — baixo risco.

**O que isto muda na posição:** reforça-a. A segunda face do teste não pode ser lida no ficheiro —
**uma pendência auto-declarada também caduca**, e tem de ser verificada contra a árvore, tal como os
ponteiros de linha.

### O que o autor decide

> ✅ **AS TRÊS DECIDIDAS pelo autor a 2026-09-30/10-01** — e executadas, ver **§A13**:
- a pergunta 4 passa a ser a de duas faces: **aprovado**;
- **a história não vai para o departamento.** O repositório de lá é **novo, criado a partir do nosso
  commit final** (autor, 2026-10-01): o que não estiver na árvore final não existe para um leitor
  público, e o histórico completo fica no `PoiMtlNet`. Criou-se a tag antes do primeiro apagamento
  (e a âncora `refs/backup/dissertacao-pre-organizacao`, porque `git fetch` apaga tags locais);
- a ordem seguiu o plano do Fable em 8 passos, dos binários sem leitor às rondas fechadas.

> ❌ **CORREÇÃO, 2026-10-01 (apanhada pela `knowladge`):** escrevi aqui a 29/09 que o `mtlcheck` era
> "outro clone" do `PoiMtlNet`. **É um worktree deste mesmo repositório** — o `.git` dele é um ficheiro
> com `gitdir: …/ingred/.git/worktrees/mtlcheck`. Medi o remote e o commit-raiz em comum, que são iguais
> num clone e num worktree, e concluí a partir de uma prova que não distinguia os dois. A
> consequência que tirei (esse passo preserva a história) mantém-se; a pergunta que deixei aberta já
> foi respondida acima.

---

## A13 · A reorganização para o repositório do departamento (2026-09-30 a 10-01)

Aprovada pelo autor a 2026-09-30, com o teste de duas faces (§A12) e a resposta à pergunta da
migração: o repositório do departamento nasce **sem histórico**, a partir do commit final.
Executada no ramo `dissertacao/organizacao-final`, em 8 commits separados, seguindo o plano do Fable.

| | antes | depois |
|---|---|---|
| ficheiros rastreados | 592 | **508** |
| pastas no topo de `src_utils/` | 16 | **4** (`_fixtures`, `_history`, `adaptation_ledgers`, `evidence`) |
| `.md` soltos na raiz | 9 | **8** (o `ACHADOS.md` veio para aqui) |
| links relativos partidos | 42 | **27** |

85 removidos (binários e dados brutos que ninguém lia, cópias derivadas, rascunhos superados), 164
movidos (`docs/` → `reviewers/research/` + `wrapup/`; `presentation/_preparacao/`;
`src_utils/evidence/`; `src_utils/_history/`), 70 editados no lugar (só caminhos e mapas).

**Como se verificou.** Linha de base dos 18 portões tirada com `build/` feito, num ambiente fixo, e
testada por sabotagem antes de lhe confiar. Depois de cada passo, saída idêntica. A única diferença
de texto em todo o trabalho é o próprio caminho `_history/` (passo 7), e uma linha que o
`check_verify_list` ecoa cortada a largura fixa. Nenhuma sonda deu SKIP. No texto entregue só
mudaram comentários, sempre uma linha por uma linha.

**O que nenhum diff mostrava, e foi apanhado:** dois scripts movidos encontram ficheiros por
aritmética sobre `__file__` e partiam ao descer um nível (`35_wave_a_render_check.py`,
`_check_pair_parity.py`). E a tag de segurança foi apagada **duas vezes** por `git fetch` de outras
sessões (`fetch.pruneTags=true` no `~/.gitconfig`); a âncora durável é
`refs/backup/dissertacao-pre-organizacao`.

**Registo ficheiro a ficheiro:** reconstrói-se com
`git diff -M --name-status "$(git log --format=%H --grep='^organizacao 1/8' -1)^" <fim> -- articles/dissertacao`; a razão de
cada ficheiro está na mensagem do commit do passo.

**O autor decidiu as quatro a 2026-10-01, e foram feitas no ramo:**
- **fundir e empurrar a tag:** fica com a `knowladge`, que funde o ramo no `main` e empurra os dois juntos;
- **as quatro fontes TikZ mortas saíram** de `presentation/figures/src/`, e o README diz onde se recuperam;
- **portabilidade:** os 13 `cd /Users/vitor/...` passaram à convenção do próprio `cwd_for`
  (`cd articles/dissertacao` a partir da raiz, `cd ../..` a partir da pasta). Com a mesma árvore, o
  portão dá saída idêntica antes e depois. A medição mostrou uma coisa que nenhuma comparação anterior
  podia mostrar: **até aqui, estes blocos verificavam o checkout principal em `/Users/vitor/...`, não a
  árvore onde o portão corria** — incluindo as minhas 18/18 por passo;
- **os dois ponteiros de fora** (`[mobiwac]/ERRATA.md`, `handoff/STORY_REVIEW.md`) apontam para os
  caminhos novos. Ficou um terceiro, que este registo dava como não aprovado e não editado: um
  comentário em `articles/[mobiwac]/src/figs/fig1_dataflow_new.tex` que cita `c2h_flow.tex`, que saiu
  com as TikZ. **Foi editado no mesmo dia** (commit `dcafac8a`, 2026-10-01): o comentário passa a dar
  o caminho completo e a tag de recuperação `dissertacao-pre-organizacao`. Corrigido aqui a
  2026-10-02.

---

## Procedência deste documento

Verificado por mim `[V]`: A1, A2, A3, A4, A5, A6 (exceto o exit code do `make check`), A7, A9, B2, B3.
Relatado e **não** reverificado `[R]`: o backup do `exemples/` da raiz, o exit code do `make check`,
a cobertura das canárias, o conteúdo do `RESULTS_BOARD`, o `ARMADILHAS_DE_MEDICAO.md`.

**Correções que eu fiz a briefings que recebi:** as linhas do NORTH_STAR (a real era a 67, e o
próprio banner apontava para portas limpas — **A4**); `science/` é proveniência, não dependência de
build (**A5**); `git check-ignore` precisa de `--no-index` (**A6**); o `6.909.789` já estava fechado
e os números emparelhados eram de estados diferentes (**A7**).

**Correções que me fizeram a mim, e o que aprendi de cada uma:**

| quem | o quê | a lição |
|---|---|---|
| o autor | eu disse que nada citava a gravação de 6,6 GB — citavam-na quatro documentos | verificar a premissa **antes** de a levar a uma decisão irreversível, não depois |
| `tikz` | usei md5 para decidir se dois PDFs eram versões diferentes | o md5 prova cópia, não conteúdo — e a regra estava escrita em `CLAUDE.md:109`, eu não a li antes de contradizer quem tinha razão |

As duas têm a mesma forma: **eu tinha o instrumento errado e a conclusão soava firme na mesma.**
É a razão de este documento separar `[V]` de `[R]` — para que a próxima pessoa possa desfazer o
meu trabalho pelo mesmo caminho por onde eu desfiz o dos outros.
