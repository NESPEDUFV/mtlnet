# PENDENCIAS.md — o que falta, e de quem depende

**Fila viva. Se um item nao espera nada de ninguem, ele nao mora aqui.**

## Como este arquivo funciona

**Cada item tem a mesma forma, e ela e curta:**

```
### N.M Titulo de uma linha
**O que e.** Uma a tres frases: o achado, com o numero medido.
> **DECISAO SUA:** o que falta, com as opcoes e o custo de cada uma.
*Forense: ponteiro para o relatorio de rodada.*
```

**Onde cada coisa vive.** O tracker carrega a **decisao**; a **forense** (como o defeito foi descoberto, qual
instrumento mentiu, o que cada commit mediu) vai para `_history/_round8/`. Em 2026-07-30 seis itens carregavam 34 mil dos 55 mil
caracteres do arquivo, quase tudo forense: foi para
[`_history/_round8/29_pendencias_detail.md`](_history/_round8/29_pendencias_detail.md), **nada apagado**, e o arquivo caiu de 67 mil para
37 mil.

**Para ADICIONAR um ponto seu:** escreva embaixo do item, comecando a linha com `> DECISSAO:` (ou
`> DECISAO:`). Eu leio isso como sua palavra final e nao reinterpreto. Se voce nao tiver numero de item, escreva no fim
do §2 com um titulo qualquer — eu numero e coloco no lugar.

**Para FECHAR um item:** ele sai daqui e vai para `_history/_archive/PENDENCIAS_RESOLVIDOS.md` **com o motivo de saida no topo do
bloco**. O gate `check_tracker_refs.py` falha se um item desaparecer sem chegar ao arquivo — tres foram perdidos assim,
e voce achou dois deles lendo o arquivo. **Nao renumere:**
comentarios no fonte citam estes numeros, e um buraco na numeracao e melhor que um ponteiro errado.

**Ordem das secoes:** §2 (voce) -> §3 (terceiros) -> §4 (o que auditar primeiro). Deliberada: o que depende de voce vem
antes. **§5 removida em 2026-08-03** (retirado; os onze itens que apontava continuam em
`_history/_archive/PENDENCIAS_RESOLVIDOS.md`, re-medidos e intactos).

**O §6 saiu deste arquivo em 2026-08-03, a seu pedido, e nao foi perdido.** Ele entrou em 2026-07-30 substituindo o §2.8
e carregou vinte e seis itens vindos do `CONSIDERATIONS.md`; **os vinte e seis foram respondidos por voce** e estao em
`_history/_archive/PENDENCIAS_RESOLVIDOS.md`, cada um com o motivo da saida no topo do bloco e sob o cabecalho que registra o
encerramento da secao inteira. A numeracao 6.1 a 6.26 **nao** foi reaproveitada, e as dezenove citacoes que apontavam
para ca foram repontadas para o arquivo na forma historica que o `check_tracker_refs.py` reconhece. O §6 seguiu a mesma
trajetoria do §2.8: deixou de pedir decisao e virou registro.

---

## §2 · Aberto e bloqueado em VOCE

> **LIMPO EM 2026-07-30, a seu pedido.** Cinco itens desta secao estavam **de fato fechados** e foram
> movidos para `_history/_archive/PENDENCIAS_RESOLVIDOS.md` com o motivo de saida no topo de cada bloco:
> **2.2** (push publicado, verificado por hash contra o remoto — o resto virou 2.16), **2.3** (fechado
> pela sua frase *"podemos fechar esse ponto"*), **2.7** (orcamento de tuning nao-recuperavel,
> registrado em `LEFT_OUT.md`), **2.13** (o comando contava 4 a mais por ser cego a comentarios;
> corrigido) e **2.17** (afirmacao falsa minha, corrigida com nota de git em `a07e547b`).
>
> **Os buracos na numeracao — 2.2, 2.3, 2.7, 2.13, 2.17 — sao esses cinco, e nao perdas.** Nao
> renumerei os que ficaram: seis comentarios no fonte e o `_history/_round6/VERIFY_LIST.md` citam estes numeros,
> e renumerar transformaria cada citacao num ponteiro para o item errado, que e pior que um buraco.
> O gate `check_tracker_refs.py` agora falha se um item sair daqui sem chegar ao arquivo.
>
> **O que sobrou aqui espera VOCE, nao a mim.** Onde a medicao esta completa, o bloco `(A)/(B)/(C)`
> diz exatamente o que falta e quanto custa cada saida.

### 2.1 Os marcadores `[NEEDS SIGN-OFF]` no fonte — **56** medidos em 2026-08-02, agora com mapa item por item

> **MORTO (2026-08-12, `wrapup/open_points/LACUNAS.md` §5; anotado aqui a 2026-10-02).** A contagem de 56
> esta invalidada: sao 34 marcadores, 32 anotados `CLOSED` e um so `OPEN`, o item 46, cujo ficheiro
> (`apx_b_static_scope.tex`) nenhum build inclui. Nada aqui espera decisao. Fica no lugar, e nao no
> arquivo, ate alguem o mover com o motivo de saida, como manda o topo deste ficheiro.


**O que e.** Pontos do fonte marcados como precisando do seu aval. Nenhum bloqueia build, e **nenhum aparece no PDF**:
todos vivem em comentario `%`. **O numero anda** — tracks paralelas removem marcadores conforme voce decide.

**Novo em 2026-08-02: [`src_utils/_history/NEEDS_SIGN_OFF.md`](_history/NEEDS_SIGN_OFF.md)** traduz os 56 marcadores para PT-BR, um por
um, com contexto, a pergunta exata e um espaco `> **SUA DECISAO:**` para voce responder — o mesmo padrao deste arquivo.
Cada item foi conferido contra o fonte vivo (`grep` na linha exata) antes de entrar no mapa. Quando um item for
resolvido la, ele sai daquele arquivo e o `[NEEDS SIGN-OFF]` correspondente sai do `.tex`. Confie no comando, nao no
titulo:

```bash
cd articles/dissertacao
grep -rc "\[NEEDS SIGN-OFF" src --include="*.tex" --exclude-dir=build | grep -v ":0$" | sort -t: -k2 -rn
```

Medido assim em 2026-07-30 sobre `5c074a2a` mais a arvore de trabalho: **54 marcadores em 21 arquivos** (52 com corpo
`[NEEDS SIGN-OFF: ...]` e 2 retrovisores nus `[NEEDS SIGN-OFF]`); 58 se `src/build/` entrar, porque
`build/fmt/_body.tex`
e copia gerada — dai o `--exclude-dir=build`.

*(O comando que estava aqui — `grep -rn ... | grep -v ":\s*%"` — imprimia **zero linhas** e saia `rc=1`: o `-v` casa o
`%` do comentario em que cada marcador vive, entao removia justamente tudo o que devia contar. E nenhum gate conta estes
marcadores: `check_verify_list` executa blocos documentados, nao mede esta contagem, ao contrario do que este item
afirmava.)*

**Tres tem prioridade** (afirmam algo sobre trabalho publicado ou co-autorado): o paragrafo corrigido do Apendice B
sobre o Cap. 3, o numero limitado do Cap. 4 na conclusao, e a frase de reprodutibilidade enfraquecida. Estao detalhados
em `_history/_round6/VERIFY_LIST.md` A1, A2 e A3.

> **DECISAO SUA:** ler os 53 e me dizer quais aprova. Nao precisa ser de uma vez — se me der os tres
> prioritarios, eu removo os marcadores deles e mantenho os outros 50.

*Forense (a tentativa de push destrutiva, o worktree, os artefatos divergentes): agora e o item 2.16 e o corpo integral
esta em [`_history/_round8/29_pendencias_detail.md`](_history/_round8/29_pendencias_detail.md).*

### 2.5 O tamanho de tipo das duas figuras de arquitetura — autorizado, mas eu nao consigo executar

**Voce autorizou:** *"pode aumentar, mas mantenha o espaco ja ocupado pela imagem... mantendo a proporcao"*, e observou
que o contraste hoje ja deixa legivel.

**Nao consigo fazer daqui:** nao ha `drawio` nem `inkscape` neste ambiente. **Os dois `.drawio` estao no repositorio** —
`figures/mtlnet_poi_new.drawio` (13.640 B, `fontSize=14`) e `figures/courb/arquitetura_modelo.drawio`
(14.588 B, `fontSize=13`), medidos em 2026-07-30 com `find . -name '*.drawio'` (quatro no repo inteiro). A receita esta
em `_history/_round6/12_figures.md` (subir `fontSize` para ~20 e reexportar na mesma largura em pixels).

*(Este bloco dizia **"so 1 dos 2"**. Era falso, e o commit `b89a9876` ja tinha diagnosticado exatamente isso — o
instrumento era `ls src/figures/*.drawio`, glob nao-recursivo que nao ve `figures/courb/` — mas a correcao nao chegou ao
arquivo. Tamanhos de tipo medidos, no `LEFT_OUT.md` LO-6: **45,3%** do corpo no do Cap. 3 e **44,4%** no do Cap. 4,
contra corpo de 11,96 pt. O raster do Cap. 3 e byte-identico ao publicado do CBIC, conferido por sha256.)*

> **Seu, quando quiser:** reexportar as duas no Draw.io e me passar os PNG — eu troco e remeco o tipo na
> pagina. **Opcional**, pela sua propria observacao sobre o contraste.

### 2.27 A arvore revisada do autor entrou no `src`, e o que ficou aberto nela

> **MORTO (2026-08-12, `wrapup/open_points/LACUNAS.md` §5; anotado aqui a 2026-10-02).** O item 1 (28
> blocos `ORPHANED`; medidos 16), o item 2 (54 marcadores abertos; sao 34, 32 `CLOSED`) e o (C) (as
> paginas) estao invalidados; os itens 3 e 4 sao registo, sem decisao pedida. Nada aqui espera decisao.


**(A) O que e.** Em 2026-08-02 o autor entregou `src_clean`, lido e editado por ele. O merge esta em
`src_utils/_history/_round9/49_clean_tree_merge.md`. A prosa dele entrou byte a byte nos 54 arquivos; a camada de comentario do
`src` (4.114 linhas, 275 blocos, 54 marcadores `[NEEDS SIGN-OFF]`) foi reancorada por cima. 228 dos 275 blocos
reancoraram exatamente.

**(B) O que fica aberto para voce.**

1. **28 blocos marcados `[ORPHANED 2026-08-02]`** — eram 47, e voce resolveu 19 no commit `45c75611`
   ("remove orphaned comments and clean up LaTeX files"). Medido em 2026-08-02:
   `grep -rho 'ORPHANED 2026-08-02' src --include='*.tex' --exclude-dir=build | wc -l` = **28**. Cada um anota uma frase
   que a sua revisao reescreveu ou cortou; nenhum foi apagado por mim. A tabela original dos 47 esta no relatorio 49.
   Sao seus para manter, reescrever ou deletar; um agente nao deve decidir isso.

2. **54 marcadores `[NEEDS SIGN-OFF]` continuam abertos**, distribuidos em 21 arquivos, com 7 em
   `2_fundamentals.tex`, 8 em `6_conclusion.tex` e 6 em `apx_a_contributions.tex`. Sao afirmacoes que nenhum artigo
   publicado sustenta e que dependem da sua assinatura.

3. **A grafia do termo central foi uniformizada em "multitask"**, como manda `GLOSSARY.md:130`. As 36 ocorrencias
   hifenizadas que restam sao TITULOS CITADOS no `references.bib` e nao podem ser alteradas sem falsear as fontes.

4. **`apx_g_hgi_tuning.tex` e um apendice novo seu**, que recebeu a varredura do peso do HGI que saiu do capitulo 2.
   Renderiza na p. 106 da defesa. Ele nao esta no `main_extra`, so no volume principal.

**(C) Status.** Builds 106/103/107/22 pp, zero erros, zero referencias indefinidas; 25 gates e o selftest em rc=0, lidos
diretamente.

### 2.28 Varredura de auditoria de 2026-08-02: 14 itens fechados, 5 abertos, 2 surpresas

**(A) O que foi feito.** Voce pediu para auditar cada item do §2 e do §5, medindo o estado do documento em vez de ler o
cabecalho do proprio item. Os 19 itens em escopo foram medidos contra a arvore em `45c75611`
mais a arvore de trabalho. **14 fecharam e foram para
[`_history/_archive/PENDENCIAS_RESOLVIDOS.md`](_history/_archive/PENDENCIAS_RESOLVIDOS.md)** com a evidencia e a sua decisao preservadas
verbatim; 51 citacoes a esses itens foram reapontadas para o arquivo, mais 3 no `GLOSSARY.md`
e neste arquivo, e o gate `check_tracker_refs` voltou a rc=0.

**(B) As duas surpresas, e as duas vao nas duas direcoes.**

1. **`2.26` estava dado por resolvido e nao estava.** Voce escreveu "Aplique o R15-10 e o R15-09" e nenhum dos dois
   havia sido aplicado: `"Two patterns stand out in the data."` e `"Settling that needs"` continuavam na prosa viva do
   apendice do cosseno. **Aplicados agora** (2026-08-02): `"The figure shows two patterns."` e
   `"Answering that question needs the same diagnostic"`.

2. **`EX-9` dentro do `2.23`: a sua revisao desfez a sua propria decisao.** Voce escreveu "nao aplique o EX-9", cuja
   familia eram quatro frases (`deserves one statement`, `worth reporting`, `needs saying`,
   `worth stating`). Todas as quatro **sairam** da prosa viva; `git log -S` mostra duas saindo no seu proprio
   `src_clean` (`807183c1`). Voce foi consultado e decidiu que a sua leitura com o texto na mao superseda a decisao
   anterior. Registrado como SUPERSEDIDO, nao como aplicado. **E o meu probe nao pegou isso:** o `A23-EX9` vigiava
   `"Pareto front"`, que continua no texto, em vez das frases que a decisao protegia — passava enquanto a decisao era
   desfeita. Reapontado para a definicao de fronteira de Pareto que voce de fato manteve, e validado nos dois sentidos.

**(C) Um item que o tracker dava por aberto e estava aplicado.** O `2.20` (italico em ingles corriqueiro no Cap. 4): a
sua opcao 2 esta aplicada. `\textit` na prosa viva do Cap. 4 = **48**, contra 157 no fonte em `5c074a2a`; os
sobreviventes sao os 7 nomes de categoria, nomes de modelo e substantivos proprios. Duas formas arguveis sobraram
(`one-hot`, `skip-gram`) e nao mexi nelas.

**(D) Segunda passagem, 2026-08-02: o §5 retirado, e o 2.21 e o 2.24 fechados.** O §5 foi **re-medido** depois da fusao
e virou ponteiro: os onze itens estao no arquivo e as conclusoes sobreviveram (o comando do proprio banner ainda
reproduz o que ele afirmava). O **2.21** fechou — o termo que o seu orientador marcou,
`license the verbs`, ja tinha saido do Cap. 2 na sua revisao, e a metafora foi trocada por `supports` nos tres sitios
vivos restantes mais a glosa do `GLOSSARY`; os usos em `apx_e_ethics.tex` ficaram, porque ali
`license` e licenca de software de verdade. O **2.24** fechou nas duas metades: a norma ABNT NBR 10520:2023 esta na §1
do `WRITING_LAW` com gate e self-test, dois fragmentos foram corrigidos e a citacao de frase completa ficou por sua
isencao; e o `towards` fica como esta por sua decisao, com a entrada do
`OPEN_REGISTER` como registro permanente dela.

**Sobram tres itens seus:** `2.1`, `2.5` e `2.27`.

*Forense: [`_history/_round9/50_pendencias_audit.md`](_history/_round9/50_pendencias_audit.md), com a medicao de cada um dos 19.*

### 2.29 Rodada 12, 2026-08-03 — o §6 fechou inteiro, as duas linhas do `GLOSSARY` entraram, e voce mesmo escreveu a D2

**Registro, nao pedido.** Nada aqui espera voce; esta secao existe para que nada disto seja reaberto.

**AS DUAS LINHAS DA §1.1, aplicadas por mim sob a sua autorizacao explicita.** Voce disse "eu autorizo voce a colar elas
no glossary", que e a **opcao 3** do antigo §6.26 e nao a 1 — a diferenca importa, porque a regra da casa e que a tabela
de notacao e sua e um agente **propoe** linhas. As duas fecham uma lacuna fail-closed medida: o $\mathbf{e}_{x_i}$
estava em uso vivo na Definicao 2.4 e o $f_{\mathrm{place}} (H_i)$ na 2.9, e nenhum dos dois estava registrado. Isso
completa a **AD-5**. **E a consequencia que a propria opcao 3 previa foi cumprida no mesmo commit:** o comentario do
`2_fundamentals.tex` afirmava, verbatim, que a linha
"is PROPOSED to the author and is not written by an agent; the notation table is his" — verdadeiro quando escrito e
**tornado falso pelo ato de escrever a linha**. Ele agora cita a frase antiga como superada, diz que voce autorizou a
excecao, e mantem a regra geral de pe.

**O §6 SAIU INTEIRO, a seu pedido.** Os vinte e seis itens foram respondidos por voce, os dez `______` que restavam eram
**residuo de formatacao** (cada um ja respondido em outra secao, conferido um por um), e a
`h3` e o cabecalho `## §6` foram removidos. **Duas coisas que eu conferi porque este arquivo manda:**

1. **Chegada antes de apagar.** Para cada bloco eu confeti que o cabecalho **e** uma linha interior do corpo estavam no
   `_history/_archive/PENDENCIAS_RESOLVIDOS.md` antes de remover. Tres itens desta lista se perderam no passado exatamente por
   apagar antes de conferir.
2. **Ponteiros.** Remover a secao orfanou **dezenove** citacoes no fonte e **quatro probes**. As citacoes foram
   repontadas para a forma historica que o `check_tracker_refs.py` reconhece
   (`PENDENCIAS_RESOLVIDOS <n>.<m> (arquivado 2026-08-03)`), e os quatro probes (`R9-pend6`, `R9-blq4`,
   `R9-blq5`, `R12-extra`) passaram a ler o arquivo — cada string **verificada presente lá** antes do repoint, nao
   suposta. O `R9-pend6` deixou de pinar um cabecalho que voce mandou remover e passa a pinar o registro do
   encerramento, com o `R9-pend6b` guardando o cabecalho citado verbatim para quem encontrar um comentario antigo
   dizendo "§6". A numeracao 6.1 a 6.26 **nao** foi reaproveitada.

**A SUA D2, afiada em cima e nao reescrita (AD-6).** Voce substituiu a frase vaga de retencao pela sua, que nomeia o
alvo por tarefa e enuncia a posse do rotulo. Tres afiamentos, nenhum tocando o seu conteudo:

- **Referencia para frente.** A sua frase era a **primeira** ocorrencia viva de "next-category prediction" e
  "next-region prediction" no capitulo, e as duas sao definidas ~130 linhas adiante. Medido, nao suposto. Os simbolos
  estavam bem (a D1 vincula o $c_i$ e o $r_i$), entao e mais leve que um simbolo-antes-da-definicao, mas e a propriedade
  que a ordem dos passos do redesenho existia para proteger. Resolvido apontando para frente **explicitamente**, em vez
  de tirar os nomes das tarefas que voce escolheu.
- **A metade positiva.** Excluir o rotulo do $x_i$ afasta o vazamento; faltava dizer que as categorias e as regioes das
  visitas **passadas** sao entrada legitima — que e exatamente a duvida que gerou a sua edicao. Agora esta dito numa
  oracao.
- Largura de linha de volta as ~85 colunas do arquivo.

**Nada mudou na 2.5, e isso e deliberado.** A sua leitura estava certa: um "historico de regioes" e uma **projecao**
de $H_i$ e nao uma entrada diferente, porque a regiao ja esta dentro do check-in pela D1, e o que o modelo le
e $\rho (H_i)$. Se a definicao da tarefa dissesse "recebe um historico de regioes", ela passaria a descrever a escolha
de representacao do Cap. 5 e o Cap. 3 nao caberia mais nela.

**Um defeito meu, apanhado por um revisor:** eu publiquei "os oito probes novos validados por sabotagem"
quando eram **sete**. O oitavo era justamente o probe de **ausencia** — o unico cuja falha e o silencio. Corrigido,
validado nos dois ramos, e a regra que evita a repeticao esta no `_history/_round9/34`: reconciliar os nomes dos probes validados
contra os adicionados **como conjuntos**, nao pela contagem de linhas.

### 2.31 Sete pontos removidos, mas dois grupos de referencia cruzada ficaram de fora por sua instrucao explicita

**O que foi feito** (registrado em `_history/_archive/PENDENCIAS_RESOLVIDOS.md §2.30`): as duas sentencas de
primeira-autoria do Tarik e os sete ponteiros `Appendix~[B/D] of \extravolume` (volume principal ->
volume suplementar) foram removidos dos capitulos 3-5.

> **VOCE DISSE, verbatim: "Documente this in the pendencias.md and let me decide in future"** e depois
> **"For now we shoudl focus on the remotaion of the eappendixs that are in the extra volume that are
> been refs in the other chapters."** Este item registra os dois grupos que ficaram **fora** desta
> rodada, exatamente porque voce pediu para decidir depois e nao agora.

**Grupo 1 — o ponteiro de apendice DENTRO do volume principal.** Um corpo de artigo aponta para um
apendice do mesmo documento (nao para o volume suplementar), o que ainda e uma referencia de um
capitulo para "fora de si mesmo":

- `chapters/5_mobiwac/02_related.tex` (linha ~25): *"Appendix~\ref{apx:cosine} reports the
  gradient-cosine diagnostic of this chapter on the final model across seven datasets."*

**Grupo 2 — os seis ponteiros `Chapter~\ref{ch:...}` entre os corpos dos tres artigos.** Cada um faz um
capitulo apontar para um capitulo irmao dentro do proprio corpo do artigo (nao na preface, que e prosa
de moldura e nao prosa reproduzida do artigo):

- `chapters/3_cbic/results.tex` (linha ~30): *"...Chapter~\ref{ch:mobiwac} adopts a stricter
  user-disjoint protocol."*
- `chapters/4_courb/related.tex` (linha ~45): *"The baseline of this study is MTLnet, the joint
  architecture introduced in Chapter~\ref{ch:cbic}..."*
- `chapters/4_courb/related.tex` (linha ~47): *"The evaluation in Chapter~\ref{ch:cbic} found that
  this joint model performed on par with the dedicated single-task models..."*
- `chapters/4_courb/results.tex` (linha ~14): *"...Chapter~\ref{ch:mobiwac} adopts a stricter
  user-disjoint protocol."*
- `chapters/5_mobiwac/02_related.tex` (linha ~26): *"Chapter~\ref{ch:cbic} introduced MTLnet, the
  first..."*
- `chapters/5_mobiwac/02_related.tex` (linha ~32): *"Chapter~\ref{ch:courb} kept the MTLnet
  architecture unchanged and replaced its..."*

**Por que ficaram de fora, e nao apenas esquecidos.** Varias destas sentencas carregam um fato que o
adaptation ledger do respectivo capitulo registra como ponte deliberada entre os tres artigos (ex.:
`4_courb_ADAPTATION_LEDGER.md` cita a comparacao explicita de protocolo com o Cap. 5). Remove-las nao
e um corte mecanico como os sete `\extravolume`: cada uma exigiria decidir se o fato sobrevive
reescrito sem nomear o capitulo irmao, ou se desaparece.

> **DECISAO SUA:** quando quiser revisitar, decida por grupo ou por linha se cada capitulo 3-5 deve
> ficar completamente autonomo (nenhuma referencia a outro capitulo ou apendice do volume principal),
> e eu aplico a mesma disciplina que os sete `\extravolume`: dobrar o fato in-line onde carrega
> conteudo, cortar onde e ponteiro puro.

> **FECHADO na rodada 14 (2026-08-04).** Voce deu exatamente essa decisao: *"In the articles(chap 3
> to 5), they must work as a standalone text, so they must not have a mention of the appendix of the
> dissertation or to sections of the dissertations."* Os dois grupos acima foram aplicados: sete
> referencias cruzadas removidas de quatro arquivos de corpo, com a disciplina prometida (dobrar o
> fato onde ele carrega conteudo, cortar onde e ponteiro puro). O MTLnet passou a ser introduzido por
> citacao ao artigo publicado (CBIC 2025) em vez de por numero de capitulo; as divulgacoes de
> protocolo (split estratificado por amostra, cinco folds em uma semente) **permaneceram integras** e
> so perderam a comparacao com o Cap. 5. As prefaces mantiveram a moldura entre capitulos, porque o
> `NORTH_STAR` a exige e a preface e prosa de moldura, nao prosa reproduzida do artigo. Probes
> `STL-01` a `STL-05` guardam o resultado, cada um validado por sabotagem. Commit `2bb82234`.

### 2.32 O Apendice E (Check2HGI e o modelo conjunto) nao e citado por nenhum capitulo

> **MORTO (2026-08-12, `wrapup/open_points/LACUNAS.md` §5; anotado aqui a 2026-10-02).** A saida (b)
> foi aplicada: o `2_fundamentals.tex` tem um `\ref` vivo para o apendice, e ele imprime no Cap. 2
> ("Appendix E gives the exact composition and its width"). A decisao pedida abaixo ja nao se aplica.


**O fato, medido.** O rotulo `apx:check2hgi-joint-model` aparece **zero** vezes como `\ref` em prosa
viva em todo o `src/chapters/` e `src/tables/`. A unica ocorrencia no documento e a propria
declaracao `\label` na linha 3 de `chapters/apx_h_check2hgi_joint_model.tex`, e um `\label` nao e uma
referencia. Comando que reproduz a medicao:

```bash
cd articles/dissertacao
for f in $(find src/chapters src/tables -name "*.tex"); do
  n=$(grep -v '^[[:space:]]*%' "$f" | grep -c "ref{apx:check2hgi-joint-model}")
  [ "$n" != "0" ] && echo "$f: $n"
done   # nao imprime nada
```

**Por que isso importa.** Compare com o apendice do cosseno de gradientes, que e apontado de tres
lugares em prosa viva (`1_introduction.tex`, `2_fundamentals.tex`, `6_conclusion.tex`). Um leitor que
chega ao Apendice E chegou por acidente: nenhum ponto do argumento diz que a explicacao operacional
do Check2HGI e do modelo conjunto existe. Sao dez paginas (107-116 no build de defesa) que o
documento nao anuncia.

**Por que eu nao apliquei.** Duas razoes, e a segunda e a que manda:

1. O hospedeiro natural e o Capitulo 5, cujo corpo esta sob o regime de errata do artigo submetido
   (`NORTH_STAR` §4 reserva alteracoes no corpo dele). Um ponteiro novo ali nao e uma edicao neutra.
2. **Escolher para onde mandar o leitor e decisao editorial sua, nao minha.** Ha pelo menos tres
   lugares defensaveis e eles dizem coisas diferentes sobre o papel do apendice.

> **DECISAO SUA.** As opcoes, com o que cada uma implica:
>
> - **(a) Na preface do Cap. 5.** A preface e prosa de moldura, entao nao toca o corpo sob errata e
>   nao conflita com a regra standalone da rodada 14 (que vale para os corpos dos artigos, nao para
>   as prefaces). E o caminho de menor atrito e a minha sugestao se voce quiser resolver em uma linha.
> - **(b) No Cap. 2 (Fundamentacao), onde a representacao no nivel de check-in e definida.** Poe o
>   apendice ao lado da teoria que ele detalha, e o Cap. 2 ja aponta para `apx:cosine`, entao o padrao
>   existe. Custa uma frase em prosa de moldura, tambem sem tocar o corpo do Cap. 5.
> - **(c) No corpo do Cap. 5 (secao de metodo).** E onde um leitor mais provavelmente sente falta da
>   explicacao, mas exige entrada no `ERRATA.md` do artigo e conflita com a regra standalone que voce
>   acabou de estabelecer: o corpo do artigo passaria a apontar para um apendice da dissertacao,
>   exatamente o que a rodada 14 removeu. **Nao recomendo.**
>
> Diga (a), (b) ou (c) e eu aplico com o probe correspondente.

**Nota separada, cosmetica, sem acao pedida.** O arquivo chama-se `apx_h_check2hgi_joint_model.tex`
mas imprime como **Apendice E**, porque B, D e G foram para o volume suplementar e as letras impressas
agora correm A, B, C, D, E sobre os arquivos A, C, E, F, H. Nada depende do nome do arquivo e nenhuma
letra esta escrita a mao em lugar algum, entao e uma verruga de nomenclatura, nao um defeito. Renomear
tocaria `content.tex:398` e mais nada.

## §3 · Aberto e bloqueado em terceiros

| Item                                               | Bloqueado em                     | Estado                                                                                                                                                                                                                                        |
|----------------------------------------------------|----------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Dois membros da banca e a data da defesa           | Orientador / PPGCC               | Placeholders entre colchetes em `preamble.tex:217-219`. **Nao imprimem em nenhum dos tres builds** (`\folhadeaprovacao` esta comentada em `abntex2-UFV.sty:166-170`), entao nao ha nada inventado no PDF — nem os nomes reais quando chegarem |
| Folha de aprovacao assinada                        | A defesa                         | `make ppgc` gera o PDF com o placeholder; a versao assinada o substitui depois                                                                                                                                                                |
| Status do MobiWac                                  | — (fechado)                      | **Aceite a 2026-08-26.** A redacao do documento passou a "accepted for publication" na AUT-35 (decidida a 2026-09-01, commit `e1f9b8c0`). Esta linha dizia "submitted, under review... Nao mudar ate haver decisao" ate 2026-10-02 |
| `\finalbuildfirstpage` conferido contra o RASCUNHO | — (conferido)                    | Agora **20** (a definicao `\newcommand{\finalbuildfirstpage}` no `main.tex`): as paginas pre-textuais do sistema contam mas nao se numeram, e a primeira pagina de corpo do RASCUNHO emitido pelo portal imprime 20, verificado a 2026-09-06 (`CLAUDE.md` §1.2, bloco da numeracao do deposito). Tem portao proprio, `check_first_body_page.py`. Esta linha dizia **9** ate 2026-10-02; volta a conferir-se no proximo RASCUNHO |

---

## §4 · Pensamentos e considerações do Autor

> **AUDITADO EM 2026-08-03/04.** Os 37 pontos que voce escreveu aqui foram medidos um por um contra o
> fonte VIVO, nao contra o build que voce leu quando os escreveu. Cada um agora carrega ID estavel,
> estado da citacao, minha avaliacao, plano, sobreposicoes, disposicao e o commit da medicao.
>
> **A NUMERACAO DOS IDs NAO E A DOS ITENS, e isso foi sua decisao.** `AUT-01` ja existia
> (`CONSIDERATIONS.md`:668, a sua pergunta sobre otimalidade de Pareto, ainda aberta, defendida pelo
> probe `R9-schema`). Reusar `AUT-01` seria reciclar um ID, o que a regra deste arquivo proibe. Voce
> escolheu **continuar a serie**, entao **item N vira AUT- (N+1)**:
>
> | item | ID | item | ID | item | ID | item | ID |
> |---|---|---|---|---|---|---|---|
> | 1 | AUT-02 | 11 | AUT-12 | 21 | AUT-22 | 31 | AUT-32 |
> | 2 | AUT-03 | 12 | AUT-13 | 22 | AUT-23 | 32 | AUT-33 |
> | 3 | AUT-04 | 13 | AUT-14 | 23 | AUT-24 | 33 | AUT-34 |
> | 4 | AUT-05 | 14 | AUT-15 | 24 | AUT-25 | 34 | AUT-35 |
> | 5 | AUT-06 | 15 | AUT-16 | 25 | AUT-26 | 35 | AUT-36 |
> | 6 | AUT-07 | 16 | AUT-17 | 26 | AUT-27 | 36 | AUT-37 |
> | 7 | AUT-08 | 17 | AUT-18 | 27 | AUT-28 | 37 | AUT-38 |
> | 8 | AUT-09 | 18 | AUT-19 | 28 | AUT-29 | | |
> | 9 | AUT-10 | 19 | AUT-20 | 29 | AUT-30 | | |
> | 10 | AUT-11 | 20 | AUT-21 | 30 | AUT-31 | | |
>
> **O seu texto original nao foi apagado.** Esta byte por byte em
> [`_history/_round13/_aut_original.md`](_history/_round13/_aut_original.md) (sha256 `e2a44fea...`, 162 linhas, 37 itens),
> junto com o snapshot da arvore medida em `_history/_round13/_snapshot/` com `MANIFEST.tsv` por arquivo.
>
> **Passagem de citacoes obsoletas, contada:** 29 ancoras citaveis nos 37 itens.
> **12 EXATAS, 12 ALTERADAS, 5 DESAPARECIDAS.** Por item: 22 itens tem ancora citavel
> (**10 exatas, 10 alteradas, 2 desaparecidas**), 14 itens pedem um conceito ou uma secao e nao tem
> string para localizar, e o item 37 esta vazio no fonte. Recontado contra `c13fe4d2` depois que a
> outra esteira commitou: **zero deriva** nas 29 ancoras.
>

*Forense completa: [`_history/_round13/60_terminology_audit.md`](_history/_round13/60_terminology_audit.md),
[`61_check2hgi_audit.md`](_history/_round13/61_check2hgi_audit.md),
[`62_literature_audit.md`](_history/_round13/62_literature_audit.md),
[`63_conclusion_audit.md`](_history/_round13/63_conclusion_audit.md),
[`59_my_own_measurements.json`](_history/_round13/59_my_own_measurements.json).*

---

> **RODADA 13, SEGUNDA ONDA, 2026-08-04 — 9 DOS 11 ITENS RESTANTES FECHARAM.** As suas decisoes chegaram
> e foram aplicadas: AUT-02, 08, 09, 14, 29, 32, 35, 36, 37. Cada um esta arquivado com o commit em que
> foi aplicado em [`_history/_archive/PENDENCIAS_RESOLVIDOS.md`](_history/_archive/PENDENCIAS_RESOLVIDOS.md), secao
> "§4 (os itens `AUT-`) — A SEGUNDA ONDA", e os blocos completos ficam em
> [`_history/_round13/_aut_closed_blocks_wave2.md`](_history/_round13/_aut_closed_blocks_wave2.md).
>
> **Sobram os dois abaixo, e nenhum espera trabalho meu.** O AUT-26 foi fechado pelo autor a 2026-10-06 (nome MTVisitNet, texto inalterado). O AUT-38
> esta vazio no fonte e a sua decisao foi "NADA A FAZER"; o ID fica reservado, porque IDs deste arquivo
> nunca sao reciclados.

### AUT-26 — renomear o modelo conjunto para MTLChkNet, e se ja e tarde

> **FECHADO 2026-10-06 pelo autor (D8a do dossie).** O nome escolhido para a rede e **MTVisitNet**
> (Multi-Task Visit Network), para distinguir a rede do modelo de embeddings (Check2HGI). **O texto da
> dissertacao NAO muda**: continua "the joint model", como o artigo publicado. O nome fica para uso fora
> do texto depositado. O que se segue e o registo de quando estava aberto.

- **§4 item:** 25
- **Source status:** [N/A] como citacao (pergunta). `MTLChkNet` aparece **0** vezes na arvore.
- **Minha leitura e avaliacao:** Medi o raio de impacto antes de opinar, porque a resposta depende dele.
  `the joint model` tem **57** ocorrencias em prosa viva, e elas nao sao equivalentes entre si: **17 estao no Cap.5**,
  que e o manuscrito **submetido**; **5 estao dentro de tabelas de errata**, onde a string citada **e** a evidencia de
  uma correcao (mudar ali altera a citacao); **31 estao em prosa de moldura e no `content.tex`**, que sao livres; 2 na
  tabela de linhagem; 2 nos capitulos publicados. Somam 57. Ou seja: **nao e um search-and-replace**, sao tres regimes
  diferentes. Alem
  <!-- CONTAGEM RE-MEDIDA em 2026-08-04, e as anteriores ficam registradas para nao voltarem como
       historia. Este bloco ja disse 49 e depois 46; agora sao 57. As tres foram medidas em momentos
       diferentes e nenhuma delas era do documento como ele esta: a de 49 saiu de uma arvore com edicoes
       nao commitadas de outra esteira, a de 46 do commit c13fe4d2, e a de 57 e a de agora, depois das
       edicoes desta rodada, que acrescentaram ocorrencias no Cap.1 e no Cap.6. Comando, com comentarios
       removidos primeiro (AGENT_GUARDRAILS §4b V4 -- este arquivo cita as strings que voce procuraria):
         para cada src/**/*.tex fora de build/, remover o que vem depois de um % nao escapado,
         colapsar espacos, e contar 'the joint model'; somar por balde.
       A leitura NAO muda com o numero: continuam tres regimes (submetido, errata citada, prosa livre),
       e a soma dos baldes fecha com o total. -->

  disso `the joint model` esta **registrado** no GLOSSARY §2 como o nome canonico, com a nota de que o id de repositorio
  `mtlnet_crossattn_dualtower` nunca aparece no texto. Uma opiniao que eu devo dar mesmo sem voce pedir: um nome proprio
  novo compra pouco aqui, porque "the joint model" ja e contrastivo com "dedicated single-task model", que e o par que o
  documento usa em todo comparativo.
- **Plano de resolucao proposto:** Se voce quiser o nome: (A) so na moldura (Caps.1, 2, 6 + `content.tex`), deixando o
  Cap.5 como esta — barato, mas cria duas nomenclaturas no mesmo documento, o que e pior que nenhuma; (B) moldura +
  Cap.5, **sem** tocar as tabelas de errata, com nova linha no GLOSSARY §2 e paragrafo no Apendice B; (C) tambem no
  manuscrito do MobiWac, que e **edicao cross-boundary num artigo em revisao** e precisa da sua autorizacao explicita (o
  precedente e a correcao B.1 do CBIC, autorizada por voce e registrada na ERRATA do MobiWac); (D) nao renomear.
  **Recomendo (D)**, e se for renomear, (B) ou (C), nunca (A).
- **Sobreposicoes e dependencias:** AUT-03 (a mesma familia de arquivos de nome). O GLOSSARY §2 precisa de linha nova em
  qualquer opcao menos (D), e so voce pode adicionar.
- **Disposicao alvo:** **[I DECIDE]** — escolha de nome, com custo em manuscrito submetido e em registro.
- **Onde renderiza:** moldura p.13-16, p.83-87; Cap.5 p.64-80; tabelas de errata p.48
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

> DECISSAO: Deixar esse ponto aberto, vou perguntar para meu orientador.

---

## §4.1 · Decisões Pendentes do Autor

> **So os itens `[I DECIDE]` do §4 moram aqui: 21 dos 37.** Cada bloco acima carrega o diagnostico
> completo; este e o formulario de decisao, com opcoes, troca e esforco. Os 15 `[YOU APPLY]` nao
> estao aqui de proposito: eles nao esperam nada de voce. O `AUT-38` esta vazio no fonte.
>
> **Para responder:** escreva `> DECISSAO:` (ou `> DECISAO:`) embaixo do item. Eu leio como palavra
> final e nao reinterpreto.
>
> **Custo em horas e o meu, nao o seu.** "P" = menos de 30 min, "M" = 30 min a 2 h, "G" = mais de 2 h
> ou toca gate/manuscrito submetido.

### As tres que eu levaria primeiro

**1. AUT-03 · tres citacoes textuais estao danificadas, e uma e o titulo do seu artigo. [P]**
Uma varredura anterior tirou o hifen de `Multi-Task` **dentro** de citacoes textuais, em tres lugares:

| onde                                                                   | o documento imprime                                     | a fonte de registro diz                                                                 |
|------------------------------------------------------------------------|---------------------------------------------------------|-----------------------------------------------------------------------------------------|
| `3_cbic.tex`:17, preambulo do Cap.3 (p.33)                             | *An Investigation into **Multitask** Learning for...*   | **Multi-Task** — Crossref, DOI `10.21528/CBIC2025-1191324`, e `CBIC___MTL/main.tex`:31  |
| `5_mobiwac.tex`:29, preambulo do Cap.5 (p.64)                          | *A Check-in-Level **Multitask** Study on Mobility Data* | **Multi-Task** — `[mobiwac]/src/main.tex`:52, o manuscrito submetido (EDAS #1571313639) |
| `tables/cbic/errata_wording.tex`:24, coluna "Published wording" (p.48) | *investigating advanced **multitask** optimizers...*    | **multi-task** — `CBIC___MTL/sections/conclusion.tex`:17                                |

O primeiro e o urgente: **o mesmo PDF imprime dois titulos diferentes para um artigo so.** A p.33 diz
`Multitask` e a bibliografia, na p.88 referencia [1], diz `multi-task`, que e a forma correta. O terceiro e
auto-anulante: a coluna cuja funcao e mostrar o que o artigo publicou deixou de mostrar o que o artigo publicou. Isto
viola R2 (atributos copiados da fonte) e a ressalva do WRITING_LAW §1 sobre citacao textual.

- **(A) Restaurar o hifen nas tres.** Recomendada. 3 strings, 3 arquivos.
- **(B) Restaurar so no titulo do CBIC** (o que sai em dois lugares do mesmo PDF).
- **(C) Nao mexer.** Nao recomendo: sao atributos de registro, nao prosa da casa.
- E, independente disso: registrar a normalizacao da **prosa reproduzida** no Apendice B, seguindo o paragrafo
  `MTLNet`->`MTLnet` que ja esta la como precedente. [P]

> DECISSAO: A.

**2. AUT-20 · "trained without category or region labels" nao e verdade como esta escrito. [M]**
Verificado no spec e no codigo: ha um termo de **reconstrucao de categoria de POI mascarado** com peso **0.3** de cinco
termos no objetivo do Check2HGI, e um termo L2 de categoria no POI2Vec a montante (peso `1e-8`, que o proprio comentario
do codigo chama de *"the only explicit category-label path"*). O que **e** verdade e mais estreito e ainda suficiente:
nenhum objetivo de representacao le a categoria ou a regiao de uma visita **futura**.

- **(A) Trocar a afirmacao de ausencia por uma de escopo.** Recomendada: diz o que protege (o alvo futuro) e admite o
  que usa (a categoria observada da visita atual).
- **(B) Manter e acrescentar uma nota de rodape** com os dois termos. Mais barato, menos honesto: a frase principal
  continua prometendo mais do que entrega.
- **(C) Manter.** Nao recomendo. E a classe de defeito que o WRITING_LAW §3 chama de bug, nao de estilo.
- **Atencao:** resolva junto com o **AUT-08**, que quer afirmar o **oposto** (que o vazamento da categoria atual e
  desejavel). Os dois no mesmo capitulo, decididos em separado, se contradizem.

> DECISSAO: A. Read the: articles/dissertacao/science/check2hgi_v17_complete_picture.md if you need more context, but we
> use the category and the region (lat and long) on the graph node.

**3. AUT-14 · o Capitulo 4 nao aparece nenhuma vez nas Contribuicoes. [M, com uma parte P]**
Medido: zero referencias a `ch:courb` na secao, contra duas ao Cap.3 e duas ao Cap.5 — embora o diagnostico de que a
representacao e o gargalo seja a dobradica do arco e o bullet Teorico afirme exatamente esse achado. O `ST-MTLNet`,
artefato registrado, esta fora do bullet Software.

- **(A) Destacar a parte mecanica agora** (acrescentar Cap.4 e ST-MTLNet) e decidir o resto depois. Recomendada: e a
  unica parte sem juizo de conteudo. [P]
- **(B) Reescrever a secao inteira de uma vez**, com os seus quatro candidatos resolvidos. [M/G]
- Sobre os seus quatro candidatos: (a) sustentavel e hoje sub-declarado; (b) so como afirmacao de projeto, nunca como
  previsao; (c) o seu proprio aviso esta certo, veja o **AUT-28** e o **GER-11**; (d) **"pioneiros" e refutavel como
  escrito** — a forma estreita que o texto ja tem ("Among the works reviewed here, none treats next category and next
  region as co-equal end targets of one joint model")
  e o teto, e **nunca** "pioneering"/"the first" no Cap.1. Uma varredura de refutacao com treze buscas encontrou dez
  trabalhos vizinhos e nenhum que refute a forma estreita.

> DECISSAO: Vamos seguir com o B. Nessa sessão de contribuições temos que colocar o que é contribuição real do ponto de
> vista de todo o trablaho, e o Cap. 4,
> apesar de ter seido uma ótima base téorica, como citada na introdução, ele não posui contribuições praticas para
> literatura, a não ser os aprendizados que já foram consumidos nos artigos em sequencias.

### As decisoes de afirmacao cientifica

**4. AUT-28 · afirmar a propriedade de Pareto do Cap.5. [P na prosa, mas toca 4 probes]**
Aplicando a definicao que o proprio documento registra, com os numeros citados da fonte de registro:
dominancia vale em **Istambul, FL, TX, CA** e esta **bloqueada em AL e AZ**, onde regiao e apenas nao-inferior por TOST.
O whitelist do MobiWac proibe "Pareto-dominates everywhere" nominalmente.

- **(A) Duas frases no Cap.6, sem a palavra "Pareto".** Recomendada.
- **(B) Nomear o conceito explicitamente.** Admissivel, mas o Apendice F e o lugar **errado** (ele mede cosseno de
  gradiente, nao desfecho de tarefa); o lugar e o Cap.6.
- **(C) Nao afirmar nada.** Custo zero, e o documento continua coerente.
- **Se (A) ou (B):** a frase "claims no Pareto property" do §2.3 fica falsa como escrita e precisa ser estreitada para
  **otimalidade**. Quatro probes a guardam (`R9-pareto`, `R9-pareto2`, `R9-pareto3`,
  `R9-conflict`), e o probe tem de ser reapontado no **mesmo commit** da edicao.

> DECISSAO: Opção C.

**5. AUT-08 · por que o par de tarefas mudou. [P na perna 1; M na perna 2]**
A perna comparativa ("na literatura essas duas tarefas tem mais forca") **nao tem ancora aberta que a sustente**, e isso
fecha em negativo a bandeira `[VERIFY]` que o `NORTH_STAR` §6 Cap.1 beat 4 (b) deixou exatamente para esta frase.

- **(A) Usar a fallback ja sancionada** no proprio `NORTH_STAR`: *"both are established end targets, and next region
  feeds a broader family of downstream problems"*. Recomendada, custo minimo.
- **(B) Usar o eixo que a literatura sustenta caso por caso:** nesses trabalhos a categoria costuma ser tarefa
  **auxiliar** de um objetivo de proximo lugar, nao alvo final.
- **(C) Acrescentar tambem o argumento do vazamento** (a sua segunda metade). Afirmacao nova (C2), entra como projeto e
  nunca como resultado, e obriga a reescrever `apx_b_static_scope.tex`:83-85, que hoje aponta na direcao contraria.
  Decida junto com o **AUT-20**.

> DECISSAO: Opção A.

**6. AUT-35 · as tres limitacoes. [(a) M e toca gate; (b) M; (c) G]**

- **(a) vintage: a sua premissa esta errada.** A limitacao ja e escopada ao Gowalla e nao fala de Istambul; e o
  Massive-STEPS **nao e dado de 2025** (2025 e publicacao, ainda preprint; os check-ins de Istambul sao de
  **2017-2018**). Opcoes: manter; ou acrescentar uma frase com a janela de Istambul, o que introduz **numero novo**
  (linha de ledger + comentario de claim) e exige manter a string
  "August 2011" literal, porque o probe `R8-vintage` a exige.
- **(b) transdutividade:** o acrescimo e afirmacao sobre trabalho de terceiros e precisa de citacao localizada **antes**
  da frase. Nao pode ser generalidade nua.
- **(c) o confound do par de tarefas: o seu raciocinio se sustenta e NAO apaga a limitacao.** Se a ablacao que
  resolveria o confound vazaria, entao o confound nao e resolvivel de forma limpa, o que e uma limitacao **mais** forte.
  O que a sua objecao invalida e o **item de trabalho futuro** amarrado a ela. Quatro saidas: manter; **manter e
  acrescentar por que a ablacao nao e limpa** (recomendada, marcada como inferencia e nao medicao); enfraquecer;
  remover — e remover precisa de **novo aval**, porque a limitacao tem aval registrado de 2026-07-22.

> DECISSAO:Vamos aplica o A,B e commentar a limitação 6, com as alterações do C. Ainda sobre o ponto A, tem um detalhe
> que voce não pegou e eu tmb não citei, mas o masive step é o conjunto mais moderno que temos na literatura publica,
> pode
> validar.

### As decisoes estruturais

**7. AUT-29 · reordenar §2.3.2 e §2.3.3. [M/G]** Concordo com o sintoma. Mas a ordem que voce propoe move o §2.3.2.2
para **antes do seu proprio pai** e o divide em dois, o que e **re-hierarquizacao**, nao reordenacao. Saida coerente:
promover "Gradient conflict" a subsecao irma e coloca-la antes. **Decida junto com GER-09 e GER-10**, que pedem a mesma
reestruturacao e estao abertos.

> DECISSAO: Eu concordo com essa sugestão, mas ainda assim teremos que mudar o inicio do 2.3.2, porque hoje o texto
> atual, já começa direto na formalização antes da problematica.

**8. AUT-31 · reorganizar §2.4 com "Preparation and data split". [M]** Concordo; a estrutura proposta e mais coerente
que a atual, e o material a promover ja esta dentro do §2.4.3. Cuidado: o
`\label{sec:fund:eval}` e citado de fora do capitulo e deve continuar apontando para onde as outras referencias esperam.

> DECISSAO: OK

**9. AUT-18 · as sete categorias numa definicao tecnica. [P]** Concordo com a primeira metade (a cardinalidade e
propriedade do dado) e discordo da segunda (setor censitario e mahalle sao o que torna
"regiao" concreto). **Decida numa unica passada com FAB-14 e FAB-15**, que sao a mesma decisao no Cap.1.

> DECISSAO: Sobre o ponto que voce discorda, a questão e que esses não devem ser citados em todo momento do texto, eles
> devem ser citados com setories adimistrativos ou um nome generico que caiba para ambos e que caiba para qualquer outro
> datasetr no futuro, o ponto da minha critica é a especificidade, não precismoas dizer que é o seto censitario dos USA
> ou e mahalle que é o orgão de istambul, conseguiimos se refeir a eles de forma generica. E ser especifico na descrição
> do dataset. Outra questão e que sim os artigos não são generalistas é isso e um problema, não devemos tratar e nem
> apontar.

**10. AUT-37 · a conclusao e o fluxo de §6.2. [M]** O seu diagnostico se sustenta: 53 numerais em §6.2 e a manchete
restabelecida mais de uma vez. O fluxo que voce quer e uma **reordenacao de quatro movimentos**, e o movimento que falta
("o que erramos na tese inicial") tem material pronto: e o que os controles descartaram (AUT-33). **A mesma edicao serve
ao AUT-34.**

> DECISSAO: OK, tome cuidado na re-escrita, para usar agents que escrevam de forma natural, se preciso for use o codex
> com o gpt-sol.

**11. AUT-34 · menos numeros em §6.1. [P]** A proporcao que voce assume **ja vale** (21 numerais em §6.1 contra 53 em
§6.2). Dos sete numerais arabes de §6.1, so um e resultado que §6.2 repete; os outros sao convencao de protocolo, que
nao sai sozinha da frase.

> DECISSAO: Então vamos deixar em como está.

**12. AUT-36 · os sete itens de trabalho futuro. [M/G]** Cada item precisa de uma limitacao amarrada 1:1, entao
acrescentar mexe na contagem de limitacoes. O seu item mais promissor (cabeca de proximo lugar) e legitimo e ja esta na
lista do `NORTH_STAR`, mas a redacao nao pode soar como algo que a dissertacao fez: dois probes guardam essa exclusao de
escopo.

> DECISSAO: Sobre o proximo lugar podemos adicionar ele no trabalho futuro relacionado ao uso do check2hgi para outros
> contextos. Esse eu faço questão de estar de alguma froma. Quanto ao resto adicione os que voê analisou e cabem estar
> lá.

### As menores, agrupadas

**13. AUT-02 · especificidades no Resumo. [P]** Metade ja foi feita: o Resumo vivo ja diz "seis conjuntos de dados...
incluindo um conjunto nao estadunidense". Sobra decidir sobre a margem de dois pontos, que e a convencao que liga o
verbo ao teste. Mesmo argumento do FAB-22.

> DECISSAO: A.

**14. AUT-09 · a frase do arco. [P]** Concordo que a atual e pior. Mas a anterior traz "correction trail", e o
`NORTH_STAR` tem guarda explicita (F4) contra fazer o resultado nulo parecer ato um de um roteiro. A saida e combinar as
duas, nao restaurar a antiga.

> DECISSAO: Vamos combinar as duas cuidado com a reescrita não soar natural.

**15. AUT-11 · alargar o objetivo 1. [P]** Discordo: acrescenta um segundo objetivo a um item que declara um so, e o
`NORTH_STAR` fixa objetivos 1:1 com capitulos. A construcao do MTLnet ja e reivindicada nas Contribuicoes. Recomendo
manter.

> DECISSAO: A.

**16. AUT-12 · o objetivo 4 aponta para o Cap.6. [P]** Defeito real e invisivel aos gates: o `\ref`
resolve, entao 0 referencias indefinidas, e o PDF imprime "(Chapter 6)" para "the protocol used in the final study".
Duas leituras, duas edicoes: **(A)** `ch:conclusion`->`ch:mobiwac`, um token (recomendada); **(B)** manter a referencia
e trocar a redacao, se a intencao era a consolidacao na Conclusao.

> DECISSAO: A.

**17. AUT-21 · citar o POI2Vec. [P/M]** Ele **esta** no pipeline (inicializacao + ancora L2). Mas o que o nosso codigo
implementa **nao e** o metodo do POI2Vec publicado (Feng et al., AAAI 2017), e cita-lo seria **misatribuicao** — a mesma
classe do erro do POI-RGNN que ja e errata deste projeto. Recomendada: nomear o mecanismo sem citar nada novo.

> DECISSAO: Vamos de i) Nomear o mecanimos citado e nada novo.

**18. AUT-23 · §2.2.3.2 contra o spec. [M]** Tres afirmacoes nao conferem, e sao o mesmo excesso do AUT-20 com outras
cabecas (a equacao mostrada e o nucleo hierarquico, nao a perda de cinco termos). **Resolva numa unica passada com
AUT-20 e AUT-21**, ou o capitulo se contradiz.

> DECISSAO: Beleza vamos resolver em uma unica passada, mas depois dessa apssada averigue se está tudo certo.

**19. AUT-25 · as duas entradas e a "correlacao". [P/M]** A sua analise tecnica confere nos dois pontos que dependiam da
codebase. O terceiro (correlacao) e defensavel como **fato de construcao** (copia com stop-gradient da mesma origem),
nao como quantidade: afirmar correlacao pediria um numero que ninguem mediu. Decida entre hedge e medicao.

> DECISSAO: hedge, deixar no left_out.md a medeição.

**20. AUT-26 · renomear para MTLChkNet. [G]** Raio re-medido em 2026-08-04: das **57** ocorrencias de "the joint model",
**17** estao no Cap.5 **submetido**, 5 dentro de tabelas de **errata** (onde a string citada e a evidencia) e **31** em
prosa livre, mais 2 na tabela de linhagem e 2 nos capitulos publicados. Nao e search-and-replace. **Recomendo nao
renomear**; se renomear, moldura **e** Cap.5 juntos, nunca so a moldura, e mexer no manuscrito precisa da sua
autorizacao explicita.
<!-- Este item dizia 49/15/22, a mesma contagem retratada que o bloco AUT-26 do §4 carregava. As duas
     estavam desalinhadas depois de eu corrigir so um dos dois lugares, o que deixava o arquivo afirmando
     duas contagens diferentes da mesma medicao. Agora as duas dizem 57/17/31 e as duas registram as
     figuras anteriores. O item continua ABERTO: a sua decisao foi consultar o orientador. -->


> DECISSAO: Deixar esse ponto aberto, vou perguntar para meu orientador.

**21. AUT-32 · a abertura do Cap.6 e a tarefa estatica. [P]** A omissao e coerente com a pergunta de pesquisa em tres
lugares aprovados. **(A)** manter; **(B)** uma oracao no Cap.6 dizendo que os dois primeiros estudos incluiam a tarefa
estatica, sem mexer na pergunta (recomendada).

> DECISSAO: B.
---

## §4.2 · Plano de execucao dos `[YOU APPLY]`

> **15 itens, ordenados. Nada aqui foi aplicado:** esta fase e auditoria, e nenhum `.tex` foi tocado
> (verificado: `git diff --name-only HEAD -- 'articles/dissertacao/src/**/*.tex'` volta vazio).
>
> **Regra de ouro para a Onda 1:** cinco destes itens sao "fechar como ja satisfeito", ou seja, **nao ha
> edicao**, so registro com a citacao que prova. Eles nao podem quebrar nada, e devem sair primeiro para
> tirar ruido da fila.

### Onda 1 — fechar sem editar (independentes, paralelizaveis, risco nulo)

| item       | o que fazer                                                                                                         | onde renderiza               | evidencia                                                                      |
|------------|---------------------------------------------------------------------------------------------------------------------|------------------------------|--------------------------------------------------------------------------------|
| **AUT-13** | fechar: "the joint setting" ja virou "The joint model operates under..."                                            | §1.4 p.15                    | `1_introduction.tex`:222-223                                                   |
| **AUT-15** | fechar: a frase viva ja carrega a clausula de escopo "at a coarse spatial resolution"                               | §2.1 p.18                    | `2_fundamentals.tex`, §2.1                                                     |
| **AUT-17** | fechar: as definicoes de `x_i` e `H_i` existem e ligam os cinco simbolos                                            | §2.1.1.1 p.18                | Definitions "Check-in" e "Check-in history"; probes `R12-s1bind`, `R12-s2type` |
| **AUT-33** | fechar: o Cap.6 ja faz a distincao entre sinal de treino e arquitetura; varredura com zero defeitos                 | §6.2 p.84                    | `6_conclusion.tex`, "does not require training transfer"                       |
| **AUT-22** | **nao executar aqui:** e o mesmo defeito do **GER-06**, que ja esta aprovado. Executar via GER-06 para nao duplicar | §2.2.3.1 p.23 -> §2.3.1 p.25 | GER-06 em `CONSIDERATIONS.md`                                                  |

### Onda 2 — edicoes de uma frase ou um token (independentes entre si)

| ordem | item       | a edicao                                                                                 | onde renderiza                          | cuidado                                                                                                                |
|-------|------------|------------------------------------------------------------------------------------------|-----------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| 1     | **AUT-07** | `static place categories` -> `category classification` (nome canonico registrado)        | §1.2 p.13-14                            | varrer o resto da arvore pelo mesmo padrao antes de fechar: uma ocorrencia so e o caso que a amostragem perde          |
| 2     | **AUT-27** | glosar `\mathcal{L}_k` como a perda da tarefa `k` (meia oracao)                          | §2.3.2 p.26                             | so a glosa; a reorganizacao e o AUT-29, que e `[I DECIDE]`                                                             |
| 3     | **AUT-30** | expandir `OOD` no primeiro uso + reescrever a frase de equivalencia                      | §2.4.2.2 p.29                           | corrigir tambem o comentario de `content.tex`:262-264, que afirma que OOD "never appears in prose" e hoje isso e falso |
| 4     | **AUT-04** | religar a frase das categorias semanticas ao que vem depois                              | §1.1 p.13                               | fazer junto com o 5: e um paragrafo so                                                                                 |
| 5     | **AUT-05** | cortar as duas frases de "neighboring geospatial tasks" (o conteudo ja esta em §2.2.3.1) | §1.1 p.13                               | fazer junto com o 4                                                                                                    |
| 6     | **AUT-06** | nomear as duas tarefas em vez de "both tasks"                                            | §1.1 p.13                               | usar os nomes canonicos, nao o rascunho do item                                                                        |
| 7     | **AUT-10** | glosar `hard parameter sharing` no primeiro uso do Cap.1                                 | §1.2 p.13-14 (`1_introduction.tex`:131) | a definicao formal fica no Cap.2; nao duplicar                                                                         |
| 8     | **AUT-16** | glosar "sequential" / "static" no primeiro uso do Cap.1                                  | §1.1 p.13                               | o Cap.2 ja resolve; o defeito e so no Cap.1                                                                            |
| 9     | **AUT-19** | uma frase de entrada em §2.2.2 dizendo o que infomax **e**                               | §2.2.2 p.21                             | os termos ja estao no GLOSSARY §3; sem bloqueio fail-closed                                                            |
| 10    | **AUT-24** | reescrever a transicao de abertura de §2.2.4 (nomear o sujeito)                          | §2.2.4 p.24                             | o fechamento da mesma subsecao e o AUT-25, que e `[I DECIDE]`                                                          |

### Sequenciamento e conflitos

- **Os itens 4, 5 e 6 tocam o mesmo paragrafo** (§1.1, `1_introduction.tex`). Aplicar em uma unica passada, nao em tres,
  ou o terceiro reescreve o contexto dos dois primeiros.
- **Os itens 1, 7 e 8 tocam a mesma regiao do Cap.1** (§1.1-§1.2). Sequenciais, nao paralelos.
- **AUT-24 e AUT-25 sao a abertura e o fechamento de §2.2.4.** O AUT-24 e `[YOU APPLY]` e o AUT-25 e
  `[I DECIDE]`; se voce decidir o AUT-25, faca os dois juntos, senao a subsecao fica com metade nova.
- **AUT-19 e AUT-20 estao na mesma subsecao** (§2.2.2), e o AUT-20 e a **primeira frase do corpo**. Aplicar o AUT-19
  antes de decidir o AUT-20 e seguro; o contrario tambem, mas nao simultaneamente.
- **Nenhum item da Onda 1 ou 2 casa com a string de nenhum probe.** Medido: das 29 ancoras, so as dos AUT-08 e AUT-09
  tem probe a menos de 600 caracteres (`R10-fab22`, que exige a presenca de "Istanbul as a non-United-States dataset"),
  e **os dois sao `[I DECIDE]`**, entao a Onda 2 nao chega perto de um gate.
- **Depois de cada onda:** `cd articles/dissertacao/src && make check` e `make defense`, lendo o codigo de saida de cada
  um por gate, nunca um veredito unico (§4b V11/V12). As paginas citadas acima sao do
  `build/main.pdf` de 105 paginas com mtime 2026-08-03 21:21:31; elas **andam** se a outra esteira soltar prosa, e por
  isso cada linha registra o build contra o qual foi medida.

### O que esta fora deste plano, e por que

- Os **21 `[I DECIDE]`** do §4.1: esperam a sua palavra.
- **AUT-38**: vazio no fonte.
- As quatro tarefas de infraestrutura que o AUT-03 abriu e que **nao** sao edicao de prosa: registrar a normalizacao no
  Apendice B, registrar a regra de hifen de POI no GLOSSARY (linha sua), implementar o probe `R9-poihyphen` reservado
  desde o FAB-20, e reparar o `[VERIFY]` de descricao obsoleta do probe
  `R8-vintage` (o probe passa, a descricao dele deixou de descrever o texto que ele guarda).
