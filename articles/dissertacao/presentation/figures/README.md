# Figuras do deck de defesa

Quatro diagramas TikZ feitos para a defesa (28/08/2026). Três são desenhos novos;
o quarto é a variante de slide de uma figura da dissertação.

Entram no deck **sem `width=`** — já estão no tamanho final, e escalar afina os traços.
`graphicspath` do `slides/main.tex` já aponta para `figures/plates/`.

## O que está vivo

| PDF em `plates/` | tamanho | slide | fonte |
|---|---|---|---|
| `dgi_flow.pdf` | 394,3 × 150,3 pt | *Deep Graph Infomax (DGI)* | `src/dgi_flow.tex` |
| `hgi_flow.pdf` | 377,9 × 164,5 pt | *Hierarchical Graph Infomax (HGI)* | `src/hgi_flow.tex` |
| `c2h_deep.pdf` | 393,2 × 120,2 pt | *Check2HGI: a fourth level below the place* | `src/c2h_deep.tex` |
| `fig2_model_slides.pdf` | 283,6 × 196,5 pt | *The architecture: sharing by exchange* | `src/fig2_model_slides.tex` |

Cada `.tex` tem um cabeçalho longo explicando as decisões de desenho e a evidência
de cada uma. **Ler o cabeçalho antes de mexer** — várias escolhas que parecem
arbitrárias são deliberadas e estão justificadas ali.

## O que está morto

**As quatro fontes mortas saíram a 2026-10-01, por decisão do autor**: `dgi_flow_v1_semdelaunay`,
`c2h_deep_v1_conexo`, `c2h_flow` (variante de fluxo de dados, preterida) e `_hgi_flow_264pt_INCOMPLETO`
(a tentativa falhada da *Dívida* abaixo). Nenhuma era usada pelo deck. Recuperam-se no histórico do
PoiMtlNet, na tag `dissertacao-pre-organizacao`. Os PDFs de `superseded/` nunca estiveram no git.

- ⚠ `superseded/_hgi_flow_v1_376pt.pdf` — **o conteúdo é o mesmo do `plates/hgi_flow.pdf` vivo.**
  Ficou de um rollback: guardei-o antes de tentar regenerar a chapa, e depois reverti.
  Evidência: mesma página (377,87 × 164,53 pt) e render **idêntico pixel a pixel a 600 dpi**
  (`bbox` das diferenças = `None`). **O md5 difere, e não quer dizer nada** — estes PDFs não
  fixam `SOURCE_DATE_EPOCH`, então cada recompilação muda `/CreationDate` e o md5 nunca bate.
  Para comparar PDFs aqui, compara o **render** ou o texto extraído, nunca o md5.
  Só o autor decide apagar; e ⚠ como está debaixo do `*.pdf` do `.gitignore`, se sumir do
  disco some sem aparecer em diff nenhum.
- `png/`, `build/` — saída gerada, reconstrói com os scripts.

## Como reconstruir e reutilizar

**São duas toolchains diferentes. Isto não é óbvio e já causou confusão.**

**As três chapas novas** (`dgi_flow`, `hgi_flow`, `c2h_deep`) são **fragmentos TikZ**,
não compilam sozinhas. Precisam de um dos dois invólucros desta pasta:

```sh
./build.sh  dgi_flow "DGI"   # renderiza dentro de um slide beamer real -> png/
./export.sh dgi_flow         # exporta no tamanho final -> plates/
```

- `preview.tex` — invólucro beamer, para ver como fica no slide de verdade.
- `standalone.tex` — invólucro de exportação.
- Precisa: **xelatex**, `fontspec`, `cabin` e o `nesped.sty` (cópia do tema do deck, incluída aqui).
- ⚠ `standalone.tex` **tem de** fixar `\renewcommand{\familydefault}{\sfdefault}`. Sem isso os PDFs saem em serifada enquanto o deck é Cabin — invisível no preview, porque o beamer já carrega o tema.
- `export.sh` recusa exportar o que estoure o gabarito do slide.

**A quarta** (`fig2_model_slides`) é **standalone e usa outra toolchain**:

```sh
pdflatex fig2_model_slides.tex     # depois mover o PDF para plates/
```

Precisa **pdflatex** e `times` — não xelatex, não Cabin. É derivada de
`articles/[mobiwac]/src_fix/figs/fig2_model.tex`.

Para reutilizar uma figura noutro artigo: pegar o `.tex` de `src/`, não o PDF.
Os três fragmentos usam as cores do tema (`primary`, `secondary`, `alert`…), que vêm
do `nesped.sty`; fora do deck é preciso defini-las ou substituí-las.

## O que não se toca

**`src/figures/mobiwac/fig2_model.pdf` é figura do VOLUME, não chapa de slide.**
A `fig2_model_slides.pdf` daqui tem cinco rótulos trocados **de propósito**
(`Next Category`/`Next Region` em vez de `semantic`/`spatial stream`), decisão do autor
para a apresentação. A do volume **não pode receber a troca**: a legenda entregue, uma
linha abaixo dela, nomeia *(semantic)* e *(spatial)*, e mudar a figura poria o documento
depositado em contradição consigo mesmo.

🛑 **Nunca chamar uma chapa de `fig2_model.pdf` dentro de `plates/`.** O `graphicspath`
põe `plates/` antes de `../../src/figures/mobiwac/` — um ficheiro homónimo sombreia o da
dissertação **em silêncio**, e o deck passa a mostrar outra figura sem nada avisar.
O nome longo é a trava.

**`AUT-20` — divergência deliberada, não erro.** A chapa do HGI mostra o embedding
**corrompido** a alimentar o `Discrimination POI–Region`. O código não faz isso:
`neg_pois = pos_poi_emb[neg_poi_idx]` (`research/embeddings/hgi/model/HGIModule.py:281`),
o negativo daquela fronteira é outro POI da tabela **original**. O autor decidiu manter a
versão dele com os dois renders lado a lado, e há resposta oral registada. **Não reabrir.**

## Dívida aberta

`hgi_flow` entra no slide com `\includegraphics[width=0.80\textwidth]` — os traços
saem ~20 % mais finos. O certo seria regenerar no tamanho final (~302 pt de largura,
= 0,80 × 377,9). O autor autorizou a redução.

⚠ **Tentei e não deu; o resultado negativo poupa a próxima tentativa.** Uma transformação
mecânica (escalar coordenadas, dimensões absolutas × fator, `line width` intocado) **não**
regenera esta chapa: os pictogramas não encolhem na proporção das caixas, e os rótulos
`Delaunay` e `Geographic adjacency`, posicionados à mão, encostam nos grafos. Falta uma
rodada de composição, não um `sed`. O trabalho parado (`src/_hgi_flow_264pt_INCOMPLETO.tex`) saiu a 2026-10-01; está no histórico do PoiMtlNet, tag `dissertacao-pre-organizacao`.

E há um limite estrutural: varrendo `scale` × fonte, a razão largura/altura fica presa em
~2,26 e nunca volta aos 2,299 do original — **os traços em peso cheio *são* a altura extra**.
Não existe versão com traço cheio e a mesma altura renderizada; só dá para escolher de que
lado fica o erro.

## Antes de subir ao git

Hoje **só os 4 PDFs de `plates/` estão versionados**. Todo o `src/` está de fora — quem
clonar recebe as imagens e nenhuma forma de as alterar, que é o oposto do objetivo.

Devem entrar: `src/*.tex`, `preview.tex`, `standalone.tex`, `build.sh`, `export.sh`,
`nesped.sty`, este README.
Não devem: `build/` (já ignorado) e `png/` (saída gerada, ~20 ficheiros).
`superseded/*.pdf` já é ignorado pelo `.gitignore` da pasta (exceção só para `!figures/plates/*.pdf`, linha 37).

⚠ **`git check-ignore` consulta o índice**: para um caminho já rastreado responde "não ignorado",
mesmo que a regra o apanhasse. Usa `--no-index` quando quiseres saber o que a **regra** faz.

---

# Como fazer uma chapa nova sem destoar

Isto é o método, não o inventário. Com este ficheiro mais um `.tex` de `src/` ao lado,
dá para produzir uma figura que pareça da mesma família.

## A paleta vem do tema — não se inventa cor

Definida em `nesped.sty:27-37`, e as chapas usam-na por nome:

| nome | rgb | o que significa **nestas figuras** |
|---|---|---|
| `secondary` | `0.04, 0.27, 0.47` | o caminho **original**: traço, caixa, rótulo |
| `alert` | `0.74, 0.07, 0.43` | o caminho **corrompido / amostra negativa** |
| `primary` / `primaryshade` | `0.22, 0.69, 0.61` | o **contexto** (o resumo global no DGI, a cidade no HGI) |
| `secondarytint` / `primarytint` | `0.88,0.92,0.96` / `0.90,0.95,0.94` | preenchimento das caixas que fazem julgamento |
| `black!48`, tracejado | — | **gradiente / sinal de treino** |

Duas cores de fora da paleta, e só onde era preciso separar duas coisas do mesmo tipo:
`discA` âmbar `0.74,0.50,0.05` e `discB` violeta `0.36,0.29,0.58`, uma por fronteira
contrastiva no HGI.

🛑 **Uma cor, um significado.** Foi por isso que o gradiente do DGI deixou de ser magenta:
magenta passou a querer dizer "negativo" e não podia querer dizer também "sinal de treino".
Se precisares de uma cor nova, primeiro verifica se não estás a reutilizar uma que já fala.

## Espessuras e setas — valores, não adjetivos

```
fluxo de dados        ->, line width=1.1pt        (1,3pt na chapa do DGI, que é mais aberta)
ponta                 >={Latex[length=2mm]}       (2,6mm no DGI; 1,4mm dentro de pictogramas)
borda de caixa        line width=1pt              rounded corners=2.5pt, inner sep=4pt
moldura de grafo      line width=1pt / 1,2pt no ramo corrompido, inner sep=1.0mm
maquinaria de treino  dashed                      nunca traço cheio
célula de vetor       3,4 × 1,8 mm (HGI) · 4,0 × 2,1 mm (Check2HGI) · 4,2 × 2,2 mm (DGI)
corpo                 \small; \normalsize só nos rótulos de caixa
```

Bordas **sólidas** nas caixas, mesmo quando o conteúdo é tracejado: borda tracejada faz as
pontas de seta dissolverem-se contra ela. Para a ponta ficar *acima* da borda, `shorten >=2pt`.

## As convenções de significado

Isto é o que ninguém deduz do código, e é o que faz duas figuras diferentes parecerem
da mesma família.

**Duas raias.** Original em cima em `secondary`, corrompida em baixo em `alert` — moldura,
rótulo e vetor de saída, tudo na mesma cor. O leitor aprende a convenção uma vez e lê as
três chapas.

**Uma caixa única que atravessa as duas raias significa "a mesma rede".** É assim que se
desenha o `same GCN` sem escrever "same weights". De quebra, uma caixa alta deixa as setas
das duas raias entrarem **horizontais** — se ela for baixa, as setas fazem um Z (coto,
vertical, coto) que em tamanho de tela lê como três traços soltos, não como uma seta.

**O vão entre as duas raias carrega o nome do método** que constrói o grafo: `Delaunay` no
DGI, `Delaunay` / `Geographic adjacency` no HGI, `directed visit sequence` no Check2HGI.
Sempre no mesmo sítio, nas três.

**As setas saem da MOLDURA do grafo, não de um nó.** Desenhar um `\node[fit=...]` à volta
do grafo e puxar de `.east`: assim é o *grafo* que alimenta a rede, e não o nó que por acaso
está mais à direita.

**Vetores são glifos**, células empilhadas, nunca uma caixa com a palavra "embedding".

**Cada fronteira contrastiva tem a sua cor e vai da fonte até à perda sem interrupção.**
Se duas fronteiras partilharem cor ou se cruzarem, a figura fica ilegível — foi o defeito
que mais rodadas custou no HGI.

**O tamanho do pictograma de grafo é intocável.** É o que faz as chapas parecerem parentes.
Quando faltou altura, a economia veio da moldura e das folgas de legenda — nunca do grafo.

## Famílias: desenha a mais funda primeiro

A chapa do Check2HGI é a do HGI **com um andar a mais em baixo**. O caminho seguro é
desenhar a mais profunda e **derivar a outra removendo o andar**, para garantir que são o
mesmo desenho menos um nível. Ao contrário, as duas divergem em detalhes e o argumento
"é o mesmo método, um nível mais fundo" perde-se.

## A regra de tamanho, e como se aplica

**Nunca reduzir com `width=`; regenerar no tamanho final.** Escalar afina os traços na
mesma proporção — a 0,70 perdem 30 % da espessura.

Procedimento: pedir a quem monta o deck a **área útil medida** do frame (aqui: 140 mm de
largura; ~63,7 mm de altura com título de uma linha, ~60 mm com duas), desenhar dentro
disso, e exportar com `export.sh`, que **recusa** o que estoure.

⚠ **E há um limite que só se descobre medindo:** traço em peso cheio **é** altura extra —
uma borda de 1 pt ocupa mais espaço do que a mesma borda escalada a 0,7 pt. Uma chapa
regenerada nunca reproduz a proporção da versão reduzida. Não existe "traço cheio *e* a
mesma altura"; escolhe-se de que lado fica o erro. Se o frame estiver no limite, entregar
a chapa **menor nas duas dimensões** é o lado seguro.

## O que só aparece no render

Cinco defeitos que compilam sem aviso e passam no log:

**Setas que apontam para trás.** `-|` e `|-` não são intercambiáveis, e se o cotovelo cair
à direita da âncora de destino a ponta inverte. Compila, não avisa, e só se vê ampliando.

**A fonte errada.** O invólucro de exportação carregava `fontspec` sem fixar a família, e
os PDFs saíam em serifada enquanto o deck é Cabin. **Invisível no preview**, porque o
preview carrega o tema do deck. Passou onze rodadas despercebido. Confere com `pdffonts`.

**Medir largura de texto na classe errada.** A base do beamer é **11 pt**, então `\small`
são 10 e `\footnotesize` são 9 — um ponto acima do que `article` dá. Um rótulo que "cabia"
estourou por 4,4 pt. Mede num documento beamer, ou deduz do `Overfull` em pt.

**Estimar largura de palavra.** Não funciona. `Contrastive` tem 2,36 cm em Cabin negrito,
não os 2,0 que eu supunha; `Check-in` tem 1,19 e não 1,5. Quatro rodadas gastas nisto.

**Validar o preview em vez do artefacto.** Confere sempre o PDF que foi entregue, por um
caminho diferente do que o produziu — extração de texto, `pdfinfo`, `pdffonts`. Um script
com falha-segura só vale depois de a teres visto disparar.
