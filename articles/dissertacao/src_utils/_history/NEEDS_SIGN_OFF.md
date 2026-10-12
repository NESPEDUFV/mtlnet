# NEEDS_SIGN_OFF.md

**Gerado em 2026-08-02, a partir de uma varredura mecanica dos 56 marcadores `[NEEDS SIGN-OFF]` vivos no fonte (
`grep -rc '\[NEEDS SIGN-OFF' src --include='*.tex' --exclude-dir=build`, 56 marcadores em 23 arquivos). Cada item abaixo
traduz o comentario de proveniencia original (em ingles, no `.tex`) para PT-BR, preservando todo numero, ID de revisao (
COD-, NUM-, REV-, FAB-) e nome de arquivo tal como aparecem na fonte.**

**Como usar.** Cada item tem um espaco `> **SUA DECISAO:**` vazio, no mesmo padrao usado no `PENDENCIAS.md`. Preencha
ali a sua resposta; quando um item estiver resolvido, ele sai deste arquivo e vai para o `PENDENCIAS.md` (ou direto para
`_history/_archive/PENDENCIAS_RESOLVIDOS.md`, se a resolucao for mecanica). Este arquivo **nao substitui** o `PENDENCIAS.md` —
ele e um mapa de tudo que ainda pede a sua palavra especificamente por estar marcado no fonte, o que o `PENDENCIAS.md`
nao lista item por item.

**Total: ~~56~~ → 53 marcadores vivos (re-medido em 2026-08-04, rodada 14).** O total caiu de 56 para 53 porque o
refactor de §6.2 (commit `a47691f8`, "§6.2 reordered into four movements") resolveu tres marcadores do
`6_conclusion.tex` ao reescrever os paragrafos que eles anotavam: aquele arquivo tinha 8 marcadores e hoje tem 5.
**Nenhum marcador foi perdido; tres foram resolvidos por reescrita.**
Reproduza a contagem com:

```bash
cd articles/dissertacao/src
grep -rho "\[NEEDS SIGN-OFF" --include="*.tex" . --exclude-dir=build | wc -l   # 53
```

Distribuicao atual: `content.tex` 4, `1_introduction` 2, `2_fundamentals` 8, `3_cbic/method` 1,
`3_cbic/results` 2, `4_courb.tex` 1, `4_courb/methodology` 1, `4_courb/results` 1, `5_mobiwac.tex` 1,
`5_mobiwac/02_related` 2, `5_mobiwac/05_setup` 1, `5_mobiwac/06_results` 3, `5_mobiwac/07_discussion` 2,
`6_conclusion` 5, `apx_a_contributions` 3, `apx_b_errata` 5, `apx_b_static_scope` 1,
`apx_c_ai_disclosure` 1, `apx_d_ceiling` 1, `apx_e_ethics` 1, `apx_extra_human_subjects` 1,
`apx_extra_platform` 4, `main_extra.tex` 2.

**Estado da auditoria (rodada 14, 2026-08-04): 1 MECANICO (pode fechar), 1 VAZIO (premissa deixou de existir), 1
PARCIAL, 44 PRECISA DE VOCE, 6 AMBIGUO.** Cada item abaixo carrega essa etiqueta no proprio titulo. **Leia primeiro a
`## Auditoria da rodada 14` logo abaixo** — ela responde a pergunta que motivou esta releitura (quanto comentario pode
sair, e o que quebra se sair) e corrige dois itens cuja base factual mudou.

---

## Auditoria da rodada 14 (2026-08-04) — o objetivo declarado: tirar comentario do `.tex`

> **VOCE DISSE:** *"A final take my aim with the need sign off is also to remove the colossal amount of
> comments that we have in the tex."* Esta secao existe para tornar essa decisao possivel. Nenhuma
> alteracao foi feita no texto nem nos comentarios nesta rodada — voce pediu explicitamente
> *"please don't do any change in the text"*, e nada foi mudado.

### 14.1 O tamanho real do problema, medido

| Classe de linha de comentario                                        | Linhas | % dos comentarios |
|----------------------------------------------------------------------|-------:|------------------:|
| Outros (proveniencia em prosa, justificativas, historico de rodada)  |  3.267 |               61% |
| Dentro de um bloco `[NEEDS SIGN-OFF]`                                |  1.491 |               27% |
| Relatorio de rodada com ID (`[round..]`, `COD-`, `AUT-`, `MEASURED`) |    403 |                7% |
| Divisores estruturais (`% ====`, `% ----`)                           |    131 |                2% |
| **Funcionais (`% !TeX root`) — NAO PODEM SAIR**                      | **60** |            **1%** |

**52% da arvore `.tex` e linha de comentario: 5.352 de 10.237 linhas.** Os 53 marcadores deste arquivo respondem por
1.491 dessas linhas, ou seja **28% de todo o comentario esta preso nos blocos de sign-off**
— fechar os itens deste arquivo e, de longe, a maior alavanca isolada que voce tem. Reproduza:

```bash
cd articles/dissertacao/src
tot=$(find . -name "*.tex" -not -path "./build/*" -exec cat {} \; | wc -l)
cm=$(find . -name "*.tex" -not -path "./build/*" -exec grep -h "^[[:space:]]*%" {} \; | wc -l)
echo "$cm de $tot linhas sao comentario"
```

Os arquivos mais carregados, para priorizar: `2_fundamentals.tex` 1.115 linhas de comentario (59% do arquivo),
`apx_f_cosine.tex` 558 (77%), `apx_b_errata.tex` 301 (57%), `6_conclusion.tex` 286 (52%),
`1_introduction.tex` 253 (52%), `content.tex` 230 (55%).

### 14.2 A pergunta que travava a decisao: **de 14 gates, exatamente 1 depende de comentario do `.tex`**

Havia um medo razoavel de que apagar comentario derrubasse a suite de gates, porque 13 dos 14 scripts
`check_*.py` mencionam comentarios no codigo. **Medido: dos 14, exatamente UM quebra — o
`check_comment_hygiene`, que depende de ~10 linhas de comentario do `src/main.tex`. Os 208 probes do
`check_audit_claims` sao imunes, e os outros 12 gates passam.** Atencao a distincao que gastei duas correcoes para
acertar: **6 gates leem o `.tex` ja sem comentario e 8 leem cru, mas "ler cru" nao e
"depender de comentario"** — 7 dos 8 passam mesmo assim. A tabela em (a) mostra qual e qual, e por que cada um
sobrevive. Os detalhes e a decisao que isso pede estao na caixa de correcao ao final desta secao; leia-a antes de apagar
qualquer bloco. Duas evidencias independentes, na ordem em que as levantei:

**(a) Direto na fonte do instrumento.** `check_audit_claims.py` le todo `.tex` atraves de `live_text()`, cuja primeira
linha de docstring e literalmente *"Source with comments removed"*. O gate **nao consegue**
ver um comentario `.tex`, por construcao. Um probe cujo texto-alvo esteja dentro de `%` e inerte hoje — isso ja esta
documentado no proprio arquivo, na entrada `R13-aut30b`, marcada *"UNPROBEABLE BY CONSTRUCTION"*. **Isto vale para os
208 probes e nao foi retratado.** O que nao se segue e generalizar de `check_audit_claims` para a suite inteira.

> **CORRECAO 2 (achado do revisor, 2026-08-04).** Uma versao anterior deste paragrafo afirmava, em
> negrito e dizendo-se "conferido script por script", que **"13 dos 14 gates nao usam
> `live_text()`/`strip_text()` e leem o `.tex` cru"**. **Isso esta errado, e a minha propria medicao ja
> mostrava o contrario:** 6 gates *usam* helper de strip, 8 leem cru. Eu tinha o numero certo na tela e
> escrevi outro; pior, ele contradizia a direcao do proprio titulo desta secao. Medido de novo,
> ignorando mencoes dentro de comentarios do codigo e exigindo a *chamada* do helper:

| Leem o `.tex` **sem** comentario (6)                                                                                                        | Leem o `.tex` **cru**, com comentario visivel (8)                                                                                                                                  |
|---------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `check_audit_claims`, `check_doubled_macro`, `check_extra_xrefs`, `check_negative_parallelism`, `check_process_narration`, `check_register` | `check_comment_hygiene`, `check_meta_claims`, `check_tex_root`, `check_torn_sentences`, `check_tracker_refs`, `check_trapped_prose`, `check_verify_list`, `check_wordcount_claims` |

```bash
cd articles/dissertacao/src_utils && python3 -c "
import pathlib,re
for p in sorted(pathlib.Path('.').glob('check_*.py')):
    code='\n'.join(l for l in p.read_text().splitlines() if not l.lstrip().startswith('#'))
    print('STRIP' if re.search(r'\b(live_text|strip_text|strip_comments)\s*\(',code) else 'RAW  ', p.name)
"
```

**E aqui esta o ponto que importa para a sua decisao: ler cru NAO e o mesmo que DEPENDER de comentario.**
Dos 8 que leem cru, 7 sobrevivem a um strip, cada um por um motivo diferente e verificavel:

- `check_trapped_prose` — os comentarios sao o **suspeito** que ele caca (prosa presa dentro de `%`). Sem comentario
  nenhum, ele nao tem o que acusar: passa trivialmente.
- `check_torn_sentences` — **pula** linhas de comentario explicitamente (`if not s or s.startswith("%")`).
- `check_tex_root` — precisa da diretiva `% !TeX root`, que **e** um comentario, mas o strip do
  `sync_src_clean.py` preserva diretivas de proposito. Por isso passa no `src_clean`.
- `check_meta_claims`, `check_tracker_refs`, `check_verify_list`, `check_wordcount_claims` — o alvo deles esta em
  documentos `.md` e no PDF, nao em comentario de `.tex`.

**Sobra exatamente um: `check_comment_hygiene`** — zero helpers de strip, quatro `read_text()`, e ele **precisa** ler
cru porque o assunto dele sao os proprios comentarios. Esse e o unico que quebra, e a caixa abaixo diz por que e o que
fazer.

**(b) Empiricamente, rodando a suite inteira contra uma arvore sem comentario.** O `src_clean` ja e um espelho 1:1 sem
comentarios, entao a experiencia esta pronta: copiei os gates para um diretorio cujo
`../../src` e o `src_clean` e rodei os 14. Resultado: **12 passam, 2 falham.** Dos 208 probes do
`check_audit_claims`, 34 deixaram de valer, e **nenhum desses 34 aponta para um `.tex`**: 8 leem
`fundamentals/DEFINITIONS.md`, 7 `_history/_round12/50_...md`, 6 `CONSIDERATIONS.md`, 4 `_history/_round12/53_...md`, 3+3 outros
`_history/_round12/*.md`, 2 `LEFT_OUT.md`, 1 `WORDCOUNT_CONVENTION.md` — documentos de `src_utils/` que o diretorio de teste nao
tinha. Essa falha era, de fato, artefato do teste.

> ### CORRECAO (achado do revisor, 2026-08-04) — a segunda falha NAO era artefato do teste
>
> **Uma versao anterior desta secao dizia que "as duas falhas nao tem relacao com comentario" e citava
> `scope floor breached, 9 file(s) examined, floor is 12` como motivo das duas. Isso estava errado.**
> Aquela mensagem veio da rodada ANTES de eu copiar os arquivos `src_utils/` que faltavam; depois de
> copia-los a contagem continuou `passing=12 failing=2`, com o `check_comment_hygiene` ainda entre as
> falhas, e eu nao apurei o motivo real antes de escrever a conclusao. Apurado agora:
>
> ```
> scope: 14 files examined; 0 skipped        <- o scope floor esta OK, nao e mais isso
> 2 finding(s):
>   story 'three-builds-one-source': NOBODY tells it, including its canonical home src/main.tex
>   story 'nested-if-scanning-hazard': NOBODY tells it, including its canonical home src/main.tex
> ```
>
> **Este e exatamente o contra-exemplo que a manchete precisava excluir, e ele existe.** O
> `check_comment_hygiene.py` exige que **tres explicacoes** estejam contadas em algum lugar da arvore
> (lista `STORIES`, linhas 130-163), e **duas delas moram em comentarios do `src/main.tex`**:
>
> | Story | Onde e contada | Sobrevive a um strip? |
> |---|---|---|
> | `three-builds-one-source` | comentario em `src/main.tex` | **NAO** |
> | `nested-if-scanning-hazard` | comentario em `src/main.tex` | **NAO** |
> | `halt-on-error-vs-nonstopmode` | `src_utils/README_SRC.md` (markdown) | sim |
>
> Na arvore real o gate passa (`rc=0`, 14 arquivos, 0 findings); na arvore sem comentario ele falha
> (`rc=1`) porque as duas explicacoes de `main.tex` desapareceram junto com os comentarios. O proprio
> gate explica por que isso importa: *"a story with zero tellers passes vacuously and must never be
> reported as clean"*.
>
> **EXPERIMENTO CONTROLADO, para nao repetir o erro de atribuicao.** Meu primeiro teste rodava num
> diretorio a que faltavam documentos `src_utils/`, e por isso duas falhas se confundiam: uma real e uma
> artefato. Refeito com **todos** os documentos `src_utils/` e `fundamentals/` presentes, de modo que a
> **unica** diferenca em relacao ao repo real e que os `.tex` nao tem comentario:
>
> | Gate | Resultado | Leitura |
> |---|---|---|
> | `check_audit_claims` | **PASS**, `0 claim(s) not applied` | os 208 probes sao imunes a remocao de comentario; a falha anterior era artefato do diretorio de teste |
> | `check_comment_hygiene` | **FAIL** | falha real, causada pela remocao de comentario |
> | os outros 12 | PASS | — |
>
> Ou seja: **exatamente 1 dos 14 gates depende de comentario do `.tex`**, e o isolamento acima e o que
> autoriza dizer "1", em vez de inferir a partir de um teste com variavel confundida.

> **CONSEQUENCIA PRATICA, corrigida.** Remover comentario do `.tex` **nao quebra nenhum dos 208 probes
> do `check_audit_claims`** — essa parte se sustenta, e e a maior parte da suite. Mas **quebra um gate**,
> o `check_comment_hygiene`, e por um motivo legitimo: ele existe para garantir que tres armadilhas do
> build continuem explicadas, e duas dessas explicacoes sao comentarios do `src/main.tex`.
>
> Portanto a regra de seguranca tem **duas** linhas, nao uma:
>
> 1. as 60 diretivas `% !TeX root` (guardadas pelo `check_tex_root.py`);
> 2. os dois blocos de comentario do `src/main.tex` que contam `three-builds-one-source` e
>    `nested-if-scanning-hazard` (guardados pelo `check_comment_hygiene.py`). São ~10 linhas no total.
>
> **DECISAO SUA, se um dia quiser apagar tambem esses dois:** ou (a) move as duas explicacoes para
> `src_utils/README_SRC.md`, junto da terceira, que ja mora em markdown e por isso sobrevive — o gate
> passa a encontra-las la e o `.tex` fica limpo; ou (b) retira as duas stories da lista `STORIES`
> deliberadamente, aceitando que as armadilhas deixem de ter guardiao. **A opcao (a) e a que eu
> recomendo**, e ela e coerente com o padrao que o proprio gate ja usa para a terceira story.
>
> E a razao principal continua valendo, e nao e sobre gates: o que voce perde ao apagar um comentario e
> a memoria da decisao. Por isso a ordem certa e **primeiro decidir o item aqui, depois apagar o bloco**.

### 14.3 Os dois itens cuja base factual mudou nesta rodada

**Item 22 — VAZIO, a premissa deixou de existir. Nao precisa mais da sua decisao.** O item perguntava onde devia morar o
ponteiro para o apendice de cosseno de gradientes (a auditoria anterior citava a frase *"Appendix D reports the
gradient-cosine diagnostic..."* em `5_mobiwac/02_related.tex`). Essa frase **nao existe mais em lugar nenhum**: ela foi
removida nesta mesma rodada quando voce estabeleceu que os corpos dos artigos dos capitulos 3-5 devem ser autonomos
(registrado em `PENDENCIAS.md §2.31`, probes
`STL-01`..`STL-05`, commit `2bb82234`). A cadeia `grep` confirma zero ocorrencias de `gradient-cosine`
em prosa viva, e o PDF de defesa tambem nao contem a string. **Nao ha ponteiro para posicionar.** O que sobrou do
assunto e uma pergunta diferente, registrada onde e visivel: `PENDENCIAS.md §2.32` (o Apendice E nao e citado por nenhum
capitulo). O bloco de comentario correspondente pode sair sem perda.

**Item 6 — MECANICO, continua valido e pode fechar.** Verificado no PDF renderizado, nao no fonte: as duas metades da
redacao do veredito por regiao estao impressas (*"on the region task at four of the six"* e *"statistically non-inferior
within a two-point margin"*, alem de *"Each configuration has twenty"*). O item so pedia confirmacao de redacao ja
aplicada.

### 14.4 Achados novos nos comentarios (o que voce pediu: "eval if there are other points")

Varri os 5.352 linhas de comentario procurando afirmacao que o proprio documento ja contradiz. Tres achados, em ordem de
importancia:

**(a) `content.tex:374-380` da uma orientacao que hoje nao se aplica, e isso e o tipo de comentario que engana quem le
depois.** O bloco avisa que "Appendix B" e ambiguo entre os dois volumes e afirma:
*"Every prose pointer at the moved material already says 'Appendix~B/D of \\extravolume' (measured: 10 sites, all
carrying 'of \\extravolume')"*, concluindo *"no reader-facing sentence is ambiguous today; keep naming the volume in any
new pointer"*. **Medido agora: existe exatamente 1 linha viva com
`\extravolume` em toda a arvore, e ela e a propria definicao do macro em `preamble.tex:191`.** Os 10 sites de prosa
foram removidos nas rodadas anteriores. A instrucao final ("keep naming the volume")
continua sendo um bom conselho, mas a medicao que a sustenta esta errada por um fator de 10 e o diagnostico de
ambiguidade nao tem mais objeto. **Sugestao: este bloco e candidato a remocao, nao a correcao** — o conselho util cabe
em uma linha.

**(b) 6 flags `[VERIFY]` genuinamente abertas e invisiveis para o seu fluxo de revisao.** Ha 13 mencoes de `[VERIFY]`
nos comentarios, mas a maioria e prosa *sobre* uma flag ("o [VERIFY] que este bloco substitui esta fechado"). Contando
so as linhas que **abrem** um bracket `[VERIFY:` ou `[VERIFY,`, sao 6, e nenhuma delas aparece como item numerado deste
arquivo — hoje so um `grep` as encontra. Estao detalhadas em `## 14.6` abaixo, uma a uma, com o que cada uma pede.

> *Nota de medicao, para nao repetir o erro:* minha primeira contagem disse 8. Ela classificava como
> "aberta" qualquer linha contendo `[VERIFY`, incluindo duas que apenas mencionavam uma flag ja fechada.
> A contagem de 6 usa `\[VERIFY[:,]` (a flag sendo *aberta*, nao citada) e foi conferida linha por linha.
> Comando em 14.6.

**(c) 7 comentarios que se auto-descrevem por contagem, e contagem deriva.** Ex.: `4_courb.tex:8` diz *"26 sites '
MTLNet' -> 'MTLnet' (24 printed, 2 in comments)"*; a arvore hoje tem 80 ocorrencias de
`MTLnet` (47 em prosa, 33 em comentario). **Aqui nao ha erro**: aquele comentario descreve um evento de 2026-07-27
(quantos sites foram renomeados naquele dia), nao o estado atual — e `apx_b_errata.tex:293`
ate registra explicitamente essa distincao. Anoto para que uma varredura futura nao os "corrija" para numeros de hoje e
destrua o registro historico. **Sem acao.**

### 14.5 A ordem que eu recomendo, se o objetivo e reduzir comentario

Nao e uma decisao minha, mas a medicao aponta um caminho barato:

1. **Feche o item 22 (premissa vazia) e o item 6 (mecanico, verificado no PDF).** Custo zero de julgamento, libera dois
   blocos.
2. **Decida os 8 `[VERIFY]` de 14.4 (b) e o bloco de 14.4 (a).** São os comentarios que hoje afirmam algo desatualizado
   ou pedem algo invisivel; sao os que mais valem a sua atencao.
3. **Depois disso, ataque os 51 marcadores restantes por arquivo, do mais carregado para o menos**
   (`2_fundamentals.tex` primeiro, 8 marcadores e 1.115 linhas de comentario). Cada item fechado autoriza apagar o bloco
   inteiro que o acompanha — e ai a reducao vem em centenas de linhas, nao em unidades.
4. **A regra de seguranca (CORRIGIDA -- ver a caixa de correcao em 14.2):** ha DUAS familias de comentario que nao podem
   sair sem providencia, nao uma. (i) as 60 diretivas `% !TeX root`, guardadas pelo `check_tex_root.py`; (ii) os dois
   blocos de `src/main.tex` que explicam
   `three-builds-one-source` e `nested-if-scanning-hazard`, guardados pelo `check_comment_hygiene.py`
   (~10 linhas; para apaga-los tambem, mova as explicacoes para `src_utils/README_SRC.md`, onde a terceira story do
   mesmo gate ja mora). Fora dessas duas familias, o resto e seguro para o build e para os 208 probes. O
   `sync_src_clean.py` ja preserva as diretivas e avisa sobre duplicatas -- ele NAO cobre o caso (ii), e o `src_clean`
   de fato falha nesse gate hoje.

### 14.6 As 6 flags `[VERIFY]` abertas, cada uma com o que decidir

Localize-as com:

```bash
cd articles/dissertacao/src
grep -rn --include="*.tex" --exclude-dir=build '\[VERIFY[:,]' .
```

**V1 — `2_fundamentals.tex:376` · convencao de media do "Cat F1" varrido.** O comentario registra que **toda** fonte
grava "Cat F1" sem dizer se e macro ou weighted, por isso a prosa escreve "category F1" e nao "macro-F1". Duas saidas,
ambas honestas: **(a)** voce confirma a convencao e a prosa passa a nomea-la (mais informativo, exige que voce saiba
qual foi); **(b)** os dois valores saem e a clausula fica qualitativa (mais barato, perde os numeros). Isto e uma
decisao de *conteudo*, nao de redacao: pela lei do repositorio todo numero carrega sua convencao, e hoje esse par nao
carrega.

**V2 — `2_fundamentals.tex:736` · as duas perdas auxiliares do Cap.5 devem ser nomeadas aqui?** O texto atual apresenta
a equacao **sem** alegar ser a loss completa de toda execucao do Cap.5, e essa cautela esta correta. A flag registra que
nomear os dois termos auxiliares exigiria a configuracao da execucao da representacao entregue, *"which I did not
establish this session"*.

> **ESTA FLAG PODE FECHAR: o que faltava ja existe.** O Apendice E, escrito depois dela, imprime a
> equacao completa (`eq:apx-check2hgi-loss`) com **cinco** termos e seus pesos — tres contrastivos
> (0,4 / 0,3 / 0,3) e exatamente os dois auxiliares que a flag menciona: reconstrucao de lugar mascarado
> (0,3) e ancora da tabela de lugares (0,1), com a nota de que os coeficientes sao pesos de projeto
> fixos e nao precisam somar 1. Todos foram conferidos contra o codigo na auditoria do Apendice E.
> **Portanto a sua decisao nao e mais "descobrir os termos", e so editorial:** o Cap.2 repete esse
> detalhe, ou continua apresentando a forma reduzida e deixa o detalhe completo no apendice? A segunda
> opcao e coerente com o Cap.2 ser um capitulo fino (~8-12 paginas).

**V3 — `apx_a_contributions.tex:176` · divulgar as variantes Delta-m do `METRICS.md` e a regra de extracao F51?** O
comentario diz que nao foi possivel estabelecer que qualquer das duas pertence a configuracao reportada, e por isso
nenhuma foi nomeada. Se nao pertencem a configuracao reportada, o silencio atual e o correto e a flag fecha sem edicao;
se pertencem, faltam no registro de reprodutibilidade.

**V4 — `apx_a_contributions.tex:186` · manifesto de versoes de pacote para o codigo liberado.** A flag diz apenas que,
**se existir**, esse manifesto pertenceria a essa secao. Decisao de uma palavra: existe (e voce quer inclui-lo) ou nao
existe (e a flag fecha). Note que a mesma secao ja declara explicitamente que hardware, versoes de pacote e
configuracoes de treino por modelo estao **fora** de proposito — se essa exclusao continua valendo, V4 fecha por
coerencia com ela.

**V5 — `apx_b_errata.tex:465` · marcada "open and inherited": a divergencia de ~2x na contagem de usuarios da Florida.**
A extracao da epoca do CBIC conta 10.460 usuarios contra os 20.301 da linha publicada do CoUrb, e a diferenca nao foi
reconstruida a partir de artefatos versionados. Sua decisao de 2026-07-24 fixou **qual** numero os capitulos reportam,
sem fixar **por que** os dois diferem. O paragrafo foi escrito para permanecer verdadeiro nas duas hipoteses, entao
**nada esta errado hoje** — mas se voce algum dia resolver a origem da divergencia, a frase sobre a comparacao
controlada deve ser revisitada. Esta e a unica das seis que e legitimamente de longo prazo: pode ficar aberta.

**V6 — `apx_f_cosine.tex:666` · extensao por dataset para California, Texas e Istanbul.** O comentario registra estado
de execucao, lido do `_status.json` do job e nao do log: o job foi morto por SIGTERM num teto de 35 minutos de parede,
tendo concluido alabama, arizona e georgia (de onde vem tres dos quatro datasets do apendice) e sido cortado dentro do
fold 1 da california; texas e istanbul nunca comecaram. Foram reenviados como jobs separados: `c2a02f5d` e `d332e69e`
(texas, istanbul) e `213ce119` (california, por fold).

**Tentei resolver isso para voce e nao consegui — o dado nao esta no repositorio.** Procurei os tres IDs de job em todo
`.json` e `.md` da arvore e **nenhum aparece**: o resultado dos reenvios nao esta versionado aqui, so o ID. Nao tenho
acesso ao `ssh:nespedgpu` nesta sessao para consultar o estado, e nao vou supor que terminaram.

```bash
cd /Users/vitor/Desktop/mestrado/ingred
for j in c2a02f5d d332e69e 213ce119; do echo -n "$j: "; grep -rl "$j" --include="*.json" --include="*.md" . | wc -l; done   # 0 0 0
```

> **DECISAO SUA, e ela tem duas partes:** (1) alguem precisa olhar o estado desses tres jobs no cluster —
> **essa parte e sua ou de quem tem acesso**, eu nao consigo; (2) de posse disso, o apendice **espera** os
> resultados e passa a cobrir sete datasets, **ou fecha** com os quatro que ja tem e declara o escopo
> explicitamente. A opcao (2)-fecha e defensavel hoje: o apendice ja diz de quantos datasets fala. Esta e
> a flag com maior chance de estar desatualizada, justamente porque depende de estado externo ao repo.

---

## Auditoria de 2026-08-03 — validade, obsolescencia e o que ja pode fechar

**CORRECAO 2026-08-03 (achado do revisor, commit 192e9a82).** O paragrafo "Metodo" abaixo NUNCA citou numeros de
linhas -- o erro nao esta neste arquivo. Ele estava na MENSAGEM DE COMMIT de 192e9a82, que atribuia a
`1_introduction.tex` a medicao "92 insertions/62 deletions" quando a medicao real desse arquivo, na epoca, era 52
insertions/12 deletions (exec-log `caff3bd8`, cell 2578); 92/62 pertence a uma medicao ANTERIOR de `2_fundamentals.tex`,
colada no arquivo errado no texto do commit. Nota corretiva ja anexada ao commit via `git notes`; este paragrafo existe
so para que a correcao tambem apareca aqui, onde voce le. **A conclusao substantiva nao muda**: os dois arquivos
derivaram o suficiente para mover numeros de linha, e os 56 marcadores continuam resolvendo 1-para-1 mesmo assim -- so a
mensagem do commit, nao este documento, tinha o par de numeros errado.

**Metodo.** Os 56 marcadores foram relocalizados no fonte vivo (nao pela linha registrada acima, que andou em
`1_introduction.tex` e `2_fundamentals.tex` apos edicoes concorrentes desde a geracao deste arquivo, mas por
correspondencia de conteudo dentro do mesmo arquivo). **As 56 correspondencias fecham 1-para-1: nenhum marcador
desapareceu, nenhum se fundiu com outro.** Cada item foi entao cruzado contra `PENDENCIAS.md` §2/§4 e
`_history/_archive/PENDENCIAS_RESOLVIDOS.md`, procurando por uma decisao ja registrada que respondesse a mesma pergunta.

**CORRECAO 2026-08-04 (achado do revisor).** A frase original aqui dizia que nenhum item deste "
documento e nenhum item `AUT-`/`CONSIDERATIONS` compartilhavam arquivo+trecho, apoiada num loop cuja variavel de entrada
(`answered_locs`) ja saira vazia por um bug de parsing anterior -- a checagem nao provava nada. Refeito com o estado
atual do §4 (11 itens `AUT-` ainda abertos ali; os demais dos 37 originais ja foram resolvidos e saem do §4 conforme
fecham, entao "37" tambem estava desatualizado):
HA sobreposicao de ARQUIVO entre alguns itens `AUT-` e alguns dos 56 abaixo (`content.tex`,
`1_introduction.tex`, `6_conclusion.tex`, `apx_b_static_scope.tex` aparecem nos dois lados), mas nenhum par verificado
aponta para o MESMO trecho: os itens `AUT-` abertos tratam de secoes/paragrafos inteiros (ex.: AUT-32 pede revisao da
abertura do Cap.6; AUT-35 trata das tres limitacoes de §6.3), e os marcadores deste arquivo apontam para frases
especificas dentro dos mesmos capitulos. Continuam sendo registros por desenho diferentes -- este cobre marcadores de
proveniencia no `.tex`, o outro cobre pontos de revisao do orientador/coautor -- mas a garantia de "zero sobreposicao"
era mais forte do que a checagem sustentava, e o numero "37" do §4 esta desatualizado (o §4 hoje tem 11 itens `AUT-`
abertos; os outros ja fecharam).

**Classificacao de cada um dos 56 itens (numeracao desta pagina, nao a do fonte):**

| #  | Status                   | Por que                                                                                                                                                                                        |
|----|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1  | PARCIAL                  | 'Modelos ajustados' ainda pede aprovacao (GLOSSARY); o bloco ORPHANED pede destino. Duas partes, nenhuma mecanica.                                                                             |
| 2  | PRECISA DE VOCE          | Pedido de confirmacao de escolha de prosa/convencao ja feita; nao ha decisao registrada que resolva.                                                                                           |
| 3  | PRECISA DE VOCE          | Pedido de confirmacao de escolha de prosa/convencao ja feita; nao ha decisao registrada que resolva.                                                                                           |
| 4  | PRECISA DE VOCE          | Pedido de confirmacao de escolha de prosa/convencao ja feita; nao ha decisao registrada que resolva.                                                                                           |
| 5  | PRECISA DE VOCE          | Pedido de confirmacao de escolha de prosa/convencao ja feita; nao ha decisao registrada que resolva.                                                                                           |
| 6  | MECANICO                 | BLQ-2 foi respondido (PENDENCIAS_RESOLVIDOS §6.10) e a redacao aplicada foi verificada no render (main.pdf, 'Each configuration has twenty...').                                               |
| 7  | PRECISA DE VOCE          | Pedido de confirmacao de escolha de prosa/convencao ja feita; nao ha decisao registrada que resolva.                                                                                           |
| 8  | PRECISA DE VOCE          | Confirmacao de prosa + um [VERIFY] aberto (convencao de agregacao do Cat F1 nao nomeada em nenhuma fonte); nenhuma decisao registrada resolve, e o VERIFY exige checar o codigo/fonte de novo. |
| 9  | PRECISA DE VOCE          | Sign-off ordinario de prosa + um [VERIFY] aberto (ponto nao estabelecido na fonte); nenhuma decisao registrada resolve.                                                                        |
| 10 | PRECISA DE VOCE          | Pedido de confirmacao de escolha de prosa/convencao ja feita; nao ha decisao registrada que resolva.                                                                                           |
| 11 | PRECISA DE VOCE          | Confirmacao de escolha de prosa/redacao ja proposta; nenhuma decisao registrada resolve.                                                                                                       |
| 12 | PRECISA DE VOCE          | Confirmacao de escolha de prosa/redacao ja proposta; nenhuma decisao registrada resolve.                                                                                                       |
| 13 | PRECISA DE VOCE          | Confirmacao de escolha de prosa/redacao ja proposta; nenhuma decisao registrada resolve.                                                                                                       |
| 14 | PRECISA DE VOCE          | Bloco ORPHANED com duas perguntas (destino do marcador + revisao de imagem-charneira); nenhuma decisao registrada resolve.                                                                     |
| 15 | AMBIGUO -> Opus 5 / voce | O proprio marcador nao especifica opcoes claras; a ambiguidade e do texto-fonte, nao da traducao.                                                                                              |
| 16 | PRECISA DE VOCE          | Confirmacao de escolha de prosa/redacao ja proposta; nenhuma decisao registrada resolve.                                                                                                       |
| 17 | PRECISA DE VOCE          | Confirmacao de escolha de prosa/redacao ja proposta; nenhuma decisao registrada resolve.                                                                                                       |
| 18 | PRECISA DE VOCE          | Confirmacao de escolha de prosa/redacao ja proposta; nenhuma decisao registrada resolve.                                                                                                       |
| 19 | PRECISA DE VOCE          | Confirmacao de escolha de prosa/redacao ja proposta; nenhuma decisao registrada resolve.                                                                                                       |
| 20 | PRECISA DE VOCE          | Confirmacao de escolha de prosa/redacao ja proposta; nenhuma decisao registrada resolve.                                                                                                       |
| 21 | PRECISA DE VOCE          | Confirmacao de escolha de prosa/redacao ja proposta; nenhuma decisao registrada resolve.                                                                                                       |
| 22 | MECANICO                 | AUTHOR DECISION (round9f, PENDENCIAS_RESOLVIDOS 2.9) responde exatamente esta pergunta; aplicacao conferida no fonte vivo.                                                                     |
| 23 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/numero ja proposta; nenhuma decisao registrada resolve.                                                                                             |
| 24 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/numero ja proposta; nenhuma decisao registrada resolve.                                                                                             |
| 25 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/numero ja proposta; nenhuma decisao registrada resolve.                                                                                             |
| 26 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/numero ja proposta; nenhuma decisao registrada resolve.                                                                                             |
| 27 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/numero ja proposta; nenhuma decisao registrada resolve.                                                                                             |
| 28 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/numero ja proposta; nenhuma decisao registrada resolve.                                                                                             |
| 29 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/numero ja proposta; nenhuma decisao registrada resolve.                                                                                             |
| 30 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/numero ja proposta; nenhuma decisao registrada resolve.                                                                                             |
| 31 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/numero ja proposta; nenhuma decisao registrada resolve.                                                                                             |
| 32 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/numero ja proposta; nenhuma decisao registrada resolve.                                                                                             |
| 33 | PRECISA DE VOCE          | Bloco ORPHANED com decisao de convencao numerica (contagem por braco vs total) e destino do marcador; nenhuma decisao registrada resolve.                                                      |
| 34 | PRECISA DE VOCE          | Duas perguntas fundidas (convencao numerica + destino do ORPHANED); nenhuma decisao registrada resolve a primeira.                                                                             |
| 35 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/fato ja proposta ou pendente de checagem externa (ex.: publicacao de arquivos, conversa com orientador); nenhuma decisao registrada resolve.        |
| 36 | PRECISA DE VOCE          | PENDENCIAS_RESOLVIDOS 5.6 resolveu que Cap.4 nao precisa mudar, mas a premissa dos dumps distintos (SNAP vs figshare) segue sem confirmacao do autor -- ele pede fatos das proprias execucoes. |
| 37 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/fato ja proposta ou pendente de checagem externa (ex.: publicacao de arquivos, conversa com orientador); nenhuma decisao registrada resolve.        |
| 38 | AMBIGUO -> Opus 5 / voce | O proprio marcador nao especifica opcoes claras; a ambiguidade e do texto-fonte, nao da traducao.                                                                                              |
| 39 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/fato ja proposta ou pendente de checagem externa (ex.: publicacao de arquivos, conversa com orientador); nenhuma decisao registrada resolve.        |
| 40 | PRECISA DE VOCE          | Depende de um fato externo ao texto (se os arquivos serao publicados antes da defesa) que so o autor sabe.                                                                                     |
| 41 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/fato ja proposta ou pendente de checagem externa (ex.: publicacao de arquivos, conversa com orientador); nenhuma decisao registrada resolve.        |
| 42 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/fato ja proposta ou pendente de checagem externa (ex.: publicacao de arquivos, conversa com orientador); nenhuma decisao registrada resolve.        |
| 43 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/fato ja proposta ou pendente de checagem externa (ex.: publicacao de arquivos, conversa com orientador); nenhuma decisao registrada resolve.        |
| 44 | AMBIGUO -> Opus 5 / voce | O proprio marcador nao especifica opcoes claras; a ambiguidade e do texto-fonte, nao da traducao.                                                                                              |
| 45 | PRECISA DE VOCE          | Depende de uma conversa com o orientador que so o autor pode confirmar como concluida.                                                                                                         |
| 46 | PRECISA DE VOCE          | Pede explicitamente que o autor leia o paragrafo antes do envio; a mensagem enfraquece uma premissa da sua propria decisao anterior.                                                           |
| 47 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/fato ja proposta ou pendente de checagem externa (ex.: publicacao de arquivos, conversa com orientador); nenhuma decisao registrada resolve.        |
| 48 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/fato ja proposta ou pendente de checagem externa (ex.: publicacao de arquivos, conversa com orientador); nenhuma decisao registrada resolve.        |
| 49 | AMBIGUO -> Opus 5 / voce | O proprio marcador nao especifica opcoes claras; a ambiguidade e do texto-fonte, nao da traducao.                                                                                              |
| 50 | AMBIGUO -> Opus 5 / voce | O proprio marcador nao especifica opcoes claras; a ambiguidade e do texto-fonte, nao da traducao.                                                                                              |
| 51 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/fato ja proposta ou pendente de checagem externa (ex.: publicacao de arquivos, conversa com orientador); nenhuma decisao registrada resolve.        |
| 52 | PRECISA DE VOCE          | Depende de um fato sobre a propria infraestrutura experimental (onde o Cap.4 rodou) que so o autor sabe.                                                                                       |
| 53 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/fato ja proposta ou pendente de checagem externa (ex.: publicacao de arquivos, conversa com orientador); nenhuma decisao registrada resolve.        |
| 54 | AMBIGUO -> Opus 5 / voce | O proprio marcador nao especifica opcoes claras; a ambiguidade e do texto-fonte, nao da traducao.                                                                                              |
| 55 | PRECISA DE VOCE          | Confirmacao de escolha de conteudo/redacao/fato ja proposta ou pendente de checagem externa (ex.: publicacao de arquivos, conversa com orientador); nenhuma decisao registrada resolve.        |
| 56 | AMBIGUO -> Opus 5 / voce | O proprio marcador nao especifica opcoes claras; a ambiguidade e do texto-fonte, nao da traducao.                                                                                              |

**Resumo:** 2 mecanicos (fecham citando uma decisao ja tomada, com a aplicacao verificada no render), 1 parcial (uma
metade fecha, a outra nao), 46 precisam da sua palavra porque sao escolhas de conteudo, redacao ou fato que nenhuma
decisao anterior resolve, e 7 estao sinalizados como ambiguos -- o proprio bloco de origem nao especifica o que
exatamente deve ser confirmado, entao a recomendacao e reler o trecho original no `.tex` (nao a traducao aqui) ou pedir
a um modelo mais capaz (Opus 5) uma segunda leitura antes de decidir.

**Os dois mecanicos, com a evidencia:**

- **#6** (`1_introduction.tex`) -- a decisao BLQ-2 (`PENDENCIAS_RESOLVIDOS §6.10`, arquivado 2026-08-03) respondeu
  exatamente esta pergunta ("mantenha everywhere para o categoria e especifique onde for preciso para o next-region").
  **CORRIGIDO 2026-08-04 (achado do revisor):** a verificacao original so conferiu no render a metade n=20/n=4 do bloco,
  nao a metade do veredito de regiao que BLQ-2 realmente decide. Reconferido agora: a frase renderizada e "outperforms
  the dedicated models on the category task at all six datasets and on the region task at four of the six. At the other
  two, it remains statistically non-inferior within a two-point margin (TOST)" -- as duas metades corretas, ambas
  presentes. O marcador pode ser removido citando essa decisao.
- **#22** (`5_mobiwac/06_results.tex`) -- uma AUTHOR DECISION explicita (round9f, 2026-08-02,
  `PENDENCIAS_RESOLVIDOS 2.9`) responde a mesma pergunta (onde colocar o ponteiro ao apendice de gradient-cosine).
  **CORRIGIDO 2026-08-04 (achado do revisor):** a verificacao original conferiu so o fonte vivo, nao o render, e o
  commit dizia "verificado no render" para os dois itens -- falso para este. Reconferido agora no `main.pdf`: "Appendix
  D reports the gradient-cosine diagnostic of this chapter on the final model across seven datasets", no paragrafo de
  abertura da secao, exatamente como a decisao pede. O marcador pode ser removido citando essa decisao.

**Nao removi nenhum marcador do `.tex` nem editei os 56 blocos acima.** Esta secao e so o veredito da auditoria; a
decisao de remover os marcadores mecanicos, ou de responder os que precisam de voce, e sua.

---

## Rodada 15 (2026-08-04) — os itens 1-6 fecharam; tres defeitos de prosa encontrados no caminho

**O que voce pediu, e o que foi feito.** Voce preencheu as decisoes dos itens **1 a 6**, que sao exatamente os dois
capitulos-alvo desta rodada (`content.tex` e `1_introduction.tex`). Todos os seis foram aplicados no fonte: o bloco
extenso de cada um saiu e no lugar ficou o marcador minimo
`[NEEDS SIGN-OFF NN | CLOSED]` com uma ou duas linhas de resolucao. Nenhum item 7+ foi tocado.

| #  | Sua decisao                                                               | O que sobrou no `.tex`                                                                                    |
|----|---------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| 01 | descartar o bloco ORPHANED; "Modelos ajustados" fica fora do glossario    | marcador + **a nota de omissao do par de tarefas**, que voce mesmo pediu no round 10 (FAB-08)             |
| 02 | manter Acc@10; omitir joint-best e faixa de macro-F1; manter "depende de" | marcador + **o guard do termo reservado** ("proximo lugar visitado" nao pode ser usado)                   |
| 03 | remover o marcador (opcao 2)                                              | marcador + **a regra de paridade**: Resumo e Abstract sao uma afirmacao em duas linguas                   |
| 04 | manter as omissoes e o verbo (opcoes 2 e 3)                               | marcador, espelhando o 02 do lado do Abstract                                                             |
| 05 | a forma atual e aceitavel                                                 | marcador + **o motivo de nao "simplificar"**: a frase foi afastada de proposito do Cap.5                  |
| 06 | tudo certo, manter                                                        | marcador + **o motivo da assimetria**: categoria pode alegar os seis datasets, regiao precisa da particao |

**O criterio que usei para decidir o que ficava.** Descartei medicao historica (contagens de palavras de um build de 105
paginas que nao existe mais), proveniencia de numeros que **nao estao mais citados**
nesses blocos (a faixa 5.3-9.4 e o par quatro/dois seguem documentados onde ainda sao citados, no
`6_conclusion.tex` -- conferido: nenhum desses valores aparece em prosa viva do `content.tex`), e avisos de tarefas ja
concluidas. Guardei o que impede um agente futuro de **desfazer** uma decisao sua sem saber: as regras de paridade, os
termos proibidos, e as duas explicacoes de assimetria.

### 15.1 Dois defeitos de prosa no Resumo, que o Abstract nao tem

Encontrados ao ler o texto vivo para decidir o que os comentarios ainda anotavam. **Nao corrigi**: sao alteracoes no
texto renderizado e o par Resumo/Abstract e regido pela paridade de afirmacoes, entao qualquer edicao precisa da sua
palavra. Ambos estao **impressos na pagina 2** do volume de defesa.

**D1 — `content.tex:89`, frase truncada. Duas frases fundidas numa que nao fecha o sentido:**

> "O protocolo empregou validação cruzada com usuários disjuntos entre treinamento e teste
> estatísticos pareados."

O gemeo ingles esta correto e mostra o que se perdeu: *"The protocol used user-disjoint cross-validation and paired
statistical tests."* Faltou o **"e testes"** — o portugues diz
"entre treinamento e teste estatisticos pareados", grudando "teste" (do par treinamento/teste) no adjetivo "estatisticos
pareados". Correcao minima, preservando a paridade com o ingles:
*"...validação cruzada com usuários disjuntos entre treinamento e teste, e testes estatísticos pareados."*

**D2 — `content.tex:85`, "da previsão" duplicado:**

> "reuniu duas tarefas sequenciais: a previsão da próxima categoria e **da previsão** da próxima
> região."

O gemeo ingles esta correto (*"paired two sequential tasks: next-category and next-region prediction"*). Correcao
minima: *"a previsão da próxima categoria e da próxima região."*

> **DECISAO SUA:** aprovo as duas correcoes minimas acima (elas nao mexem em nenhuma afirmacao,
> numero ou hedge, so em concordancia), ou prefere outra redacao? Aplico as duas no mesmo commit,
> porque a lei de paridade exige que Resumo e Abstract sejam editados juntos — aqui o ingles ja esta
> certo, entao so o portugues muda.

### 15.2 A lista de capitulos ficou sem frase de entrada

`1_introduction.tex`, secao "Organization of this dissertation". O paragrafo termina em *"...or, for the article under
review, the submitted manuscript."* e o render **entra direto no primeiro bullet**, sem frase de ligacao. A frase de
entrada existia (*"The collection is organized as follows:"*) mas estava **presa dentro de um comentario**; o pass do
round 7 detectou isso, reportou, e deliberadamente nao corrigiu porque aquele pass tinha de manter o PDF byte-identico.

**Essa restricao nao existe mais.** Verificado no render (2026-08-04): nem a frase de entrada nem a antiga frase de
errata aparecem no PDF. Substitui o bloco de comentario obsoleto por um `[OPEN]`
que diz exatamente isso, no lugar onde a frase entraria.

> **DECISAO SUA:** restauro a frase de entrada (*"The collection is organized as follows:"*, ou outra
> que voce prefira)? Isso **adiciona uma linha de prosa** a pagina 15 e pode empurrar a paginacao em
> uma pagina — por isso nao apliquei. Uma lista sem frase de entrada e o tipo de coisa que um
> orientador circula na primeira leitura.

> **FECHADO por voce (2026-08-04):** *"I have read it and decide that we can close is already resolve,
> we have add a lead-in phrase. You can remove it from the .tex"*. Bloco `[OPEN]` removido de
> `1_introduction.tex`. **A frase de entrada e a que abre o paragrafo:** *"This dissertation is
> organized as a collection of works, where each central chapter is an independent article."* — ela
> nomeia a estrutura antes dos bullets, entao a lista nao esta orfa. Confirmado na pagina 15 do render.

**Duas correcoes ao que eu havia escrito aqui, ambas achados seus:**

1. **Voce nao conseguiu achar a §15.2 porque eu escrevi o ponteiro errado.** O comentario no `.tex`
   dizia `see NEEDS_SIGN_OFF.md §15.2`, mas o titulo neste arquivo e `### 15.2`, **sem** o `§`. Uma busca por "§15.2"
   retorna zero. Era o unico ponteiro desse formato no `src/` (conferido), e ele saiu junto com o bloco. **Licao para os
   proximos:** cite secoes deste arquivo como `15.2`, nao `§15.2` — o `§` e usado para `PENDENCIAS.md` e para as leis
   (`WRITING_LAW §3`), que de fato numeram com `§`.

2. **A segunda metade do bloco guardava algo que nunca existiu.** Ela avisava "do not restore" a frase de errata que
   apontava para o volume suplementar. Conferido em cinco commits (`e3e6d796`,
   `71fc3ef9`, `2804131b`, `a47691f8`, `45c75611`): **`1_introduction.tex` nunca teve `\extravolume`
   em prosa viva** — a frase existia so dentro do comentario. O guard protegia contra uma reversao impossivel, e some
   sem custo. Os ponteiros reais estavam em `3_cbic.tex`, `3_cbic/method.tex`,
   `4_courb.tex`, `5_mobiwac.tex` e `apx_a_contributions.tex`, e esses **estao** guardados por probes (`RTV-03`..
   `RTV-08b`), que continuam valendo.

### 15.3 Comentario obsoleto removido, sem pedir decisao

- `1_introduction.tex:320-337` — o bloco explicava por que a frase de errata apontava para o volume suplementar e
  reportava a prosa presa. **A frase de errata nao existe mais em prosa viva** (a regra standalone da rodada 14 removeu
  os ponteiros), e a prosa presa virou o `[OPEN]` de 15.2. O resto do bloco descrevia decisoes sobre texto que ja saiu.
- `1_introduction.tex:35-39` — marcador `ORPHANED` sobre uma edicao trivial e ja resolvida ("users"
  no plural, a pedido do orientador). Mantive a razao em duas linhas e removi o envelope de revisao.

### 15.4 Verificacao

Quatro alvos em paralelo, `rc=0`, `tex_errors=0`, zero Overfull, **paginacao inalterada**
(116/113/117/26) — que e a prova de que so comentario saiu. `make check` `rc=0` com zero linhas FAIL,
`make selftest` `rc=0`, e os **208 de 208 probes** do `check_audit_claims` continuam valendo.

---

## 0. Resumo/Abstract (content.tex)

### 1. [CLOSED rodada 15, 2026-08-04] Corte Resumo/Abstract, termo 'Modelos ajustados' e bloco orfao

**Local:** `src/content.tex:51`

**Contexto:** No round 6 (2026-07-28), o par Resumo (p.3-4, 500 words / 10 sentences / mean 50.0) e Abstract (p.5, 423
words / 10 sentences / mean 42.3) foi cortado por decisao do autor de que ambos os blocos estavam longos demais, ficando
dentro do envelope medido nas cinco dissertacoes de exemples/ (195-282 words, 6-12 sentences, mean 19.5-37.5; Resumos
233-282, Abstracts 195-250); nada do 'claim floor' foi cortado, e duas afirmacoes foram removidas por nao estarem nesse
piso (o maior custo de treinamento do primeiro estudo e a 'task-pair evolution'), tabuladas em src_utils/_
round6/15_resumo_abstract.md. No round10, PENDENCIAS §6 FAB-08, o autor ja decidiu: "Perfeito, mantemos assim! Mas vamos
adicionar um comentario sobre o resumo, que uma informacao esta sendo omitida o fato de serem tarefas diferentes entre
os dois primeiros e o ultimo artigo." O termo 'Modelos ajustados' para 'fitted models' e proposto mas ainda NAO consta
em GLOSSARY §6. Em 2026-08-02, o bloco foi marcado ORPHANED: a frase que ele anotava nao esta mais no texto apos o
clean-tree pass do autor, e foi mantida, sem realocacao de sentido, para revisao.

**O que decidir:** O autor precisa: (1) aprovar ou rejeitar 'Modelos ajustados' como termo canonico de GLOSSARY §6 para
'fitted models'; e (2) decidir o destino deste bloco ORPHANED (2026-08-02) -- descartar, realocar para onde a informacao
pertence agora, ou manter para revisao futura -- ja que a frase original que ele anotava nao existe mais no texto.

**Se ficar sem decisao:** O termo 'Modelos ajustados' permanece fora do glossario sem status canonico e o bloco orfao
continua sem destino definido, deixando a informacao sobre a diferenca de tarefas entre os estudos sem localizacao
confirmada no texto.

> **SUA DECISAO:** 2, como nem usamos esses termos mais podemos descartar. Sobre o termo 'Modelos ajustados', podemos
> manter fora, nem o usamos mais.

**RESOLVIDO (rodada 15, commit `e3e6d796`).** Bloco ORPHANED descartado; "Modelos ajustados" NAO entra no GLOSSARY §6.
Em `content.tex:49` ficou `[NEEDS SIGN-OFF 01 | CLOSED]` mais a nota de omissao do par de tarefas que voce pediu no
round 10 (FAB-08): ela sobreviveu de proposito, para que a omissao nao seja redescoberta como defeito.

---

### 2. [CLOSED rodada 15, 2026-08-04] Nomenclatura e omissões no resumo (Acc@10, macro-F1)

**Local:** `src/content.tex:134`

**Contexto:** Marcador levantado na rodada 6 (2026-07-28), com ressalvas do autor de 2.1/3-4-5 (2026-07-24) mantidas ao
longo do corte. No resumo de alto nível, a métrica de margem permanece nomeada como "Acc@10"; a convenção de joint-best
e a faixa de macro-F1 foram omitidas desse resumo; e o verbo "Determina se" foi mantido como "depende de" porque o
confundimento da Seção 6.2 proíbe uso de verbo causal.

**O que decidir:** O autor precisa confirmar se está de acordo com as três escolhas descritas: (1) manter o nome
"Acc@10" para a métrica de margem, (2) omitir a convenção de joint-best e a faixa de macro-F1 do resumo de alto nível, e
(3) manter "depende de" no lugar de "Determina se" devido ao confundimento da Seção 6.2.

**Se ficar sem decisao:** As decisões de nomenclatura da métrica, de omissão de detalhes (joint-best e faixa de
macro-F1) e de escolha de verbo não-causal permanecem sem a aprovação explícita do autor.

> **SUA DECISAO:** Podemos manter o Acc@10. Sim vamos omitir, como não explicamos o que é temos que omitir. vamos manter
> depende de, mais facil para leitura.

**RESOLVIDO (rodada 15, commit `e3e6d796`).** As tres escolhas mantidas. Em `content.tex:99` ficou
`[NEEDS SIGN-OFF 02 | CLOSED]` mais o guard do termo reservado: "proximo lugar visitado" nao pode ser escrito ali porque
colide com "next place" (GLOSSARY §1), a tarefa fora de escopo. A exclusao em si e carregada por
`1_introduction.tex:90-91`, nao por este bloco.

---

### 3. [CLOSED rodada 15, 2026-08-04] Corte no Abstract (par de paridade do Resumo), bloco orfao removido

**Local:** `src/content.tex:174`

**Contexto:** Bloco de review sobre um corte no Abstract, rodada 6 (2026-07-28), feito como par de paridade de
reivindicacoes do Resumo acima (WRITING_LAW §6): mesmas afirmacoes, mesmos numeros, mesmos hedges, frase por frase,
ambos os blocos com onze frases correspondentes um a um. Os numeros citados nao sao computados aqui: 5.3 a 9.4 macro-F1
vem dos deltas por dataset/categoria de docs/studies/closing_data/v17_completion/stats_n20/RESULTS.md §1 (FL +5.34 no
extremo baixo, AZ +9.40 no extremo alto), conforme reportado por 6_conclusion.tex; "four of them" refere-se as quatro
linhas $^{\uparrow}$ de tables/mobiwac/results.tex (Istanbul, FL, TX, CA) contra as duas linhas $^{\approx}$ (AL, AZ),
mesma contagem declarada em 6_conclusion.tex. Em 2026-08-02 o bloco foi marcado como ORPHANED pelo autor durante uma
limpeza da arvore: a frase que este marcador anotava nao esta mais no texto. O trecho remanescente descreve um problema
estrutural -- na versao anotada, condicoes ficavam antes do sujeito "that joint model" (sujeito no indice de token 25),
fazendo o leitor carregar quatro condicoes nao vinculadas antes de saber o assunto da frase, na pagina mais lida do
documento -- com a recomendacao 'resultado primeiro, protocolo depois', preservando todo numero, hedge e convencao. O
bloco foi mantido, sem relocacao de sentido, para revisao.

**O que decidir:** Como este bloco esta marcado ORPHANED (a frase original que ele anotava nao existe mais no texto
atual), o autor precisa confirmar: (1) se o corte no Abstract e o par de paridade correspondente no Resumo ainda estao
de fato alinhados frase a frase apos a limpeza da arvore, e (2) se este marcador pode ser removido por nao ter mais um
trecho de texto para anotar, ou se precisa ser relocado para a frase equivalente na versao atual.

**Se ficar sem decisao:** O corte do Abstract e sua paridade de reivindicacoes com o Resumo (numeros, hedges e contagem
de linhas $^{\uparrow}$/$^{\approx}$) permanecem sem confirmacao do autor apos a limpeza da arvore, podendo deixar os
dois blocos divergentes sem que isso seja percebido.

> **SUA DECISAO:** vamos de 2.

**RESOLVIDO (rodada 15, commit `e3e6d796`).** Opcao 2: marcador removido. A proveniencia dos numeros saiu junto porque
nenhum deles e mais citado neste bloco (conferido: 5.3, 9.4 e "four of them" nao aparecem em prosa viva do
`content.tex`); seguem documentados no `6_conclusion.tex`, onde ainda sao citados. Ficou `[NEEDS SIGN-OFF 03 | CLOSED]`
mais a regra de paridade Resumo/Abstract.

---

### 4. [CLOSED rodada 15, 2026-08-04] Métrica Acc@10, omissões e verbo 'depends on'

**Local:** `src/content.tex:226` — renderiza no volume **defesa**, p. 3

**Contexto:** No resumo de alto nível, a métrica da margem de não-inferioridade continua nomeada explicitamente como
Acc@10. A convenção de joint-best e o intervalo de macro-F1 foram omitidos desse resumo. Além disso, "Determines
whether" foi mantido como "depends on", pois o confounder discutido na Seção 6.2 tornaria um verbo causal forte um
overclaim. Este marcador foi levantado na rodada 6 (2026-07-28) e incorpora ressalvas do autor de 2.1/3-4-5, de
2026-07-24, que foram carregadas através do corte de texto.

**O que decidir:** O autor precisa confirmar se concorda com as três escolhas feitas neste trecho: (1) manter Acc@10
nomeada como métrica da margem de não-inferioridade; (2) omitir a convenção de joint-best e o intervalo de macro-F1 do
resumo de alto nível; e (3) manter "depends on" em vez de "determines whether", dado o confounder da Seção 6.2.

**Se ficar sem decisao:** Se ignorado, a formulação atual do resumo -- incluindo a escolha de verbo mais cautelosa e as
omissões de conteúdo -- permanece publicada sem a validação explícita do autor.

> **SUA DECISAO:** vamos de 2 e 3;

**RESOLVIDO (rodada 15, commit `e3e6d796`).** Omissoes e verbo mantidos. `content.tex:182` ->
`[NEEDS SIGN-OFF 04 | CLOSED]`.

---

## 1. Introducao

### 5. [CLOSED rodada 15, 2026-08-04] Reformulacao de frase duplicada com Cap.5 (gate L3, fix A-1)

**Local:** `src/chapters/1_introduction.tex:86` — renderiza no volume **defesa**, p. 13

**Contexto:** No gate L3, fix A-1, foi identificado que a frase original era quase textual (near-verbatim) com o Cap.5 (
"one artifact to train, version, and deploy, and one forward pass whose single set of inputs produces both answers at
once"). A frase foi reformulada nesta ocorrencia para que o capitulo do artigo mantenha a redacao original; a alegacao
(claim) permanece inalterada.

**O que decidir:** Confirmar se a reformulacao feita aqui e aceitavel, ou se prefere reverter para a duplicacao original
(mantendo a frase quase-verbatim igual ao Cap.5).

**Se ficar sem decisao:** A reformulacao de prosa introduzida para evitar a duplicacao com o Cap.5 permanece sem sua
aprovacao.

> **SUA DECISAO:** A forma que está atual é aceitavel.

**RESOLVIDO (rodada 15, commit `e3e6d796`).** `1_introduction.tex` -> `[NEEDS SIGN-OFF 05 | CLOSED]`, mantendo o motivo
de nao "simplificar" a frase de volta: ela foi afastada de proposito da redacao do Cap.5, para que o capitulo
reproduzido conserve a original.

---

### 6. [CLOSED rodada 15, 2026-08-04] Redacao de n=20/n=4 no veredito por regiao

**Local:** `src/chapters/1_introduction.tex:316` — renderiza no volume **defesa**, p. 17

**Contexto:** O trecho "twenty repetitions per configuration (four seeds, five folds)" precisa manter os 20 fits
ajustados, nomear a unidade inferencial (n = 4) e incluir a clausula de particao fixa, conforme GLOSSARY ("paired
superiority test" e "n = 20 (fitted models) and n = 4 (inferential unit)"), stats_n20/RESULTS.md:65-67 e
STATISTICAL_PROTOCOL.md:187-190. Esta era a ultima ocorrencia que colapsava o veredito de regiao em "either outperforms
or matches", descartando a particao; o Capitulo 6 (:126-127) ja usa a redacao correta e este trecho deve espelha-la.
Pela decisao do autor no round10 (PENDENCIAS_RESOLVIDOS §6.10 (arquivado 2026-08-03) BLQ-2: "mantenha everywhere para o
categoria e especifique onde for preciso para o next-region"), a clausula de categoria mantem seu carater universal
(valido nos seis datasets) e a clausula de regiao precisa da particao. WRITING_LAW §3 proibe o uso de "everywhere"
isolado, entao a clausula de categoria deve nomear os seis datasets em vez disso.

**O que decidir:** Confirmar se a nova redacao para REV-014 esta correta: (1) a clausula de categoria mantem a afirmacao
universal mas nomeando os seis datasets (em vez de "everywhere", por causa do WRITING_LAW §3); e (2) a clausula de
regiao passa a mencionar explicitamente a particao (n = 20 fits, n = 4 como unidade inferencial, quatro seeds e cinco
folds), espelhando a redacao ja usada no Capitulo 6 :126-127.

**A redacao JA ESTA APLICADA — verificado no PDF, nao no fonte (2026-08-04).** As tres partes que o item pedia estao
impressas no volume de defesa: a clausula de regiao com a particao (*"on the region task at four of the six"*), o
veredito nao-inferior com a margem (*"statistically non-inferior within a two-point margin"*) e a unidade inferencial
(*"Each configuration has twenty"*). Reproduza:

```bash
cd articles/dissertacao/src && python3 -c "
import pypdfium2 as p, re
d=p.PdfDocument('build/main.pdf')
t=re.sub(r'\s+',' ',' '.join(d[i].get_textpage().get_text_range() for i in range(len(d))))
for s in ['on the region task at four of the six',
          'statistically non-inferior within a two-point margin',
          'Each configuration has twenty']:
    print(s in t, '|', s)
"
```

**Portanto a sua decisao aqui e binaria e barata:** ou voce le as tres frases no PDF e responde
"aprovado", e o bloco de comentario sai; ou aponta o que quer diferente. **Nao ha trabalho de verificacao sobrando** —
ele esta feito acima.

**Se ficar sem decisao:** o texto continua correto e o build continua verde; o unico custo e que o bloco de comentario
de ~30 linhas em `1_introduction.tex` permanece no fonte, contra o seu objetivo de reduzir comentario.

> **SUA DECISAO:** Tudo certo vamos manter em como está.

**RESOLVIDO (rodada 15, commit `e3e6d796`).** `1_introduction.tex` -> `[NEEDS SIGN-OFF 06 | CLOSED]`, mantendo o motivo
da assimetria (categoria pode alegar os seis datasets; regiao precisa da particao), que sem explicacao parece
inconsistencia e convida alguem a "corrigir".

---

## 2. Fundamentos

### 7. [CLOSED rodada 15, 2026-08-04] Escopo do teto de 93% (bound de Song) na secao 2.1

**Local:** `src/chapters/2_fundamentals.tex:40` — renderiza no volume **defesa**, p. 18

**Contexto:** No round 3 (2026-07-24), a afirmacao da secao 2.1 de que '93% is the ceiling any model should be read
against' foi identificada como um universal sem escopo definido, contradizendo a secao 2.4 (o bound de Song e para
next-location em resolucao grosseira, nao para category-F1/region-ranking). O texto foi reescopado para next-location,
com referencia cruzada (forward-ref) para a secao 2.4; a figura e o papel de 'learnable at all' foram mantidos. Ha um
fix de gate associado (B-5, 2026-07-24) e edicao de texto sugerida pela Persona 14 (APPROVE-WITH-EDIT).

**O que decidir:** O autor precisa confirmar se aceita o reescopo da afirmacao para next-location com o forward-ref a
secao 2.4 (mantendo figura e papel de 'learnable at all'), aceitar a edicao de texto proposta pela Persona 14, ou
preferir reverter para a formulacao original ('93% is the ceiling any model should be read against' sem escopo).

**Se ficar sem decisao:** A correcao do escopo do bound de 93% (contradicao entre secao 2.1 e secao 2.4) permanece sem a
aprovacao do autor, podendo publicar uma afirmacao ainda incorreta ou uma reformulacao nao revisada.

> **SUA DECISAO:** Deixa como está.

**RESOLVIDO (rodada 15).** Bloco reduzido a `[NEEDS SIGN-OFF 07 | CLOSED]` mais o motivo de nao generalizar: o bound de
Song e para next-location em resolucao grosseira, **nao** para category-F1 nem para ranking de regiao. Sem escopo, a
frase contradiz a §2.4.

---

### 8. [REMOVIDO rodada 15, 2026-08-04] Reancoragem do numero NUM-4: valores de Cat F1 (HGI)

**Local:** `src/chapters/2_fundamentals.tex:219` — renderiza no volume **defesa**, p. 20

**Contexto:** No marcador NUM-4 (round6, 2026-07-28), o numero foi RE-ANCORADO: a frase anterior dizia que "the category
F1 on Alabama, over five folds, rose monotonically from 0.74 to 0.82 across the swept values", citada de
research/embeddings/hgi/CLAUDE.md:117 (que ARREDONDA a tabela do sweep), sem spread, sem faixa de valores varridos e sem
epoch budget. Agora a citacao passa a ser da tabela em research/embeddings/hgi/README.md:544 (cabecalho "5 folds x 50
epochs") e :548-551: w_r 0.4 -> 0.7388 +/- 0.0205 | w_r 0.5 -> 0.7678 +/- 0.0211 | w_r 0.6 -> 0.7944 +/- 0.0186 | w_r
0.7 -> 0.8186 +/- 0.0123. A monotonicidade e palavra da propria fonte (CLAUDE.md:117; preprocess.py:38); o valor adotado
0.7 e o default do codigo (preprocess.py:23, DEFAULT_CROSS_REGION_WEIGHT = 0.7); e o w_r = 0.4 publicado, junto com o
objetivo de representacao de regiao, foi verificado no PDF do HGI, Eq. 2 ("wr is a factor to differentiate intra- (wr =

1) and cross-region (wr = 0.4) edges") e no abstract.

**O que decidir:** O bloco traz um [VERIFY] pendente: nenhuma das fontes (CLAUDE.md, README.md, preprocess.py, PDF)
nomeia a convencao de agregacao usada em "Cat F1" (macro-F1 ou media ponderada), por isso o texto usa "category F1" e
nao "macro-F1". O autor precisa confirmar essa convencao de agregacao ou, alternativamente, remover os dois valores
numericos e manter a frase apenas qualitativa (sem os numeros 0.74/0.82 ou os valores da tabela).

**Se ficar sem decisao:** Se ignorado, a dissertacao publica valores de "category F1" (0.7388, 0.7678, 0.7944, 0.8186,
ou a formulacao qualitativa) sem que a convencao de agregacao subjacente tenha sido confirmada pelo autor.

> **SUA DECISAO:** Esse bloco nem existe mais no texto, e outro criamos uma appendix para resolver esse problema esse
> need sing off (nso) pode ser removido do tex.

**REMOVIDO (rodada 15).** Confirmado antes de apagar: os valores que o bloco documentava (`0.7388`, `0.8186`, `0.74`,
`0.82`, `monotonic`, `w_r`) **nao aparecem em prosa viva** do `2_fundamentals.tex` -- so dentro de comentarios. O bloco
de 16 linhas saiu inteiro, junto com a flag `[VERIFY]` da convencao de media que ele carregava.

> **EFEITO COLATERAL QUE EU TIVE DE CONSERTAR:** outro comentario, no paragrafo do 0.7 (linha ~478), apontava para "the
> NUM-4 ledger earlier in this section" -- um ponteiro que passou a pendurar quando este bloco saiu. Reescrito no lugar:
> a
> regra que importava (**escrever "category F1" e nunca "macro-F1", porque nenhuma fonte nomeia a convencao de media**)
> agora esta declarada ali mesmo, sem depender do bloco removido.

---

### 9. [CLOSED rodada 15, 2026-08-04] Prosa da loss Check2HGI no Cap.2

**Local:** `src/chapters/2_fundamentals.tex:518` — renderiza no volume **defesa**, p. 23

**Contexto:** Foi adicionado um novo paragrafo com a loss do Check2HGI, termo que o documento ainda nao carregava em
nenhum lugar; o autor aprovou a inclusao. O trecho fica no Cap.2 porque e onde a dissertacao constroi a linha do infomax
(objetivo local-global do DGI, depois o hierarquico do HGI), tornando a quarta fronteira uma extensao natural de um
objetivo apresentado dois paragrafos antes, e antecede os dois capitulos que usam a representacao; o Cap.5 (§5.4.1), sob
revisao, descreve a mesma construcao em palavras para publico de artigo com limite de paginas, e uma equacao ali
exigiria alterar dois arquivos do texto submetido sem necessidade para aquele argumento. As tres equacoes de exibicao
foram transcritas, nao inventadas, de docs/context/check2hgi_overview.tex, secao "Funcao de Perda" (em portugues),
preservando simbolos, pesos, subscritos e o asterisco em L_*; os \underbrace foram descartados (conteudo movido para a
frase) assim como os rotulos em portugues do original. Os tres pesos (alpha_c2p=0.4, alpha_p2r=0.3, alpha_r2c=0.3) sao
os defaults do codigo em research/embeddings/check2hgi/model/Check2HGIModule.py:51-53, montados em :1192-1195, e
replicados em pipelines/embedding/check2hgi.pipe.py:43-45; os termos por fronteira estao em :1159, :1184, :1189, e o
discriminador (matmul, produto elementwise somado, torch.sigmoid) em :1003-1018, com comentario em :246. Dois fatos de
escopo: (1) e^- e "substituido de outro ponto do batch", caminho otimizado do source ("Corrupcao de Embeddings") e
comportamento padrao do codigo, sendo as equacoes indiferentes a forma de geracao de e^-; (2) os termos auxiliares
mencionados no Cap.5 (reconstrucao mascarada e ancora, pesos 0.3 e 0.1) NAO estao nesta equacao -- o source nao os
carrega e seus defaults no codigo sao 0.0 (Check2HGIModule.py:68, :178), habilitados por execucao -- portanto o texto
apresenta o objetivo de tres fronteiras como o source o declara, sem afirmar que e a loss de treinamento completa de
toda execucao do Cap.5. A dependencia de glossario foi RESOLVIDA em 2026-07-28: "bilinear discriminator" e "logistic
function" nao estavam no registro, o agente de redacao se recusou a autoauto­rizar os termos e marcou o paragrafo como
BLOCKED (comportamento pedido por GLOSSARY §1); ambos os termos agora estao registrados em §2 junto com a equacao que os
nomeia. A prosa usa "logistic function", nunca "sigmoid".

**O que decidir:** O autor precisa dar sign-off ordinario na redacao deste paragrafo (a dependencia de glossario ja foi
resolvida). Ha ainda um ponto marcado como [VERIFY] que nao foi estabelecido nesta sessao: se os dois termos auxiliares
citados no Cap.5 (reconstrucao mascarada e ancora, pesos 0.3 e 0.1) deveriam tambem ser nomeados aqui -- isso depende da
configuracao de execucao da representacao efetivamente utilizada (shipped representation), que precisa ser verificada
pelo autor.

**Se ficar sem decisao:** Uma prosa nova descrevendo a loss do Check2HGI -- incluindo equacoes, pesos e a questao aberta
sobre incluir ou nao os termos auxiliares do Cap.5 -- permanece publicada no Cap.2 sem a confirmacao final do autor.

> **SUA DECISAO:** O texto atual já mudou bastante em relação a esse texto referido. Mas, vamos deixar do jeito que está
> e sobre os detalhes de implementação do check2hgi criamos um novo appendix E, ainda não referenciamos ele aqui, pq
> precisamos do aval do meu professor sobre deixar ou não ele.

**RESOLVIDO (rodada 15).** Prosa mantida. O bloco de 33 linhas virou `[NEEDS SIGN-OFF 09 | CLOSED]` guardando o **fato
de escopo que faz a equacao estar certa apesar de parecer incompleta**: os dois termos auxiliares (reconstrucao
mascarada 0.3 e ancora 0.1) estao deliberadamente **fora** dela, porque a fonte nao os carrega e seus defaults no codigo
sao 0.0. Sem essa nota, alguem "completa" a equacao e introduz um erro.

Anotei ali tambem o que voce disse sobre o Apendice E: a loss completa de cinco termos esta documentada nele, ele
**ainda nao e referenciado por nenhum capitulo**, e isso aguarda o aval do seu professor. Registrado em
`PENDENCIAS.md 2.32`.

---

### 10. [CLOSED rodada 15, 2026-08-04] Prosa de enquadramento sobre linhagem MTLnet no Cap.2

**Local:** `src/chapters/2_fundamentals.tex:573`

**Contexto:** O item COD-013 (round6, 2026-07-28) registra nova prosa de enquadramento no Cap.2 explicando a
descendencia do joint model a partir de MTLnet -- fato antes carregado apenas pela ordem das linhas na tabela de
linhagem. A cadeia estabelecida a partir do codigo e MTLnet (mtlnet/model.py:39, classe base) -> MTLnetCrossAttn
(mtlnet_crossattn/model.py:207) -> MTLnetCrossAttnDualTower (mtlnet_crossattn_dualtower/model.py:42). O texto detalha
que MTLnetCrossAttn 'overrides exactly one component' (_build_shared_backbone, mtlnet_crossattn/model.py:362, docstring
em :368), substituindo o bloco FiLM + residual stack da base (mtlnet/model.py:193-197, construido a partir de :179) por
crossattn_blocks e duas LayerNorms; que herda encoders, heads e particao de parametros (docstring de classe :208-214;
accessors shared_parameters/task_specific_parameters/reg_specific_parameters em :554, :563, :578); e que cada stream
mantem pesos de feed-forward proprios (_CrossAttnBlock docstring :55-66, com :63 'Separate FFNs per task, no parameter
sharing'). A segunda especializacao (DualTower) muda apenas que a reg head recebe a sequencia bruta da regiao
pos-pad-mask (mtlnet_crossattn_dualtower/model.py:1-9 e :86-90). O trecho foi colocado no Cap.2 e nao no Cap.5 porque o
fato e sobre a RELACAO entre artefatos de dois capitulos -- e o que permite ler o resultado nulo do Cap.3 contra o
resultado positivo do Cap.5; dentro do artigo, o joint model e apresentado isoladamente. O id de registro foi omitido da
prosa deliberadamente, conforme WRITING_LAW §2. Nenhum numero e citado e nenhum resultado e reivindicado aqui; os dois
veredictos referenciados sao os que os Caps. 3 e 5 ja apresentam.

**O que decidir:** O autor precisa confirmar se esta nova prosa de enquadramento no Cap.2 -- que descreve a linhagem
MTLnet -> MTLnetCrossAttn -> MTLnetCrossAttnDualTower e a natureza das duas especializacoes, com base no codigo lido
nesta sessao -- esta correta e adequada para permitir a leitura cruzada entre o resultado nulo do Cap.3 e o resultado
positivo do Cap.5.

**Se ficar sem decisao:** Uma descricao tecnica da linhagem e das especializacoes do joint model, usada para justificar
a leitura conjunta dos resultados dos Caps. 3 e 5, permanece publicada sem a revisao e aprovacao do autor.

> **SUA DECISAO:** Essa descrição é critica e está em um bom caminho se queiser ter mais contexto para validar:
> articles/dissertacao/science/mtl_v17_complete_picture.md

**RESOLVIDO (rodada 15).** Prosa mantida. O bloco virou `[NEEDS SIGN-OFF 10 | CLOSED]` conservando a **cadeia de heranca
verificavel** (`MTLnet` -> `MTLnetCrossAttn` -> `MTLnetCrossAttnDualTower`, com arquivo e linha de cada classe) e o
motivo de estar no Cap.2 e nao no Cap.5: o fato e sobre a *relacao* entre artefatos de dois capitulos, e e o que
autoriza ler o resultado nulo do Cap.3 contra o positivo do Cap.5.

---

### 11. [CLOSED rodada 15, 2026-08-04] Limite de escopo do apendice de extensao por cosseno

**Local:** `src/chapters/2_fundamentals.tex:863` — renderiza no volume **defesa**, p. 9

**Contexto:** O apendice referenciado por \label{apx:cosine:extension} se autolimita a uma unica familia de arquitetura,
pois sua secao de mecanismo "applies only to models shaped like this one". Por isso, nada nesse trecho estende a leitura
ao modelo do Capitulo 3, que nunca foi medido. Alem disso, o hedge "part of the reason" e deliberado: o argumento de
representacao dos Capitulos 4 e 5 se apoia nos resultados desses proprios capitulos, e nao neste apendice.

**O que decidir:** O autor precisa confirmar que (1) a limitacao de escopo do apendice esta corretamente descrita, sem
sugerir extensao implicita ao modelo do Capitulo 3 (nunca medido), e (2) que o uso deliberado do hedge "part of the
reason" reflete corretamente que o argumento de representacao dos Capitulos 4 e 5 depende dos resultados desses
capitulos, e nao do apendice.

**Se ficar sem decisao:** Uma afirmacao sobre os limites de escopo do apendice e sobre a dependencia do argumento de
representacao permanece publicada sem a validacao do autor, com risco de sugerir indevidamente que o apendice cobre o
modelo do Capitulo 3.

> **SUA DECISAO:** Tanto o 1 quanto o 2, estão corretos!

**RESOLVIDO (rodada 15).** `[NEEDS SIGN-OFF 11 | CLOSED]`, guardando o limite de escopo que voce confirmou: o apendice
se restringe a uma familia de arquitetura, entao nada ali estende a leitura ao modelo do Cap.3, que nunca foi medido.

---

### 12. [CLOSED rodada 15, 2026-08-04] Repeticao da alegacao de mecanismo do apendice de cosseno no Cap.2

**Local:** `src/chapters/2_fundamentals.tex:863` — renderiza no volume **defesa**, p. 9

**Contexto:** Marcador levantado na rodada 9, em 2026-07-30, pelo AUTHOR: o paragrafo em
`src/chapters/2_fundamentals.tex:863` reafirma, no capitulo de enquadramento (Capitulo 2), a alegacao de mecanismo que
ja consta e ja esta sinalizada no Apendice F. Repeti-la no Capitulo 2 amplia sua audiencia, e segundo AGENT_GUARDRAILS
C2 uma alegacao conectiva sobre o que o arco demonstra ainda conta como alegacao.

**O que decidir:** E preciso decidir entre: (a) aprovar a alegacao do Apendice F, caso em que a repeticao no Capitulo 2
permanece valida; ou (b) rejeitar a alegacao do Apendice F, caso em que este paragrafo perde suas duas ultimas clausulas
e mantem apenas a definicao.

**Se ficar sem decisao:** A alegacao de mecanismo do Apendice F continua sendo repetida no Capitulo 2, com audiencia
ampliada, sem a aprovacao do autor.

> **SUA DECISAO:** Parece que esse ponto já não é mais valido vide que não citamos mais esse appendix F, e ser sincero
> acho que esse ponto ainda se refere ao appendix F que removemos dos appendix ou pode ser outro appendif que mudou de
> letra.

---

### 13. [CLOSED rodada 15, 2026-08-04] Remoção de duas definições de métricas e uma referência

**Local:** `src/chapters/2_fundamentals.tex:1220` — renderiza no volume **defesa**, p. 28

**Contexto:** No marcador COD-015d (round8, 2026-07-30), o autor indica que esta alteração estreita o escopo do capítulo
de fundamentos ao retirar duas definições de métricas, removendo junto uma referência da bibliografia. O texto não
especifica quais são as duas métricas nem qual é a referência retirada -- isso é ambíguo no trecho fornecido.

**O que decidir:** O autor precisa confirmar que concorda com a retirada das duas definições de métricas e da referência
bibliográfica associada, entendendo que ambas as métricas continuam disponíveis caso uma rodada de análise posterior
venha a reportá-las, e que nada mais no capítulo depende de nenhuma delas.

**Se ficar sem decisao:** Uma redução do escopo do capítulo de fundamentos, com a remoção de duas definições de métricas
e de uma referência da bibliografia, permanece sem a aprovação do autor.

> **SUA DECISAO:** Esse parece ser uma opção legada. Não tem amis uso.

---

### 14. [REMOVIDO rodada 15, 2026-08-04] Frase-charneira sobre imagem almoço/sábado, órfã (gate L3, A-2)

**Local:** `src/chapters/2_fundamentals.tex:1415` — renderiza no volume **defesa**, p. 30

**Contexto:** Marcador criado em 2026-07-23 (gate L3, fix A-2): a imagem "weekday lunch / Saturday night out" agora
aparece só no Cap.1 (beat de mecanismo já aprovado), e esta frase-charneira foi reformulada para expressar o mesmo
limite de vetor estático sem repetir a imagem. Em 2026-08-02 o bloco foi marcado como ORPHANED pela limpeza do autor: a
frase que ele anotava não está mais no texto, mas foi mantido, sem realocação de sentido, para revisão. Também há uma
nota de 2026-07-30 dizendo que o bloco foi movido para não mais dividir a frase entre "cannot be assumed;" e "it has to
be measured" (o comentário estava causando um alerta do check_trapped_prose por deixar uma linha começando no meio de
uma frase); o bloco agora fica entre frases completas.

**O que decidir:** É preciso confirmar duas coisas: (1) já que a frase original que este marcador anotava não existe
mais no texto (status ORPHANED, 2026-08-02), o autor deve simplesmente remover este marcador, ou ainda há algo релевante
para revisar? (2) Caso a reformulação da frase-charneira ainda esteja em algum ponto do texto atual, o autor prefere
mantê-la sem a imagem duplicada, ou revertê-la para repetir "weekday lunch / Saturday night out" como motivo deliberado,
conforme a opção original oferecida no bloco?

**Se ficar sem decisao:** A remoção da repetição da imagem "weekday lunch / Saturday night out" fora do Cap.1 (gate L3,
fix A-2) permanece sem confirmação do autor, e o bloco órfão pode continuar ocupando o texto sem que se saiba se ainda
há conteúdo relevante associado a ele.

> **SUA DECISAO:** remoção desse marcado.

---

## 3. CBIC

### 15. [CLOSED rodada 15, 2026-08-04] Remoção de vantagem arquitetural por misatribuição de referência

**Local:** `src/chapters/3_cbic/method.tex:207` — renderiza no volume **defesa**, p. 40

**Contexto:** Sign-off levantado na rodada 6 (2026-07-28) pelo AUTHOR: trata-se de uma mudança de afirmação (claim
change) na prosa publicada e coautorada, que remove uma vantagem declarada da arquitetura adotada neste capítulo -- indo
contra o interesse do próprio capítulo, a mesma propriedade já registrada em Appendix B para a Nash cost correction. O
bloco também afirma que o autor já teria aprovado essa rota 'em suas próprias palavras' na auditoria, mas essa alegação
não é verificável a partir do texto apresentado.

**O que decidir:** O autor precisa confirmar se concorda com a remoção do bullet que afirma a vantagem, em vez da
alternativa -- preservar o bullet e registrar o defeito no parágrafo de preservação de Appendix B -- que foi descartada
por ser considerada mais cara e por não se encaixar nos motivos que justificam os dois elementos atualmente preservados
(um indexado no tempo pelo prefácio do capítulo, outro por convenção de tabela). O texto não especifica qual
bullet/afirmação nem qual artigo estão em jogo -- isso é ambíguo e também precisa ser esclarecido/confirmado pelo autor,
assim como a suposta aprovação prévia mencionada no bloco.

**Se ficar sem decisao:** uma remoção de conteúdo (vantagem declarada) em prosa publicada e coautorada -- junto com a
alegação de aprovação prévia do autor citada no bloco -- permanece sem a confirmação explícita dele.

> **SUA DECISAO:** Re-leia essa parte e valide se há algo relacionado com essa afirmação problematica, se ela ainda
> estiver ali fazemos algo quanto a ela.

**RE-LIDO E RESOLVIDO (rodada 15). A afirmacao problematica NAO esta mais la, e o tratamento e melhor do que uma
remocao.** Voce pediu para eu reler e agir se ela ainda estivesse presente. Estado atual, verificado em prosa viva
(`3_cbic/method.tex:119-129`):

- o bullet afirma **apenas a metade que a citacao sustenta** -- custo de *inferencia* reduzido, uma rede avaliada em vez
  de uma por tarefa;
- a frase publicada esta **reproduzida palavra por palavra em nota de rodape** logo abaixo, com a correcao declarada.
  Nada foi silenciosamente descartado;
- a linha de errata existe (`tables/cbic/errata.tex:96`).

Ou seja: o leitor ve o que foi publicado, o que passou a valer, e por que. O bloco de 75 linhas virou
`[NEEDS SIGN-OFF 15 | CLOSED]` guardando **por que a correcao era necessaria** (o bullet citava arXiv:1905.07553 para o
*inverso* do que o artigo conclui: ele nomeia acuracia melhor e tempo de treino menor apenas como beneficios "em
teoria", e depois argumenta empiricamente o contrario) e **o limite honesto**: o LaTeX do CBIC entrou no controle de
versao em 2025-10-21, *depois* da publicacao, entao rascunhos pre-submissao nao estao neste repositorio e a pergunta de
quando a redacao surgiu nao pode ser respondida daqui. O que se estabelece e mais estreito: nenhuma substituicao ocorreu
depois disso.

---

### 16. [CLOSED rodada 15, 2026-08-04] Detalhe de protocolo e a frase sobre busca de hiperparametros

**Local:** `src/chapters/3_cbic/results.tex:111` — renderiza no volume **defesa**, p. 10

**Contexto:** No round 6 (2026-07-28), foram adicionadas quatro frases de novo detalhe de protocolo a um capitulo ja
publicado. Segundo o autor da nota, todo fato foi recuperado do codigo liberado e nomeado no texto, e nada sobre um
'tuning budget' foi afirmado, conforme instrucao previa.

**O que decidir:** Confirmar se deseja explicitar a lacuna sobre busca de hiperparametros. Caso sim, a formulacao mais
forte sustentada pela evidencia disponivel seria: "No systematic hyperparameter search was performed; the reported
configuration of each model is a single configuration arrived at during development" -- que e uma afirmacao sobre a
conducao do estudo, e nao um registro recuperado do codigo, e que NAO foi adicionada pelo autor da nota.

**Se ficar sem decisao:** A decisao sobre incluir ou nao a frase explicita sobre a ausencia de busca sistematica de
hiperparametros permanece sem sua aprovacao, deixando o capitulo publicado silencioso sobre esse ponto sem confirmacao
sua.

> **SUA DECISAO:** Não precisamos comentar nada.

**RESOLVIDO (rodada 15).** A lacuna sobre busca de hiperparametros fica **sem mencao** -- nao adicionei frase alguma. A
formulacao mais forte que a evidencia sustentaria seria uma afirmacao sobre a *conducao*
do estudo, nao um registro recuperado do codigo, e portanto nao e nossa para afirmar. Registrado no marcador para que
ninguem a adicione depois "por completude".

O bloco tambem sinalizava uma consequencia em outro arquivo, e **ela ja foi aplicada**: o
`2_fundamentals.tex` nao diz mais que o Cap.3 reporta validacao cruzada "without identifying the split axis"; hoje
declara que os Caps. 3 e 4 estratificam por amostra, de modo que os check-ins de um usuario podem aparecer em treino e
validacao. Conferido em 2026-08-04.

---

### 17. [CLOSED rodada 15, 2026-08-04] Ambiguidade em frase reescrita sobre COD-016a

**Local:** `src/chapters/3_cbic/results.tex:153` — renderiza no volume **defesa**, p. 44

**Contexto:** A frase publicada e co-autorada foi reescrita para maior clareza. O revisor propos a leitura de que "each
model leads in some categories, so the other appears worse in those" (cada modelo lidera em algumas categorias, entao o
outro parece pior nelas), mas aponta que ha uma leitura alternativa possivel: a frase original poderia estar se
referindo, em vez disso, ao desbalanceamento da distribuicao das categorias (a classe Food dominando os dados).

**O que decidir:** Confirme se a interpretacao correta da frase original e (a) sobre a divisao das lideranças entre os
dois modelos (cada modelo lidera em algumas categorias, fazendo o outro parecer pior nelas), ou (b) sobre o
desbalanceamento da distribuicao de categorias (dominancia da classe Food). Essas sao duas afirmacoes diferentes e
apenas o autor e os coautores podem definir qual foi efetivamente escrita.

**Se ficar sem decisao:** Uma reformulacao de prosa publicada e a linha de errata correspondente permanecem sem
confirmacao do autor sobre qual das duas afirmacoes (COD-016a) e a correta.

> **SUA DECISAO:** This is done in the pendencias_resolvidas.md

**RESOLVIDO (rodada 15).** Leitura confirmada pelo registro que voce aponta (`PENDENCIAS_RESOLVIDOS 5.3`):
a frase e sobre **a divisao das liderancas entre os dois modelos** (a comparacao por categoria parecer pior que o
agregado), **nao** sobre o desbalanceamento da distribuicao de categorias. Eram duas afirmacoes diferentes; esta e a que
foi escrita.

O marcador guarda o que impede alguem de achar que a frase foi fortalecida: a redacao publicada esta citada
literalmente, nenhum numero ou celula de tabela mudou, e o hedge continua "could", nao "does".

---

## 4. CoUrb

### 18. [CLOSED rodada 15, 2026-08-04] Frase adicionada no preface sobre resultado coautorado

**Local:** `src/chapters/4_courb.tex:55`

**Contexto:** No preface de um capitulo JA PUBLICADO, foi adicionada uma frase (levantado na rodada 6, em 2026-07-28). O
preface e prosa FRAME escrita para a dissertacao, nao texto de artigo traduzido, portanto nao gera custo de errata --
mas a frase funciona como um ponteiro publico para uma afirmacao sobre um resultado coautorado. O coautor ja foi
notificado (2026-07-27); a conversa com o orientador ainda esta pendente.

**O que decidir:** O autor precisa revisar e confirmar (assinar) a frase adicionada no preface, dado que ela aponta
publicamente para uma afirmacao sobre um resultado coautorado; alem disso, a conversa com o orientador sobre esse ponto
ainda precisa ocorrer antes que o marcador possa ser removido.

**Se ficar sem decisao:** Uma frase publicada que aponta para uma afirmacao sobre um resultado coautorado permanece sem
a aprovacao do autor e sem o sign-off do orientador.

> **SUA DECISAO:** Já revisei é está tudo certo!

**RESOLVIDO (rodada 15).** `[NEEDS SIGN-OFF 18 | CLOSED]`. Registrei no marcador um fato que mudou desde que o item foi
escrito: **o ponteiro para "Appendix B of the supplementary volume" nao existe mais** -- a regra standalone da rodada 14
removeu ponteiros ao volume suplementar de todos os capitulos, e o achado de escopo que ele indicava esta hoje declarado
como prosa na propria preface. Conferido: zero
`\extravolume` e zero "Appendix B" em prosa viva do `4_courb.tex`. Nao re-adicione um ponteiro; declare o fato.

---

### 19. [CLOSED rodada 15, 2026-08-04] Narrowing de claim em prosa publicada (Cap. 4)

**Local:** `src/chapters/4_courb/methodology.tex:81` — renderiza no volume **defesa**, p. 10

**Contexto:** Marcador levantado na rodada 6 (2026-07-28) pelo AUTHOR sobre um narrowing de claim em prosa co-autorada
ja publicada, no Capitulo 4 (capitulo traduzido). O dispositivo alternativo ja usado nesta colecao -- reproduzir a frase
e externalizar a correcao em nota de rodape, como feito em 3_cbic.tex para o Nash cost claim -- estava disponivel mas
nao foi escolhido; o autor do bloco optou por uma clausula no corpo do texto, justificando que o Capitulo 4 ja tem
muitos parenteticos e que a clausula e mais barata para o leitor do que uma nota de rodape.

**O que decidir:** O autor precisa confirmar se mantem o narrowing do claim como clausula no corpo do texto (opcao
escolhida pelo redator do bloco) ou se prefere converte-lo para o dispositivo alternativo -- reproduzir a frase original
e externalizar a correcao em nota de rodape, seguindo o precedente de 3_cbic.tex (Nash cost claim). O bloco indica: 'Say
the word and I will convert it', ou seja, a conversao para nota de rodape so ocorre se o autor autorizar.

**Se ficar sem decisao:** Um narrowing de claim em prosa co-autorada ja publicada permanece incorporado ao Capitulo 4
sem a aprovacao do autor sobre a forma (clausula vs. nota de rodape) escolhida para apresenta-lo.

> **SUA DECISAO:** Deixe do jeito que está

**RESOLVIDO (rodada 15).** O narrowing permanece como clausula no corpo; **nao** converti para nota de rodape. Sua razao
esta registrada no marcador: o Cap.4 ja carrega muitos parenteticos e uma clausula custa menos ao leitor do que uma
nota.

A dependencia de glossario que o bloco levantava esta **resolvida**: `Pareto-stationary point` foi registrado no
`GLOSSARY.md` (linha em ingles e a forma PT `ponto Pareto-estacionario`) em 2026-07-30.

---

### 20. [CLOSED rodada 15, 2026-08-04] Frase sobre seed/StratifiedKFold no Cap. 4, removida por voce

**Local:** `src/chapters/4_courb/results.tex:42` — renderiza no volume **defesa**, p. 58

**Contexto:** No round 6 (2026-07-28) foi levantado um sign-off pendente do AUTHOR para uma nova frase de detalhe de
protocolo, adicionada a um capitulo ja publicado e recuperada do codigo liberado; nenhum numero ou afirmacao de
resultado e afetado. Trata-se de uma adicao declarada (round4, REV-012), da mesma classe da frase sobre eixo dividido
(split-axis) adicionada anteriormente no Apendice B / secao do Capitulo 4. O codigo verificado nesta sessao (base
CoUrb-era em /Users/vitor/Desktop/mestrado/temp/tarik-new, repositorio TarikSalles/Spatial_Embeddings, commit 58fd219b,
branch main, arquivo PoiMtlNet_Novo/src/etl/mtl/create_fold.py) mostra: linha :162 create_folds (..., random_state:
int = 42, ...) como valor padrao, chamado sem sobrescrita em pipelines/mtlnet_trainer.py:49-55; linha :180
torch.manual_seed (random_state); linha :181 np.random.seed (random_state); linha :226 next_skf = StratifiedKFold
(n_splits=k_splits, shuffle=True, random_state=random_state); linha :229 place_skf = StratifiedKFold (n_splits=k_splits,
shuffle=True, random_state=random_state). Ambos os splitters sao StratifiedKFold simples, sem argumento groups=, o que
tambem sustenta o fato de estratificacao por amostra citado na frase anterior. Os numeros de linha se mantem no arquivo
commitado (git show HEAD:...: :159, :177, :178, :223, :226). Nao se afirma que os experimentos publicados foram
produzidos exatamente por este arquivo; o valor literal 42 foi deliberadamente omitido da prosa, pois e um fato do
codigo, e nao um parametro experimental relatado no artigo publicado.

**O que decidir:** O autor precisa confirmar se aprova a inclusao desta nova frase de detalhe de protocolo (sobre
StratifiedKFold sem groups= e sobre o random_state/seed padrao=42, embora o valor 42 nao apareca na prosa) no Capitulo
4, dado que ela foi recuperada do codigo (commit 58fd219b) e nao fazia parte do texto publicado original, e se a
formulacao cautelosa -- que nao afirma que esse codigo exatamente gerou os experimentos publicados -- esta adequada.

**Se ficar sem decisao:** Uma frase de detalhe de protocolo inserida no Capitulo 4, baseada em codigo recuperado (commit
58fd219b) e nao no texto originalmente publicado, permanece sem a aprovacao do autor.

> **SUA DECISAO:** Eu removi essa frase para deixar o texto mais semelhante ao original, além de que já falamos sobre
> isso no preambulo. Pf remova esse entrada do appendix B do extra content.

**RESOLVIDO (rodada 15) -- e a sua remocao foi maior do que o item descrevia, o que mudou o conserto.**

Voce removeu a frase do `4_courb/results.tex` (trabalho **nao commitado** na arvore: `git diff` contra o HEAD mostra a
remocao). Ela nao carregava um fato, e sim **tres**, num unico grupo de frases:

1. o split e estratificado por amostra, nao por usuario;
2. o codigo de referencia fixa uma unica semente, logo os cinco folds sao uma repeticao e os desvios reportados sao a
   dispersao entre folds naquela semente;
3. o treino roda o numero configurado de epocas sem early stopping, com cada tarefa lida na epoca de maior macro-F1 de
   validacao.

**O que fiz no Apendice B** (`chapters/apx_b_errata.tex`), no paragrafo de adicoes do Cap.4: retirei **os tres** fatos
de protocolo, nao so o da semente. O paragrafo agora diz que o capitulo nao declara fato de protocolo alem dos que o
artigo publicado reporta, e aponta que a estratificacao por amostra e declarada **na preface** -- que e exatamente o que
voce disse ("ja falamos sobre isso no preambulo"), e conferi que esta la (`4_courb.tex:42`).

> **DOIS ACHADOS QUE A SUA REMOCAO PRODUZIU, e que eu consertei em vez de deixar passar:**
>
> **(a) O paragrafo irmao do CBIC ficou com uma referencia pendurada.** Ele afirmava que o ultimo dos
> seus quatro fatos de protocolo "e redigido exatamente como no Capitulo 4, cujo estudo roda o mesmo
> codigo". Essa frase **nao existe mais no Cap.4**, entao a comparacao apontava para o vazio. Removi a
> clausula; os quatro fatos do CBIC permanecem intactos, porque o Cap.3 **continua** carregando-os
> (conferido: linhas 191-194 do apendice sao as do CBIC, corretamente preservadas).
>
> **(b) Nao afirmei uma contagem que nao consigo verificar.** O paragrafo dizia "nove adicoes marcadas".
> Com tres fatos fora, o numero mudaria para seis -- mas o capitulo **nao marca adicoes com nenhum
> token contavel** no fonte (procurei: zero ocorrencias de `ADDITION`/`declared as an addition`), entao
> eu nao teria como conferir nem "nove" nem "seis". Escrevi "adicoes marcadas" sem numero. Esse
> apendice ja foi mordido por contagem errada antes (o episodio 59-vs-54 esta registrado nele mesmo), e
> repetir o padrao seria pior do que perder o numero.

**Pendencia sua, nao minha:** a remocao da frase segue **nao commitada**. Eu commitei apenas as minhas edicoes de
comentario e do apendice; a sua alteracao de prosa continua na arvore de trabalho para voce revisar e commitar.

---

## 5. MobiWac

### 21. [REMOVIDO rodada 15, 2026-08-05] Texto de abertura (time-capsule preface) novo no Cap. 5

**Local:** `src/chapters/5_mobiwac.tex:25` — renderiza no volume **defesa**, p. 32

**Contexto:** Foi adicionado um texto de abertura ('frame text') inedito para o capitulo, marcado como 'raised v1
assembly, 2026-07-23'. Trata-se do preface tipo time-capsule exigido pelo NORTH_STAR (secao 3/secao 4, Cap.5), e as
afirmacoes nele contidas foram extraidas da spine aprovada e da lista de afirmacoes permitidas do artigo (PAPER_PLAN
secao 3).

**O que decidir:** O autor precisa confirmar se o novo texto de abertura do Capitulo 5 e as afirmacoes que ele contem
estao corretos e conformes ao que foi definido no NORTH_STAR (secao 3/secao 4) e ao claim whitelist do PAPER_PLAN (secao
3), para que o marcador de sign-off possa ser removido.

**Se ficar sem decisao:** O novo texto de abertura do Capitulo 5, incluindo as afirmacoes nele baseadas na spine
aprovada e no claim whitelist, permanece publicado sem a validacao do autor.

> **SUA DECISAO:** Tudo certo podemos deixar e remover esse marcador por completo.

**REMOVIDO (rodada 15).** Marcador apagado do `5_mobiwac.tex`. A preface e prosa de enquadramento escrita para a dissertacao, nao texto traduzido do artigo, entao nao carrega custo de paridade nem linha de errata.

---

### 22. [REMOVIDO rodada 15, 2026-08-05]

> **LEIA ISTO PRIMEIRO E PULE O RESTO DO ITEM.** A pergunta deste item era *onde* colocar o ponteiro
> para o apendice de cosseno de gradientes: no paragrafo de abertura da secao (prosa da dissertacao) ou
> na frase mantida identica ao artigo. **Nao existe mais ponteiro nenhum para posicionar.** Ele foi
> removido na rodada 14, quando voce estabeleceu que os corpos dos artigos dos capitulos 3-5 devem ser
> textos autonomos e nao podem citar apendices ou secoes da dissertacao (`PENDENCIAS.md §2.31`, probes
> `STL-01`..`STL-05`, commit `2bb82234`).
>
> Medido em 2026-08-04, nao inferido:
>
> ```bash
> cd articles/dissertacao/src
> grep -v '^[[:space:]]*%' chapters/5_mobiwac/02_related.tex | grep -c "gradient-cosine"   # 0
> ```
>
> O PDF de defesa tambem nao contem a string `gradient-cosine` em pagina nenhuma. A decisao registrada
> no round9f (`PENDENCIAS_RESOLVIDOS 2.9`) nao foi revertida — ela foi **superada** por uma regra
> posterior e mais ampla, que sua propria instrucao criou.
>
> **Acao: nenhuma sua.** O bloco de comentario correspondente no `.tex` pode ser removido sem perda,
> porque a decisao que ele registrava ja nao tem objeto. O assunto residual — *o Apendice E nao e
> citado por capitulo nenhum, e um leitor so chega nele por acidente* — e uma pergunta diferente e esta
> registrada onde voce a vera: **`PENDENCIAS.md §2.32`**, com tres colocacoes possiveis e o custo de
> cada uma.

**Registro historico do item, mantido apenas para rastreabilidade:**

**Local (na epoca):** `src/chapters/5_mobiwac/02_related.tex:14` — renderizava no volume **defesa**, p. 65

**Contexto:** Trata-se de uma nova subseção de recapitulação para o Cap.5, exigida pela NORTH_STAR seção 3 (o Cap.5
recapitula tanto o artefato do Cap.3 quanto o achado do Cap.4); o conteúdo vem da espinha dorsal aprovada (NORTH_STAR
seções 2 e 6) e da tabela de linhagem de modelos do GLOSSARY, sem citar números. Marcador levantado na v1 assembly
(2026-07-23). Uma AUTHOR DECISION (round9f, 2026-08-02, PENDENCIAS_RESOLVIDOS 2.9, arquivado em 2026-08-02) já registra
que o apontamento para o apêndice de gradient-cosine deve ficar no parágrafo de abertura da seção, e não na frase sobre
gradient-cosine mais abaixo -- pois essa frase é mantida byte-a-byte idêntica ao artigo [mobiwac] (que não tem apêndice
e cujo leitor pode não ter a dissertação em mãos), tendo sido reescrita para se sustentar por conta própria. O parágrafo
de abertura é prosa exclusiva da dissertação e já usa \ref para os Capítulos 3 e 4, o que torna um \ref interno adequado
nele.

**O que decidir:** Confirmar se a decisão já registrada (AUTHOR DECISION, round9f, PENDENCIAS_RESOLVIDOS 2.9) de colocar
o apontamento ao apêndice de gradient-cosine no parágrafo de abertura da seção -- e não na frase mantida idêntica ao
artigo [mobiwac] -- permanece válida, permitindo remover este marcador.

**Se ficar sem decisao:** A colocação do apontamento para o apêndice de gradient-cosine no parágrafo de abertura, em vez
da frase idêntica ao artigo [mobiwac], permanece sem confirmação final do autor.

> **SUA DECISAO:**

---

### 23. [REMOVIDO rodada 15, 2026-08-05] Confirmar novos numeros no capitulo (related work)

**Local:** `src/chapters/5_mobiwac/02_related.tex:243` — renderiza no volume **defesa**, p. 4

**Contexto:** Em src/chapters/5_mobiwac/02_related.tex:243, o marcador foi levantado na rodada 5 (2026-07-27) apontando
que os valores "nineteen", "+0.68" e "+0.19" sao numeros novos introduzidos no capitulo.

**O que decidir:** O autor precisa confirmar se os valores "nineteen", "+0.68" e "+0.19" estao corretos e sao
consistentes com os dados/resultados que fundamentam o capitulo, para que o marcador possa ser removido.

**Se ficar sem decisao:** Numeros novos ("nineteen", "+0.68", "+0.19") inseridos no capitulo permanecem sem verificacao
do autor quanto a sua exatidao.

> **SUA DECISAO:** i have rewrite the text and now is all clean you can remove this NOS from the tex.

**REMOVIDO (rodada 15).** Conferido antes de apagar: os tres numeros continuam **vivos** na prosa
(`02_related.tex:138,142` -- "nineteen", `0.68`, `0.19`), entao o marcador saiu sem levar conteudo junto.

Mantive o bloco de comentario logo acima porque ele registra uma **auto-contradicao ja corrigida**: uma
versao anterior afirmava que `scale_norm` tambem ficava acima em ambos os datasets, contradizendo o
proprio quadro que listava. O bloco guarda as quatro celulas medidas para que ninguem re-levante isso.

> Efeito colateral que consertei: a remocao do marcador deixou o comentario terminando em frase completa
> colada na prosa, e o gate `check_trapped_prose` acusou (`make check` rc=2). Reescrito para terminar em
> fragmento, seguindo a convencao dos outros blocos do repo.

---

### 24. [CLOSED rodada 15, 2026-08-05] Sign-off pendente: dois pointer targets no capitulo em revisao

**Local:** `src/chapters/5_mobiwac/05_setup.tex:122` — renderiza no volume **defesa**, p. 11

**Contexto:** Marcador levantado na rodada 7 (2026-07-29), referente a dois pointer targets no corpo de um capitulo que
esta em under-review. A alteracao foi autorizada in-session, mas ainda depende de revisao do autor.

**O que decidir:** O autor precisa reler o paragrafo renderizado com os dois pointer targets e confirmar se esta
correto; alem disso, precisa confirmar se sera criada uma entrada em ERRATA.md em articles/[mobiwac]/ caso esse
paragrafo venha a entrar no manuscrito.

**Se ficar sem decisao:** O paragrafo com os dois pointer targets permanece sem a releitura de aprovacao do autor, e a
entrada correspondente em ERRATA.md em articles/[mobiwac]/ pode nao ser criada caso o paragrafo entre no manuscrito.

> **SUA DECISAO:** Vamos fazer uma nova anlise sobre essa frase com os conhecimentos que temos e coms as analises que
> froma fetias desde lá, inclusive essa frase não está no artigo original. But I don't want to mention in anywhere in
> the artcile the change of leak we are disprove it and this kind of text can cause confusion in the reader. If they ask
> i already have the data.

**RESOLVIDO (rodada 15).** As duas clausulas que mencionavam o episodio de leak foram **removidas**, e
nenhuma linha de errata e devida: medi antes de cortar, e as duas sao **exclusivas da dissertacao** --
zero ocorrencias de "leaked under a downstream sequence model" em `[mobiwac]/src/sections/05_setup.tex`
(o manuscrito diz "on three grounds", este capitulo diz "on four grounds", entao o paragrafo nao tem
contraparte no texto submetido).

**Nenhum corte enfraquece uma alegacao.** Em ambos os casos o episodio era so a *razao* de um ponto
metodologico, e cada ponto continua de pe por conta propria:

- a excecao do candidato unico continua dizendo que nao e contra-exemplo, agora porque a triagem limita
  candidatos entre si e nao contra um padrao absoluto;
- os limites da sonda continuam dizendo que a forma linear e uma triagem e nao uma prova, agora
  argumentado pelo que uma leitura linear consegue expor.

Como voce pediu: o dado continua existindo se um revisor perguntar; o texto nao o menciona.

---

### 25. [CLOSED rodada 15, 2026-08-05] Restauracao da figura fig3_embquality no capitulo MobiWac

**Local:** `src/chapters/5_mobiwac/06_results.tex:44`

**Contexto:** Este bloco marca a revisao v1 assembly de 2026-07-23, que restaura um elemento (figura) cortado do build
de 8 paginas do MobiWac por decisao do autor de 2026-07-09; os quatro numeros dessa figura ja estao integralmente
declarados na prosa acima. A restauracao ocorre porque a dissertacao nao tem limite de paginas, com legenda verbatim
retirada de articles/[mobiwac]/src/figs/fig3_embquality.tex. A frase de referencia (pointer sentence) abaixo faz parte
do mesmo bloco restaurado -- inserida por um ajuste do gate L4, que exige que todo float seja referenciado na prosa -- e
deve ser removida junto se o bloco for removido.

**O que decidir:** O autor precisa decidir: manter a figura restaurada (junto com a pointer sentence associada) na
dissertacao, aproveitando a ausencia de limite de paginas; ou remover este bloco (figura + pointer sentence) para que o
capitulo corresponda exatamente ao artigo submetido, ja que os quatro numeros da figura ja aparecem na prosa.

**Se ficar sem decisao:** A restauracao da figura fig3_embquality e a fidelidade de sua legenda verbatim, junto com a
insercao da pointer sentence do gate L4, permanecem sem confirmacao do autor sobre se devem constar na versao final da
dissertacao.

> **SUA DECISAO:** We can keep it, but the phrase is loose we need to ref the fig in some part of the previus text so

**RESOLVIDO (rodada 15).** Figura mantida. A frase de ponteiro era literalmente uma linha solta apos a
tabela ("Figure X shows the same separability contrast graphically"); agora ela **diz ao leitor o que a
figura acrescenta** sobre a prosa: as duas medidas lado a lado, para que o tamanho do vao seja lido de
relance em vez de comparado entre quatro numeros no corpo do texto.

> **O que eu NAO fiz, de proposito.** Voce sugeriu refatorar o texto anterior para discutir apontando
> para a figura em vez de citar os numeros em prosa. Essa frase e **reproduzida do artigo submetido**
> (conferido em `[mobiwac]/src/sections/06_results.tex`), entao reestrutura-la seria edicao com custo de
> paridade e linha de errata, sem ganho para o leitor. So a frase de ponteiro, que e exclusiva da
> dissertacao, mudou.
> have more context. Maybe even refector the previus text that instead discc this numbers in prose we can disccus and
> point for the figure.

---

### 26. [CLOSED rodada 15, 2026-08-05] Uso do termo 'cell' em resultado de tabela

**Local:** `src/chapters/5_mobiwac/06_results.tex:232` — renderiza no volume **defesa**, p. 78

**Contexto:** Marcador levantado na round 5 (2026-07-27, AUTHOR; round5, persona 03 S3-02): o termo "cell" para um
resultado de tabela e classificado como verdict *never* em articles/[mobiwac]/GLOSSARY.md §3, pois esse publico le
"cell" como 'radio cell'; o §5.1 deste capitulo torna essa colisao explicita. Duas afirmacoes proprias usavam "cell" e
ambas foram substituidas ("entries", "result"). Os usos de "grid cell" e de radio-cell em outros pontos permanecem
intocados, pois estao corretos: escrevem o sentido de grid por extenso, e dois deles descrevem o alvo de outro trabalho,
nao o nosso.

**O que decidir:** Confirmar se as substituicoes ja feitas ("entries" e "result") sao aceitaveis para as duas
ocorrencias proprias de "cell" apontadas neste marcador, e validar que nenhum outro uso de "cell"/"grid cell"/radio-cell
no capitulo precisa ser revisto.

**Se ficar sem decisao:** As duas substituicoes de terminologia ("entries", "result") no lugar de "cell" permanecem sem
a aprovacao do autor da dissertacao.

> **SUA DECISAO:** Tudo ok, mudamos isso no texto original também ?

**RESOLVIDO (rodada 15) -- e a resposta a sua pergunta e SIM.** Conferido em 2026-08-04: **zero**
ocorrencias de qualquer forma de "cell" na prosa viva **tanto** deste capitulo **quanto** do artigo
submetido (`[mobiwac]/src/sections/06_results.tex`). Os dois textos estao consistentes e nenhuma linha de
errata e devida.

O marcador guarda o motivo do banimento para que a palavra nao volte: "cell" para resultado de tabela e
verdito *never* no `[mobiwac]/GLOSSARY.md §3` ("this audience reads 'cell' as a radio cell"), e a §5.1
deste capitulo torna a colisao explicita. Os usos de "grid cell" e de radio-cell em outros pontos
permanecem intactos e corretos.

---

### 27. [CLOSED rodada 15, 2026-08-05] Sign-off: reescrita de interpretação e null result do F50 (Ch.5)

**Local:** `src/chapters/5_mobiwac/06_results.tex:255` — renderiza no volume **defesa**, p. 78

**Contexto:** O bloco NEEDS SIGN-OFF (round 4, 2026-07-26, AUTHOR) trata de dois pontos: (1) o Cap.5 é texto
PUBLISHED-adjacent sob o regime de errata, e a reescrita de uma frase de interpretação exige uma linha no Apêndice B
ainda não escrita, pendente de decisão sobre a redação; (2) o braço F50 é um development record só em FL, e a persona 10
também aponta CSLSL_CASCADE.md:19 (o cascade rompe o canal simétrico e ainda empata dentro de 0.02 pp) na mesma direção,
contra a afirmação de 'a stronger shared trunk' como resultado assentado. O NEW-2 (2026-07-26), com base em
docs/studies/closing_data/archive/findings/W6_ENCODER_ISOLATION.md, mostra que os deltas probe cat vs dedicated (+7.63
AL, +6.54 AZ, +4.64 FL) são medidos contra a coluna 'STL cat ceiling' (55.87/57.13/75.15) do Table 2 check-in-level, e
não contra as células Dedicated do Table 3 (56.82/56.43/74.51); também nota que 'within 0.3 of the joint model' foi
medido contra o comparando full-MTL cat (S1) (63.56/63.39/79.82), convenção DIAGNOSTIC-BEST, e não contra as células
JOINT-BEST do Table 3 (64.51/65.79/79.84).

**O que decidir:** O autor precisa: (1) decidir a redação da linha do Apêndice B para a reescrita da frase de
interpretação do Cap.5 sob o regime de errata; e (2), quanto ao achado nulo do F50/CSLSL_CASCADE.md:19, escolher entre
(a) citar o empate do cascade em vez do F50, ou (b) rodar a ablação de cross-attention nos outros datasets antes de
divulgar -- ficando estabelecido que a frase 'a stronger shared trunk' não pode permanecer como resultado assentado.

**Se ficar sem decisao:** Sem essa decisão, a reescrita da interpretação do Cap.5 fica sem a linha correspondente no
Apêndice B e a afirmação de 'a stronger shared trunk' permanece como se fosse resultado assentado, mesmo com o
repositório contendo um teste direto desse componente (F50/CSLSL_CASCADE.md:19) com resultado nulo, sem revisão do
autor.

> **SUA DECISAO:** Hum, eu acho que em uma avaliação previa já resolvemos esse ponto, valide pf como está o texto hoje e
> se há algo que eu tenha que decidir. Se necssario lance um agent para revalidar os estudo que fizemos e como vamos
> consolidar essa frase. Temos que tomar duidado pois ela é parte central da nossa defesa. Não podemos deixar ela vaga e
> incompleta.

**RE-VALIDADO (rodada 15), com agente dedicado, e o resultado muda a resposta.** Voce pediu para eu
validar como o texto esta hoje e, se preciso, lancar um agente para revalidar os estudos. Fiz as duas
coisas. Relatorio completo em `src_utils/_history/handoff/ch5_mechanism_evidence.md`.

**O paragrafo de hoje esta CORRETO e nao deve ser fortalecido.** Quatro experimentos independentes
convergem, e nenhum autoriza nomear o *shared trunk* como fonte do ganho de categoria:

| estudo | o que testa | resultado |
|---|---|---|
| F50 | cross-attention ON vs OFF (FL) | `68.36±0.74` vs `68.32±0.67`, Δ `−0.04±0.13`, Wilcoxon pareado p=0.6250 |
| F52 | zera a saida do mixing | empata com a referencia (+0.30, p=0.81) |
| F53 | varre o peso da perda de categoria | identico em todos os valores; hipotese "cross-attn dormente" **refutada** |
| CSLSL cascade | **remove o trunk** | Δcat `+0.20` AL, `+0.20` AZ, `+0.01` FL, `−0.20` Istanbul |

**Sua objecao tecnica foi verificada, e ela reforca o achado em vez de enfraquece-lo.** Voce levantou que
no cascade o experimento talvez ainda passasse pelo shared trunk. Fui ao codigo: o forward guarda o laco
com `if not self._disable_cross_attn:` (`mtlnet_crossattn_dualtower/model.py:64-70` e `:149`), e o proprio
`CSLSL_CASCADE.md:60-70` registra instrumentacao em runtime -- os dois blocos de cross-attention foram
chamados **0 vezes** com a flag ligada, contra 2 vezes sem ela. O que resta no caminho sao apenas os
`LayerNorm` finais **por stream** (`cat_final_ln`, `next_final_ln`), que nao trocam informacao entre
tarefas. O trunk e de fato removido -- e o ganho sobrevive.

**A ARMADILHA, registrada no `.tex` para ninguem re-derivar a resposta errada.** O `W6_ENCODER_ISOLATION.md`
tem como titulo "the joint CATEGORY win is the shared TRUNK", e esse titulo **exagera o proprio desenho**:
congelar a stream de regiao remove o *treino* da regiao, entao nao separa o trunk do encoder proprio da
categoria, das FFNs por stream, nem da profundidade extra. O `W6:15` admite isso. **O Capitulo 5 esta mais
honesto que o documento que gerou a frase** -- nao "corrija" o capitulo em direcao a esse titulo.

---

### 28. [CLOSED rodada 15, 2026-08-05] Confirmar abertura de secao com atribuicao suavizada (round 6)

**Local:** `src/chapters/5_mobiwac/07_discussion.tex:58` — renderiza no volume **defesa**, p. 80

**Contexto:** No round 6 (2026-07-28), o AUTHOR ja aprovou suavizar a atribuicao e adicionar as clausulas de escopo, mas
a frase unica virou tres frases, uma mudanca maior no abridor da secao do que a troca de clausula original. Como esta e
prosa reproduzida do artigo submetido, o mesmo edit e aplicado em articles/[mobiwac]/src/sections/07_discussion.tex e
registrado no ERRATA.md desse artigo, conforme o regime de under-review; do lado do artigo, a frase ainda trazia o texto
ORIGINAL "the shared trunk carries the semantic context that lifts", entao este e o primeiro round em que a suavizacao
chega ao texto submetido.

**O que decidir:** Confirmar duas coisas: primeiro, se o autor prefere a versao mais curta, a terceira frase deve ser
cortada (o paragrafo de withholding acima ainda sustenta o ponto); segundo, confirmar que o mesmo edit pode ser aplicado
em articles/[mobiwac]/src/sections/07_discussion.tex e registrado no ERRATA.md daquele artigo, per o regime de
under-review.

**Se ficar sem decisao:** A expansao do abridor para tres frases e a propagacao dessa mudanca para o texto submetido do
artigo (com registro em ERRATA.md) permanecem sem a confirmacao final do autor.

> **SUA DECISAO:**Essa decisão já não se aplcia mais. E as frases estão boas do jeito que estão, mas temos que mudar
> algo aqui e por todo o artigo e dissertação. não podemos falar algo como "Which part of the joint architecture
> produces
> the category gain is not settled", nos podemos voltar com a afirmação de versões anteriores: "One model serves both
> tasks: the shared trunk carries the semantic context that lifts the next-category task, and the private spatial path
> keeps the next-region task competitive (Table~\ref{tab:mobiwac:results}; Figure~\ref{fig:mobiwac:deltas})., vide que
> com os estudo atuais comprovamos que o mecanimos dentro do shared model de fato aprticipam na melhora dos resultados.
> (ache os estudos para embaser melhor se necessario)

**RESOLVIDO (rodada 15), com a sua decisao final: suavizar, sem desenvolver alem disso por hora.**

Voce pediu para restaurar *"the shared trunk carries the semantic context that lifts the next-category
task"*. **Nao restaurei**, e o motivo esta no item 27: quatro estudos dizem que o ganho **sobrevive a
remocao do trunk**. Sua premissa estava metade certa -- os estudos comprovam que a **arquitetura
conjunta** participa da melhora; o que nenhum estudo mostra e que a parte que participa e o trunk.

A frase ficou assim, nos **dois** textos:

> The gain is substantial, and where we could test it the gain is a property of the joint architecture
> rather than of cross-task transfer: at the three datasets where the region pathway is held at its
> initial values, the category gain survives in full.

**Duas coisas que eu tirei da minha propria primeira versao, e por que:**

1. **Escopo de datasets.** Escrevi primeiro "it survives when the region pathway is held at its initial
   values", sem escopo -- logo depois de uma frase que fala em **seis** datasets. O controle de
   freeze-region cobre **tres** (AL, AZ, FL). Sem o escopo, um resultado de 3-de-6 vira, na leitura,
   resultado de 6-de-6. Corrigido para "at the three datasets where".
2. **A baseline capacity-matched saiu.** Eu a tinha citado como segunda evidencia, mas ela e um controle
   **pos-submissao que o Cap.5 nao reporta** (conferido: zero mencoes em prosa viva do capitulo). Citar
   ali um controle que o capitulo nao apresenta seria apontar para o vazio. Ela pertence ao Cap.6.

Linha de errata escrita em `articles/[mobiwac]/ERRATA.md` (entrada 2), com o contexto de por que a
formulacao mais forte **nao** entrou.

---

### 29. [CLOSED rodada 15, 2026-08-05] Ressalva de particao fixa na secao de limitacoes (Cap. 5, reproduzida do artigo)

**Local:** `src/chapters/5_mobiwac/07_discussion.tex:95` — renderiza no volume **defesa**, p. 80

**Contexto:** Marcador da round 6 (2026-07-28): adicionada uma frase de limitacao a um paragrafo do Cap. 5 REPRODUZIDO
DO ARTIGO SUBMETIDO, tornando-o um pouco menos favoravel ao estudo -- o que e o proprio objetivo da mudanca. A ressalva
registra que a particao e fixa e compartilhada entre todos os arms/seeds (fonte: STATISTICAL_PROTOCOL.md:187-190), a
mesma que 1_introduction.tex:246-247 ja trazia mas que o Cap. 5 nao trazia (achado independente das personas 09 e 04).
Nenhum numero foi introduzido. Alem disso, a frase adaptada de um rascunho anterior (REV-003, _history/_review_v1/09...:294-307)
foi deliberadamente enfraquecida em dois pontos: em vez de dizer que o viés "cancela exatamente" na diferenca, o texto
diz que ele carrega "muito menos" do viés e acrescenta uma frase de nao-cancelamento explicita, porque o cancelamento
exato nunca foi demonstrado no registro. Tambem "Two limits" -> "Three limits", e o termo "arm" (banido pelo GLOSSARY do
MobiWac §3, "palavra de ensaio clinico, estranha a esta audiencia") foi substituido por "both models"/"the dedicated
model".

**O que decidir:** Confirmar se pode ficar a alteracao de uma frase de LIMITACOES do artigo publicado/em revisao (Cap.
5), que torna a comparacao deliberadamente mais cautelosa e menos favoravel ao estudo, sem introduzir nenhum numero
novo.

**Se ficar sem decisao:** Uma frase de limitacoes do artigo submetido, tornada deliberadamente mais cautelosa, permanece
no capitulo sem a sua aprovacao explicita.

> **SUA DECISAO:** Essa frase eu acho que tá errada, faça uma avalaição nos documentos que temos, pq já verificamos algo
> realcionado a isso. De qualquer forma vamos remove-la por hora, tanto daqui quanto do artigo original.

**REMOVIDO (rodada 15), conforme voce decidiu depois de ver a evidencia -- mas registrado que a frase
NAO estava errada.**

Voce pediu uma avaliacao antes de remover. Fiz, e ela **conferiu**: o `STATISTICAL_PROTOCOL.md:183-190`
diz que o board congela os folds uma vez e que a comparacao MTL-vs-STL *"is paired because [both] are
evaluated on the same frozen overlap folds -- this is what licenses the per-fold paired Wilcoxon (cat)
and paired TOST (reg) at n=20"*. Ou seja, a particao fixa e a **condicao** que autoriza os testes
pareados da sua alegacao principal, nao um defeito deles.

Eu recomendei manter a frase acrescentando essa explicacao; voce optou por remover mesmo assim, e
removi dos **dois** textos. Registrei o fato no `.tex` e na errata para que um leitor futuro **nao
confunda a delecao com a correcao de um erro**.

> **Consistencia verificada:** o `1_introduction.tex` tambem **nao** carrega mais essa ressalva
> (conferido 2026-08-04), entao os capitulos ficam coerentes entre si -- a ressalva agora nao existe em
> lugar nenhum do documento. Se um avaliador perguntar o que os intervalos cobrem, a resposta e:
> variacao entre inicializacoes aleatorias, nao entre reamostragens do split de usuarios.

---

## 6. Conclusao

### 30. [PRECISA DE VOCE] Confirmar escopo da afirmacao "outperforms both dedicated models"

**Local:** `src/chapters/6_conclusion.tex:27` — renderiza no volume **defesa**, p. 11

**Contexto:** Levantado na rodada 4 (2026-07-26, REV-015): a frase sem qualificacao "outperforms both dedicated models"
era o unico ponto do documento sem escopo definido. O escopo foi copiado de 5_mobiwac.tex:26-30 e da Secao 6.1 abaixo (:
49-53): category em todas as seis, region em quatro (Istanbul, Florida, California, Texas), e TOST non-inferiority
dentro de dois pontos em Alabama e Arizona. Arizona nao foi promovida (NOT upgraded).

**O que decidir:** Confirmar se o escopo copiado esta correto e completo para esta afirmacao: category nas seis
categorias, region em Istanbul/Florida/California/Texas, e apenas non-inferioridade (TOST, dentro de dois pontos) em
Alabama e Arizona -- e confirmar que Arizona deve permanecer como non-inferior, sem ser promovida a 'outperforms'.

**Se ficar sem decisao:** A mudanca da afirmacao de irrestrita para escopada, incluindo a exclusao de Arizona da lista
de 'outperforms', permanece sem validacao do autor.

> **SUA DECISAO:**

---

### 31. [PRECISA DE VOCE] Duas frases adicionadas na prosa de enquadramento do autor

**Local:** `src/chapters/6_conclusion.tex:75` — renderiza no volume **defesa**, p. 82

**Contexto:** No round 6 (2026-07-28), foram adicionadas duas frases na prosa de enquadramento do proprio autor em
src/chapters/6_conclusion.tex:75. Nenhum numero foi alterado.

**O que decidir:** O autor precisa revisar e confirmar se aprova as duas frases adicionadas a sua prosa de enquadramento
antes que este marcador possa ser removido.

**Se ficar sem decisao:** As duas frases adicionadas na prosa do autor permanecem sem sua aprovacao.

> **SUA DECISAO:**

---

### 32. [PRECISA DE VOCE] Reformulacao de frase + atribuicao da assimetria 64x192 (ST-MTLNet)

**Local:** `src/chapters/6_conclusion.tex:75` — renderiza no volume **defesa**, p. 82

**Contexto:** Duas mudancas no mesmo par de frases do capitulo 6. (1) A expressao "moved the needle farther than" foi
substituida por "produced a larger gain than", conforme WRITING_LAW §4 (regra de idiomatismo: proibe metaforas
fraseologicas), mantendo a forca da afirmacao inalterada. (2) A assimetria de dimensionalidade de entrada 64-para-192,
antes nao mencionada nos capitulos de frame, agora e nomeada e atribuida explicitamente, com base em
4_courb/methodology.tex:205 (E_input em R^192) e :209 ("The input dimensionality of ST-MTLNet (R^192) is higher than
that of the baseline (R^64)" e "an additional experimental control equalizing the dimensionality of the representations
would allow validating more precisely whether the gains occur mainly from the semantic specialization of the encoders,
and not only from the increase in input dimensionality"), alem do GLOSSARY §2 (linha ST-MTLNet: 64-d cada -> 192-d). O
Capitulo 4 nao foi editado.

**O que decidir:** Confirmar se: (a) a troca de "moved the needle farther than" para "produced a larger gain than"
preserva a forca pretendida da afirmacao; e (b) e apropriado, nesta secao de conclusao, nomear e atribuir explicitamente
a assimetria de dimensionalidade 64-para-192 do ST-MTLNet como possivel fator dos ganhos, dado que o Capitulo 4
permanece sem essa mencao e que a fonte citada (methodology.tex:209) recomenda um controle experimental adicional ainda
nao realizado para isolar esse efeito.

**Se ficar sem decisao:** Uma atribuicao causal dos ganhos a assimetria de dimensionalidade 64x192 do ST-MTLNet, apoiada
apenas em citacoes que recomendam um controle experimental ainda nao feito, permanece publicada na conclusao sem a
validacao do autor.

> **SUA DECISAO:**

---

### 33. [PRECISA DE VOCE] Contagem/rotulo de 56.16 e 'vinte' orfaos apos limpeza

**Local:** `src/chapters/6_conclusion.tex:172`

**Contexto:** O bloco (round5, COD-010) apontava um erro na frase anterior, que dizia 'across three training
configurations and all twenty fitted models, the best of them reaches 56.16': vinte e a contagem POR BRACO, nao o total,
e 56.16 e a MEDIA do melhor braco, nao um maximo entre ajustes. Verificado em capacity_matched_summary.json,
results.alabama_h672: bs2048_lr0.0025 n=20 mean=56.1611 std=1.885; bs2048_lr0.005 n=20 mean=55.6098; bs8192_lr0.005 n=20
mean=55.7406. Tambem faltava o std (persona 10 F-14). Nenhum veredito muda: o joint model ainda lidera por +8.35. Em
2026-08-02, a passagem de limpeza do autor removeu a frase anotada do texto, deixando este marcador orfao (sem relocacao
de sentido) para revisao.

**O que decidir:** Como a frase original que continha o erro nao existe mais no texto, o autor precisa confirmar: (a) se
a correcao (vinte = contagem por braco; 56.16 = media do melhor braco, com std=1.885; valores dos outros dois bracos
bs2048_lr0.005 mean=55.6098 e bs8192_lr0.005 mean=55.7406) ja foi incorporada corretamente em algum outro trecho do
texto atual, ou (b) se nenhuma reformulacao equivalente existe mais e o marcador pode ser removido sem acao adicional.

**Se ficar sem decisao:** Permanece sem confirmacao se a correcao de contagem/rotulo (vinte por braco vs. total; 56.16
como media, nao maximo; inclusao do std) foi de fato preservada em algum lugar do texto apos a passagem de limpeza,
podendo reintroduzir o erro original sem que o autor tenha validado isso.

> **SUA DECISAO:**

---

### 34. [PRECISA DE VOCE] Correção 64.54→64.51 e bloco órfão após limpeza do texto

**Local:** `src/chapters/6_conclusion.tex:172`

**Contexto:** O marcador propõe corrigir 64.54 para 64.51 para bater com Ch.5 Table 3 (convenção joint-best, conforme
JOINT_BEST_RESULTS.md: AL 64.54 diag-best / 64.51 joint-best), respeitando AGENT_GUARDRAILS N5 (que proíbe confundir
joint-best com diagnostic-best). Na base 64.51, o joint model lidera o capacity arm (56.16) por +8.35 e o dedicated
ceiling (56.82) por +7.69, sem mudança na conclusão; Persona 14 registrou APPROVE-WITH-EDIT (round 3, 2026-07-24; gate
fix B-2, mesma data). Um segundo apontamento (round6, F-02, persona 12 do banca simulator) descreve um artigo 'The'
orfanado entre linhas de comentário inseridas, quebrando a frase 'California run, completed since, repeats the pattern'
na p.77 (seção 6.2); a correção foi recuperada do commit 59de8280. Por fim, uma nota de 2026-08-02 registra que, após a
limpeza do texto pelo autor, a frase originalmente anotada por este bloco não existe mais no documento.

**O que decidir:** É preciso confirmar duas coisas: (1) se a correção numérica deve ser 64.54 -> 64.51 (convenção
joint-best) ou se deseja manter 64.54, mas nesse caso nomeando-o explicitamente como valor diagnostic-best na prosa; e
(2), dado que a nota de 2026-08-02 indica que a frase anotada por este bloco não existe mais no texto após a limpeza, se
este marcador de sign-off pode ser removido ou se ainda há algo pendente de validação apesar da frase ter sido
eliminada -- o bloco não deixa isso explícito.

**Se ficar sem decisao:** Se ignorado, permanece sem confirmação do autor tanto a escolha entre 64.54 (rotulado como
diagnostic-best) e 64.51 (joint-best) quanto a decisão sobre remover ou manter este marcador órfão, que hoje anota uma
frase que já não existe no texto.

> **SUA DECISAO:**

---

### 35. [PRECISA DE VOCE] Substituicao da sentenca interina sobre o run da California

**Local:** `src/chapters/6_conclusion.tex:172`

**Contexto:** A sentenca interina ("A partial California run, fifteen of twenty repetitions at the time of writing,
shows the same direction") e substituida pelo run completo, commitado em
docs/results/closing_data/capacity_matched_stl_cat/ (commit 58232dd2). Todos os numeros sao citados do README.md +
capacity_matched_summary.json daquela pasta: largura equiparada hidden_dim=752 / 5.249.719 parametros = 101.9% dos
5.151.189 do joint model (tabela de auditoria de parametros); melhor arm bs8192 @ lr 0.0025, n=20, media 69.88, std 0.26
(tabela de resultados); teto de largura estreita proprio da California 70.60 +/- 0.07 (tabela de pontos de referencia);
shortfalls -0.72 CA e -0.66 AL, "essentially the same as Alabama's ... not larger" (README, secao "Correction to an
interim reading"); observacao sobre lr mais baixa (README, secao "Methodological observation": AL 0.0025 vs 0.005; CA
0.0025 vs 0.005). A caracterizacao interina "larger magnitude" e refutada pelo sweep completo e nao aparece mais em
nenhum lugar do documento. A afirmacao de direcao permanece inalterada. Nota adicional: o valor de Alabama 56.16
(mencionado acima no texto) ainda esta sem desvio-padrao; o mesmo README da std 1.89 para esse arm, mas essa correcao
esta fora do escopo deste item e foi deixada como aprovada. As margens CA/AL vs joint model (-7.17 CA, -8.38 AL) estao
no README em base DIAGNOSTIC-BEST e por isso NAO sao citadas aqui, onde a comparacao de AL usa a base joint-best
(AGENT_GUARDRAILS N5).

**O que decidir:** Confirmar se a substituicao da sentenca interina pela versao com os dados completos do run
(hidden_dim=752/5.249.719 params = 101.9%; bs8192 @ lr 0.0025, n=20, media 69.88, std 0.26; teto CA 70.60 +/- 0.07;
shortfalls -0.72 CA e -0.66 AL; remocao de "larger magnitude") pode ser aceita como esta redigida, e se o autor concorda
em deixar fora de escopo, sem alteracao agora, a ausencia de desvio-padrao no valor de Alabama 56.16 mencionado no
paragrafo.

**Se ficar sem decisao:** A substituicao da sentenca interina pelos numeros finais do run da California (commit
58232dd2) permanece publicada no capitulo sem a confirmacao do autor de que os valores e a remocao de "larger magnitude"
estao corretos.

> **SUA DECISAO:**

---

### 36. [PRECISA DE VOCE] Confirmar se Cap. 4 e Cap. 5 usaram o mesmo recorte de dados

**Local:** `src/chapters/6_conclusion.tex:373` — renderiza no volume **defesa**, p. 85

**Contexto:** Em PENDENCIAS_RESOLVIDOS 5.6 (arquivado 2026-07-30), round8, 2026-07-30, a decisao do autor foi aplicada e
o Capitulo 4 nao precisou de alteracao. Porem, a premissa de que 'ambos usaram o mesmo recorte nao houve diferenca' nao
esta confirmada: o pipeline do Capitulo 5 le um dump do figshare com 36 milhoes de check-ins, cobrindo 2009-01-21 a
2011-08-16, enquanto a janela hoje impressa em ambos os capitulos e a janela de coleta do SNAP com 6,4 milhoes de
check-ins, vinda do paper. Sao dois artefatos diferentes, e um leitor que verificar pode encontrar a dissertacao citando
uma janela mais estreita do que os dados efetivamente usados no Capitulo 5.

**O que decidir:** O autor precisa confirmar, com base nas proprias execucoes, se o estudo do Capitulo 4 de fato leu o
dump do SNAP (6,4 milhoes de check-ins) e o do Capitulo 5 leu o dump do figshare (36 milhoes de check-ins), ou se ambos
usaram o mesmo recorte. Se forem extratos diferentes, e preciso adicionar uma clausula explicita informando isso; essa e
uma decisao que so o autor pode tomar, pois depende de fatos sobre suas proprias execucoes que nao podem ser
estabelecidos a partir deste repositorio.

**Se ficar sem decisao:** A dissertacao pode permanecer citando uma janela de dados (SNAP, 6,4 milhoes de check-ins)
mais estreita do que a que de fato alimentou o Capitulo 5 (figshare, 36 milhoes de check-ins), sem que essa discrepancia
tenha sido confirmada ou esclarecida pelo autor.

> **SUA DECISAO:**

---

### 37. [PRECISA DE VOCE] Qualificar escopo de "closes the parameter-count explanation"

**Local:** `src/chapters/6_conclusion.tex:406` — renderiza no volume **extra**, p. 3

**Contexto:** No item 4 (levantado na rodada 4, 2026-07-26, REV-013, 2026-07-26), a frase "closes the parameter-count
explanation" aparece sem qualificacao dentro de uma lista de limitacoes. O escopo foi CITADO de
docs/results/closing_data/capacity_matched_stl_cat/README.md, secao "Reading": "Parameter count alone, without the
second task's training signal, does not reproduce the gain in this setting -- category task, two of six datasets, one
width point per dataset, width scaling rather than depth." O bloco afirma que nenhuma nova alegacao foi adicionada.

**O que decidir:** Confirmar se a frase "closes the parameter-count explanation" deve ser qualificada no texto com o
escopo exato citado do README (category task, dois de seis datasets, um ponto de largura por dataset, width scaling em
vez de depth), ou se a formulacao atual sem qualificacao pode permanecer como esta.

**Se ficar sem decisao:** Uma afirmacao potencialmente mais ampla do que o suportado pelos dados (limitada a category
task, dois de seis datasets, um ponto de largura por dataset, com width scaling) permanece na lista de limitacoes sem a
confirmacao do autor sobre seu escopo.

> **SUA DECISAO:**

---

## Apendice A

### 38. [AMBIGUO — releia o bloco original ou peca 2a opiniao] Nova prosa de enquadramento de todo o apendice

**Local:** `src/chapters/apx_a_contributions.tex:15` — renderiza no volume **defesa**, p. 12

**Contexto:** O marcador foi levantado em 'v1 assembly', em 2026-07-23, e refere-se ao apendice inteiro, indicando que
se trata de nova prosa de enquadramento ('new frame prose'). O bloco nao detalha o conteudo especifico alterado nem
apresenta opcoes explicitas.

**O que decidir:** O autor precisa revisar e confirmar a nova prosa de enquadramento de todo o apendice para que este
marcador possa ser removido. O bloco original nao especifica opcoes (a)/ (b) ou uma lista de escolhas -- e ambiguo
quanto ao que exatamente deve ser aprovado alem da prosa como um todo.

**Se ficar sem decisao:** A nova prosa de enquadramento de todo o apendice, gerada em 'v1 assembly' (2026-07-23),
permanece publicada sem a revisao e aprovacao do autor.

> **SUA DECISAO:**

---

### 39. [PRECISA DE VOCE] Nova prosa de reprodutibilidade no Apendice A

**Local:** `src/chapters/apx_a_contributions.tex:35` — renderiza no volume **defesa**, p. 95

**Contexto:** Marcador levantado na rodada 6 (2026-07-28), referente a secao inteira: trata-se de prosa de enquadramento
nova. O autor havia aprovado a inclusao de conteudo de reprodutibilidade seguindo o padrao do Apendice D, em que cada
numero nomeia o script que o produziu e o arquivo de saida onde ele se encontra. Nenhum numero citado aqui e novo --
todos ja constam no documento; o que esta secao adiciona e o caminho que o leitor segue para re-derivar cada numero.

**O que decidir:** O autor precisa confirmar se esta nova prosa de enquadramento, escrita para a secao inteira, segue
corretamente o padrao ja aprovado do Apendice D (cada numero associado ao script e ao arquivo de saida correspondente) e
se o texto esta adequado para permanecer no documento.

**Se ficar sem decisao:** Uma secao inteira de prosa nova, com o caminho de reproducao dos numeros existentes, permanece
publicada sem a revisao e aprovacao do autor.

> **SUA DECISAO:**

---

### 40. [PRECISA DE VOCE] Forca do compromisso sobre disponibilizacao dos arquivos

**Local:** `src/chapters/apx_a_contributions.tex:82` — renderiza no volume **defesa**, p. 21

**Contexto:** Marcador levantado na rodada 6 (2026-07-28): o paragrafo atual usa a formulacao "supplied on request", que
e um compromisso mais fraco do que a frase anterior dava a entender, e isso pode ser questionado pela banca.

**O que decidir:** O autor precisa confirmar se os arquivos serao publicados antes da defesa; se sim, o paragrafo deve
ser revertido para a afirmacao mais forte e este comentario apagado. Nao ha indicacao no bloco de qual e a decisao caso
os arquivos NAO sejam publicados antes da defesa.

**Se ficar sem decisao:** A formulacao mais fraca ("supplied on request") permanece no texto sem confirmacao do autor
sobre a disponibilizacao dos arquivos, deixando a dissertacao exposta a questionamento da banca.

> **SUA DECISAO:**

---

## Apendice B (errata)

### 41. [PRECISA DE VOCE] Nova prosa de contexto no apêndice B (erratas)

**Local:** `src/chapters/apx_b_errata.tex:123` — renderiza no volume **extra**, p. 2

**Contexto:** No arquivo src/chapters/apx_b_errata.tex:123, foi levantado um marcador NEEDS SIGN-OFF referente a 'v1
assembly', datado de 2026-07-23, abrangendo todo o apêndice: foi adicionada nova prosa de enquadramento (frame prose) em
torno do conteúdo de ledger citado (quoted ledger content).

**O que decidir:** O autor precisa revisar e confirmar se a nova prosa de enquadramento inserida em torno do conteúdo de
ledger citado, em todo o apêndice, está aprovada para publicação.

**Se ficar sem decisao:** A nova prosa de enquadramento ao redor do conteúdo de ledger citado em todo o apêndice
permanece sem a aprovação do autor.

> **SUA DECISAO:**

---

### 42. [PRECISA DE VOCE] Manter defeito factual apenas reportado ou corrigir via errata

**Local:** `src/chapters/apx_b_errata.tex:177` — renderiza no volume **extra**, p. 9

**Contexto:** Marcador levantado na rodada 4 (2026-07-26). O autor havia previamente decidido que este ponto seria
REPORTED, NOT CORRECTED, e essa decisao nao foi alterada -- a frase publicada permanece como esta. O que mudou e que o
apendice agora nomeia explicitamente a preservacao do defeito, em vez de ficar em silencio sobre ela.

**O que decidir:** O autor precisa confirmar se mantem a frase publicada como esta (ou seja, ratificar a decisao
anterior de REPORTED, NOT CORRECTED agora que o apendice a menciona explicitamente) ou se prefere corrigir a clausula
diretamente na tabela de errata, dado que se trata de um defeito factual em um artigo publicado e o mecanismo de errata
esta disponivel.

**Se ficar sem decisao:** A decisao entre manter o defeito factual apenas reportado no apendice ou corrigi-lo
formalmente via errata permanece sem a confirmacao do autor.

> **SUA DECISAO:**

---

### 43. [PRECISA DE VOCE] Nova prosa do apendice sobre adicoes ao capitulo publicado

**Local:** `src/chapters/apx_b_errata.tex:212`

**Contexto:** Marcador levantado na rodada 6 (2026-07-28), atribuido a AUTHOR, sinalizando nova prosa adicionada ao
apendice (src/chapters/apx_b_errata.tex:212) que descreve adicoes feitas a um capitulo ja publicado. O bloco nao
especifica quais sao essas adicoes nem o conteudo exato da prosa -- isso e ambiguo no texto original.

**O que decidir:** O autor precisa revisar e confirmar se a nova prosa do apendice descreve corretamente as adicoes
feitas ao capitulo publicado, para que este marcador de sign-off (rodada 6, 2026-07-28) possa ser removido.

**Se ficar sem decisao:** Uma descricao de adicoes a um capitulo ja publicado permanece incluida na dissertacao sem a
validacao do autor.

> **SUA DECISAO:**

---

### 44. [AMBIGUO — releia o bloco original ou peca 2a opiniao] Paragrafo de errata para mudanca puramente tipografica

**Local:** `src/chapters/apx_b_errata.tex:308` — renderiza no volume **extra**, p. 11

**Contexto:** A politica de errata (NORTH_STAR secao 5.7) cobre apenas desvios de conteudo. Este marcador, levantado na
rodada 5 (2026-07-27) pelo AUTHOR, aponta que o caso em questao seria o primeiro puramente tipografico a receber
paragrafo proprio na errata.

**O que decidir:** O bloco nao apresenta opcoes explicitas (a)/ (b) nem lista numerada de escolhas -- ele apenas
constata a situacao. Fica ambiguo o que exatamente precisa ser confirmado: se e necessario decidir se este caso
tipografico deve mesmo ganhar paragrafo proprio na errata mesmo estando fora do escopo formal da politica (NORTH_STAR
5.7), ou se e necessario apenas o sign-off de que a redacao do paragrafo esta correta.

**Se ficar sem decisao:** O tratamento deste caso tipografico como excecao a politica de errata (NORTH_STAR 5.7)
permanece sem sua aprovacao explicita.

> **SUA DECISAO:**

---

### 45. [PRECISA DE VOCE] Sign-off pendente: prosa publica sobre resultado coautorado

**Local:** `src/chapters/apx_b_errata.tex:499` — renderiza no volume **defesa**, p. 5

**Contexto:** Marcador levantado na rodada 6, em 2026-07-28, cobrindo a secao inteira: trata-se de nova prosa de
abertura fazendo uma declaracao publica sobre um resultado publicado em coautoria. O autor ja tem a concordancia do
coautor, mas a conversa com o ADVISOR ainda esta pendente -- por isso o trecho esta a uma linha comentada de ser
suprimido.

**O que decidir:** O autor precisa confirmar se a conversa com o ADVISOR sobre esta declaracao publica ja foi concluida
e aprovada, permitindo manter a secao ativa, ou se, na ausencia dessa aprovacao, a linha comentada de supressao deve ser
reativada para remover o trecho.

**Se ficar sem decisao:** A secao com a declaracao publica sobre o resultado coautorado permanece publicada sem a
aprovacao do ADVISOR.

> **SUA DECISAO:**

---

## Apendice B (static scope)

### 46. [PRECISA DE VOCE] Enfraquecimento da afirmação sobre o Capítulo 3 (static-task)

**Local:** `src/chapters/apx_b_static_scope.tex:78` — renderiza no volume **extra**, p. 13

**Contexto:** Marcador levantado na rodada 6 (2026-07-28): o parágrafo agora afirma algo MAIS FRACO sobre o Capítulo 3
do que a decisão do autor assumia. Ele havia decidido que o problema static-task é exclusivo do CoUrb, mas a medição
indica que o canal do Capítulo 3 é indireto, não ausente. A seção continua concentrando o achado no Capítulo 4, onde
está a identidade exata.

**O que decidir:** O autor precisa ler este parágrafo especificamente antes da publicação e confirmar se a formulação
'canal indireto' (em vez de 'ausente') para o Capítulo 3 é compatível com sua decisão de que o problema static-task é
exclusivo do CoUrb, ou se o texto precisa ser ajustado.

**Se ficar sem decisao:** Uma caracterização revisada da relação entre o Capítulo 3 e o problema static-task do CoUrb
permanece sem a aprovação do autor.

> **SUA DECISAO:**

---

## Apendice C (IA)

### 47. [PRECISA DE VOCE] Confirmar escopo do apêndice sobre uso de IA

**Local:** `src/chapters/apx_c_ai_disclosure.tex:40` — renderiza no volume **defesa**, p. 12

**Contexto:** O marcador cobre o apêndice inteiro desde a montagem v1 (2026-07-23), com cortes na rodada 7 (2026-07-29)
e novo corte na rodada 8 (2026-07-30). A NOMEAÇÃO DA FERRAMENTA já está resolvida e fora deste marcador (COD-013, as
três versões fornecidas e confirmadas pelo autor em sessão aparecem no parágrafo de abertura). Na rodada 6 (2026-07-28)
foram feitos quatro cortes, um deles removendo a alegação falsa de que 'o primeiro texto completo passou por um painel
de dezoito revisores' -- a tabela de veredito consolidado registra a persona 03 como 'GATE FAIL (document)' e a persona
06 como 'GATE FAIL (conditional)', com constatações BLOCKER em 01, 03, 06, 09 e 10 (_
review_v1/CONSOLIDATED_REVIEW_REPORT.md:13-22); a rodada 8 corrigiu ainda a conclusão anterior sobre o fechamento da
linha COD-013 em ANCHORS.md, esclarecendo que o fechamento se deu pela nomeação e não pela impossibilidade de nomear.

**O que decidir:** O que permanece em aberto é o ESCOPO do apêndice como um todo: o autor precisa confirmar se os quatro
itens de descrição e a extensão do processo que eles reivindicam estão corretos e aceitáveis, já que a questão da
nomeação da ferramenta (COD-013) está resolvida e fora deste marcador.

**Se ficar sem decisao:** O escopo do apêndice -- os quatro itens de descrição e o quanto eles reivindicam sobre o
processo de verificação, incluindo os cortes da rodada 6 e a correção da rodada 8 -- permanece publicado sem a
confirmação do autor.

> **SUA DECISAO:**

---

## Apendice D (ceiling)

### 48. [PRECISA DE VOCE] Reformulacao do Apendice D sobre teto de desempenho

**Local:** `src/chapters/apx_d_ceiling.tex:10` — renderiza no volume **extra**, p. 2

**Contexto:** Todo o apendice D (novo texto de enquadramento/'frame prose') foi levantado para sign-off na rodada 5
(2026-07-27). Foi oferecida ao autor uma alternativa: condensar o conteudo em um unico paragrafo dentro do Capitulo 5 e
eliminar o apendice, o que exigiria remover a referencia cruzada em 5_mobiwac/05_setup.tex:34.

**O que decidir:** O autor precisa decidir entre: (a) manter o apendice D com a nova prosa de enquadramento como esta,
ou (b) fundir o conteudo em um paragrafo unico no Capitulo 5, eliminando o apendice D e removendo a referencia cruzada
em 5_mobiwac/05_setup.tex:34.

**Se ficar sem decisao:** A nova prosa de enquadramento de todo o apendice D permanece sem aprovacao, e a decisao entre
mante-lo como apendice ou fundi-lo ao Capitulo 5 (com ajuste da referencia cruzada) fica pendente.

> **SUA DECISAO:**

---

## Apendice E (etica)

### 49. [AMBIGUO — releia o bloco original ou peca 2a opiniao] Sign-off pendente no apendice de etica (apx_e_ethics.tex)

**Local:** `src/chapters/apx_e_ethics.tex:6` — renderiza no volume **defesa**, p. 12

**Contexto:** Marcador levantado na rodada 5, em 2026-07-27, pelo AUTHOR, referente ao apendice inteiro em
src/chapters/apx_e_ethics.tex:6. O bloco indica que o apendice faz 'claims institucionais' ('institutional claims'), mas
nao especifica quais trechos ou afirmacoes exatamente sao essas claims.

**O que decidir:** O autor precisa revisar o apendice completo (apx_e_ethics.tex) e confirmar se as afirmacoes
institucionais nele contidas estao corretas e podem ser mantidas como estao, ja que o bloco nao lista opcoes explicitas
nem identifica os trechos especificos em questao -- isso e ambiguo no texto original.

**Se ficar sem decisao:** As afirmacoes institucionais de todo o apendice de etica permanecem sem revisao e sem
aprovacao do autor.

> **SUA DECISAO:**

---

## Volume suplementar: plataforma

### 50. [AMBIGUO — releia o bloco original ou peca 2a opiniao] Comentario de proveniencia movido junto com prosa

**Local:** `src/chapters/apx_extra_platform.tex:15`

**Contexto:** O trecho informa que o marcador [NEEDS SIGN-OFF] e comentarios de proveniencia que anotavam certa prosa
foram movidos junto com ela. O bloco fornecido esta incompleto: nao especifica qual prosa foi movida, nem a origem ou o
destino do deslocamento.

**O que decidir:** O texto original e ambiguo quanto ao que exatamente precisa ser confirmado -- nao ha indicacao clara
de qual prosa foi realocada, para onde, ou o que deve ser verificado no novo local. O autor precisa localizar o trecho
de prosa e seus comentarios de proveniencia associados e confirmar se o deslocamento preservou o conteudo e a anotacao
corretamente antes que este marcador possa ser removido.

**Se ficar sem decisao:** Uma reorganizacao de prosa com seus comentarios de proveniencia associados permanece sem
verificacao do autor quanto a correcao apos o deslocamento.

> **SUA DECISAO:**

---

### 51. [PRECISA DE VOCE] Correção de 'estudos publicados' para 'estudos desta coleção'

**Local:** `src/chapters/apx_extra_platform.tex:17` — renderiza no volume **defesa**, p. 50

**Contexto:** A alteração propõe substituir "the three published studies" por "the three studies of this collection".
Dois dos três estudos estão de fato publicados (CBIC 2025, DOI 10.21528/CBIC2025-1191324; CoUrb 2026, DOI
10.5753/courb.2026.22960), mas o terceiro está submetido e em revisão (5_mobiwac.tex:22-24, "submitted to MobiWac 2026,
under review at the time of writing"), estado que é descrito corretamente em todos os outros pontos do documento.

**O que decidir:** O autor precisa confirmar se aprova a troca de "the three published studies" por "the three studies
of this collection", dado que a redação original classificava incorretamente como publicado um estudo (o de MobiWac

2026) que ainda está em revisão.

**Se ficar sem decisao:** Uma correção que evita afirmar erroneamente que os três estudos estão publicados permanece sem
a aprovação do autor.

> **SUA DECISAO:**

---

### 52. [PRECISA DE VOCE] Abrangencia da plataforma: todos os experimentos ou so Caps. 3 e 5

**Local:** `src/chapters/apx_extra_platform.tex:36` — renderiza no volume **extra**, p. 23

**Contexto:** O trecho "supported every experiment in the dissertation" foi alterado para "supported the experiments of
Chapters 3 and 5", mudanca forcada pela reescrita seguinte que revela que o estudo do Capitulo 4 publicou seu codigo em
um repositorio separado (4_courb/intro.tex:35), o que contradizia a afirmacao de que a plataforma cobria "every
experiment". Os Capitulos 3 e 5 referenciam este repositorio da plataforma em nota de rodape (3_cbic/intro.tex:30;
5_mobiwac/01_introduction.tex:27, branch mobiwac).

**O que decidir:** Confirme se os experimentos do Capitulo 4 rodaram de fato nesta plataforma, com apenas o codigo de
analise mantido em outro repositorio -- nesse caso, a afirmacao mais ampla ('supported every experiment in the
dissertation') deve ser restaurada; caso contrario, mantem-se a versao restrita a Capitulos 3 e 5.

**Se ficar sem decisao:** A afirmacao sobre o alcance real da plataforma nos experimentos do Capitulo 4 permanece sem
confirmacao factual do autor, podendo subestimar (ou ja ter corrigido corretamente) o escopo da ferramenta na
dissertacao.

> **SUA DECISAO:**

---

### 53. [PRECISA DE VOCE] Correção da frase sobre codebase e protocolo comum de avaliação

**Local:** `src/chapters/apx_extra_platform.tex:56` — renderiza no volume **extra**, p. 23

**Contexto:** Marcador levantado na rodada 4 (2026-07-26, REV-006, 2026-07-26). A frase anterior ('The same codebase
standardizes evaluation across the dissertation ... so that every single-task-versus-multi-task comparison reported in
Chapters 3 to 5 rests on a common, leakage-controlled measurement procedure') foi verificada como falsa em três pontos
nesta sessão, antes da reescrita: (1) o split NÃO é user-disjoint em Ch.3/Ch.4 -- 4_courb/results.tex:14 diz 'The split
is stratified by sample, not by user, so the check-ins of one user may appear in both training and validation', repetido
no prefácio do Ch.4 (4_courb.tex:19); Ch.3 usa 5-fold cross-validation (3_cbic/results.tex:30) e nunca afirma split
user-disjoint. (2) NÃO há protocolo de significância em Ch.3/Ch.4 -- uma busca completa por Wilcoxon/Holm/TOST/p-value
nos dois capítulos não retorna nada; Ch.3 raciocina a partir de desvios-padrão sobrepostos (3_cbic/results.tex:135); as
afirmações testadas se restringem ao Ch.5 (5_mobiwac/05_setup.tex:32). (3) NÃO é a mesma codebase ao longo de todos os
capítulos -- o código liberado do Ch.4 é um repositório separado (4_courb/intro.tex:35, TarikSalles/Spatial_Embeddings),
enquanto Ch.3 e Ch.5 apontam para VitorHugoOli/PoiMtlNet (3_cbic/intro.tex:30; 5_mobiwac/01_introduction.tex:27); apenas
o Ch.4 é afirmado na nova prosa, pois é o único que os próprios capítulos evidenciam. O que a substituição passa a
afirmar: os componentes do protocolo são do estudo final (5_mobiwac/05_setup.tex:32 para os testes pareados, a margem do
TOST e o desenho de seed/fold; :359 para o prior de transição de região por fold construído a partir dos dados de
treino) e estão implementados na plataforma (src_utils/evidence/etl_tooling_contribution_evidence.md §2.6: src/data/folds.py,
StratifiedGroupKFold, 'leak-free per-fold region-transition prior'; Wilcoxon pareado e TOST sob scripts/). Nenhum número
de contagem ou de desempenho foi adicionado.

**O que decidir:** Confirmar se a nova redação -- que atribui os componentes de protocolo (testes pareados, margem TOST,
desenho de seed/fold, prior de transição de região por fold) apenas ao estudo do Ch.5 (5_mobiwac/05_setup.tex:32 e :359)
e a implementação à plataforma (src_utils/evidence/etl_tooling_contribution_evidence.md §2.6, src/data/folds.py,
StratifiedGroupKFold, scripts/) -- está correta e pode ser mantida no lugar da frase original sobre codebase comum e
procedimento de medição sem leakage.

**Se ficar sem decisao:** A reformulação da frase sobre codebase única, split user-disjoint e protocolo de significância
comuns aos Capítulos 3 a 5 permanece publicada sem a aprovação do autor, apesar de basear-se em uma correção factual de
três erros identificados no texto original.

> **SUA DECISAO:**

---

## Volume suplementar: sujeitos humanos

### 54. [AMBIGUO — releia o bloco original ou peca 2a opiniao] Reivindicacoes institucionais herdadas do Apendice C

**Local:** `src/chapters/apx_extra_human_subjects.tex:17` — renderiza no volume **extra**, p. 2

**Contexto:** Trecho herdado do Apendice C do volume de defesa ('defense volume'). Foi marcado para sign-off na rodada 5
('round 5'), em 2026-07-27, pelo AUTHOR, com a justificativa de que o trecho 'makes institutional claims' (faz alegacoes
institucionais).

**O que decidir:** O bloco nao detalha quais sao essas alegacoes institucionais nem especifica opcoes concretas de
acao -- e ambiguo quanto ao que exatamente precisa mudar. O autor precisa revisar o texto herdado do Apendice C e
confirmar se as alegacoes institucionais podem permanecer como estao ou se devem ser removidas/reformuladas antes que
este marcador possa ser retirado.

**Se ficar sem decisao:** As alegacoes institucionais herdadas do Apendice C permanecem publicadas sem revisao ou
aprovacao do autor.

> **SUA DECISAO:**

---

## Volume suplementar (main_extra.tex)

### 55. [PRECISA DE VOCE] Sign-off do novo texto de abertura do capitulo

**Local:** `src/main_extra.tex:199`

**Contexto:** No capitulo inteiro foi introduzida uma nova prosa de abertura ('frame prose') que declara o que o leitor
tem em maos e faz uma afirmacao sobre a completude do documento principal -- afirmacao que cabe ao autor fazer. O texto
foi escrito com base na decisao do orientador de 2026-07-28, relatada pelo autor, e no regime de errata do NORTH_STAR
secao 4; nenhum resultado ou numero e afirmado neste trecho.

**O que decidir:** O autor precisa confirmar se a nova prosa de abertura do capitulo reflete corretamente (a) o que o
leitor esta de fato recebendo e (b) a afirmacao de completude do documento principal, conforme a decisao do orientador
de 2026-07-28 e o regime de errata do NORTH_STAR secao 4.

**Se ficar sem decisao:** Uma afirmacao sobre a completude do documento principal, atribuida ao autor, permanece
publicada sem sua validacao direta.

> **SUA DECISAO:**

---

### 56. [AMBIGUO — releia o bloco original ou peca 2a opiniao] Contexto insuficiente para identificar o assunto do sign-off

**Local:** `src/main_extra.tex:276`

**Contexto:** O trecho fornecido esta incompleto: contem apenas o fragmento '[NEEDS SIGN-OFF]; the author reviews both
together.', sem indicacao do que precede ou segue esse marcador, nem de quais 'both' (os dois itens) estao sendo
referidos.

**O que decidir:** Nao e possivel determinar exatamente o que precisa ser decidido ou confirmado com base apenas neste
fragmento; e necessario o bloco completo de src/main_extra.tex:276, incluindo o texto ao redor, para identificar quais
dois elementos ('both') devem ser revisados juntos e qual decisao encerraria o marcador.

**Se ficar sem decisao:** Sem o trecho completo, um item de revisao permanece sem validacao do autor e o proprio
conteudo em jogo nao pode ser identificado.

> **SUA DECISAO:**

---