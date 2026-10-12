# CONSIDERATIONS.md — os pontos dos revisores, com ID estavel e status medido

> **O que este arquivo e.** Um bloco por ponto de revisao, com ID estavel, a citacao original, o estado
> dessa citacao no fonte VIVO, minha leitura com o raciocinio, a decisao, onde ele aparece no PDF, o nome
> do probe que o defende, e **o commit contra o qual a medicao foi tomada**. O que precisa da sua decisao
> esta em [`PENDENCIAS.md`](PENDENCIAS.md) **§6**; o resto mora aqui.
>
> **A prosa original nao foi apagada.** Ela esta em
> [`_history/_round9/30_considerations_prosa_original.md`](_history/_round9/30_considerations_prosa_original.md), byte por
> byte (com o sha256 e o comando que o reproduz no cabecalho), junto com a auditoria de 2026-07-28 e o
> adendo dela. Este arquivo e a forma de trabalho; aquele e o registro.


> ### ATENCAO — houve edicao CONCORRENTE nesta arvore enquanto eu media
>
> Enquanto esta passagem corria, **outro editor alterou dois arquivos que eu nao toquei**, e as
> mudancas nao estao commitadas:
>
> | arquivo | mtime | o que mudou |
> |---|---|---|
> | `GLOSSARY.md` | 02:11:37 | +31 linhas: quatro registros de Pareto (dominancia, otimalidade, ponto Pareto-estacionario, conflito de gradientes) e os quatro pares PT, fechando a PENDENCIAS_RESOLVIDOS 2.12 (arquivado 2026-08-02) pela opcao (a) |
> | `src/chapters/2_fundamentals.tex` | 02:23:31 | +106 linhas em §2.3: a equacao da perda total (`eq:fund:mtl-total`), o tratamento de dominancia/otimalidade/estacionariedade de Pareto, e a frase de que esta dissertacao nao reivindica propriedade de Pareto nenhuma |
>
> **Consequencias para este arquivo, medidas e nao inferidas:**
>
> 1. **`make check` esteve em rc=2 por causa daquela edicao, e ja voltou a rc=0** — pela propria
>    esteira, nao por mim. O gate `check_verify_list` reprovava numa anotacao de
>    `_history/_round6/VERIFY_LIST.md` que dizia `# EXPECT: contains=Pareto-stationary 0`, tornada falsa no
>    instante em que o termo foi registrado; ela foi corrigida para `2` no mesmo commit do registro.
>    Um segundo vermelho (um `CD-FAIL`) vinha de um bloco cercado no mesmo arquivo que fazia o gate
>    **rodar um build de verdade**, 108 s medidos; o bloco saiu da cerca as 03:01. Eu nao mexi em
>    nenhum dos dois: sao daquela esteira. **A licao e minha, porem** — eu li os dois como vermelhos
>    meus e cheguei a escrever o primeiro como uma decisao do autor com tres opcoes. Numa arvore com
>    duas esteiras, um gate vermelho nao vale nada ate se reconferir de quem e o arquivo e qual o mtime.
> 2. **Tres coordenadas minhas andaram +106 linhas** e foram **reconferidas linha a linha**, nao
>    deslocadas por aritmetica: FAB-28 (454 -> 560), FAB-29 (513 -> 619) e FAB-30 (515-516 -> 621-622,
>    e 670 -> 776). As ancoras antes da linha 418 nao se moveram.
> 3. **AUT-01 e a parte 1 do GER-09 foram parcialmente ATENDIDOS por aquela edicao** — a equacao da
>    perda total e o tratamento de Pareto agora existem no fonte. Os blocos desses dois itens dizem
>    isso. O que **continua faltando** do GER-09 e o agrupamento dos balanceadores por mecanismo, a
>    linhagem de quem definiu o que, e a definicao do conflito pelo cosseno **na prosa do §2.3** (o
>    registro do GLOSSARY nao e prosa do capitulo).
>
> Nao commitei nenhum dos dois arquivos: nao sao meus e estao em andamento.

## 0 · Como ler um bloco

```
### ID — titulo de uma linha
- Reviewer            quem, e se foi VERBAL ou ESCRITO
- Quote               a passagem em que o ponto se ancora
- Live-source status  exata / alterada / desaparecida, com arquivo:linha
- What he asks        o pedido, nas palavras dele
- My take             minha leitura, com o raciocinio
- Disposition         VOCE APLICA / VOCE DECIDE / BLOQUEADO
- Where it renders    onde o efeito aparece no PDF
- Probe               o nome em check_audit_claims.py que defende a correcao
- Build commit        o estado da arvore em que a medicao foi tomada
```

**IDs nunca sao reciclados.** `FAB-01`..`FAB-31` seguem a numeracao que voce mesmo escreveu na prosa
original; `GER-01`..`GER-11` sao meus, na ordem em que os pontos do Germano aparecem na sua transcricao;
`AUT-01` e a sua pergunta no fim do arquivo. Um numero vago e melhor que um ponteiro errado.

**Os pontos do Germano foram transcritos por voce, de uma conversa.** Onde este arquivo cita o Germano,
esta citando a sua paraphrase, e os blocos dele dizem isso explicitamente. Nenhuma palavra ali e
atribuida a ele como se fosse escrita.

---

## 1 · A medicao, antes de qualquer juizo

Cada ponto se ancora numa passagem citada. Localizei cada uma no fonte vivo (comentarios removidos,
quebras de linha juntadas, `\ref` resolvido pelos `.aux` do build) e classifiquei em exata / alterada /
desaparecida.

| Revisor | Itens | Ancoras | exata | alterada | desaparecida | parafrase |
|---|--:|--:|--:|--:|--:|--:|
| Fabrício (escrito) | 31 | 31 | 22 | 4 | 5 | 0 |
| Germano (verbal) | 11 | 14 | 10 | 0 | 0 | 4 |
| **Total** | **42** | **45** | **32** | **4** | **5** | **4** |

As quatro colunas somam 45, o numero de ancoras. As 4 parafrases sao pontos do Germano em que
ele descreveu a passagem em vez de cita-la, e por isso nao ha string para localizar.

**9 de 41 ancoras localizaveis (22%) estao obsoletas, e elas nao estao espalhadas:** todas as
9 sao do Fabrício, todas citam `0_main.tex`, e sao exatamente os itens **FAB-02 a FAB-10**. Aquele arquivo
foi dividido em `preamble.tex` + `content.tex` em 2026-07-29, e o Resumo e o Abstract foram cortados e
reescritos em 2026-07-28. **As 20 ancoras dele fora do `0_main.tex` conferem todas** — e as outras duas que
citam `0_main.tex` (FAB-01, a linha do orientador, e FAB-11, as palavras-chave) tambem, porque aquele
texto sobreviveu a divisao do arquivo.

*(Uma correcao minha, registrada porque a versao errada quase foi publicada: eu primeiro contei **dez**
obsoletas e escrevi que "todas as dez citam `0_main.tex`". Eram nove. A decima era o FAB-27, que esta no
arquivo da TABELA e cuja citacao so falhou porque ele a escreveu prefixada com "Na tabela: " e terminada
em "....". O texto que ele cita esta presente palavra por palavra. Uma linha de resumo e exatamente onde
o membro discrepante se esconde.)*

A consequencia pratica, e ela e boa: **FAB-04, FAB-05 e FAB-08 ja estao satisfeitos** — a palavra
`coletanea`, a clausula "na ordem em que aconteceram" e a clausula do par de tarefas nao existem em
lugar nenhum do fonte vivo. Ele pode ter lido um build anterior a reescrita.

**As medicoes da auditoria de 2026-07-28 tambem foram refeitas**, porque uma auditoria e um conjunto de
ancoras como qualquer outro. Cinco continuam valendo (5 secoes, ZERO subsecoes, 3 equacoes numeradas,
~4.400 palavras, 1 citacao por 64 palavras). **Tres nao:** ela contou 27 paragrafos, media de 161
palavras e cinco paragrafos acima de 240; hoje sao **33 paragrafos, media de 132, e 4** acima de 240.
As tres linhas obsoletas sao todas da Parte V, cujo argumento inteiro e sobre estrutura de paragrafo.

## 2 · A divisao

| Balde | Itens | O que significa |
|---|--:|---|
| **VOCE APLICA** | 20 | Concordo, a correcao nao envolve juizo de conteudo seu, e nada trava. **7 edicoes ja estao aplicadas e conferidas no PDF renderizado nos dois sentidos** (texto novo presente, texto antigo ausente), e **1 — o FAB-01 — ja estava satisfeito e so foi conferido**, sem edicao: sao a Wave A do `_history/_round9/33_apply_plan.md`. Os outros 12 esperam a outra esteira soltar o `2_fundamentals.tex` ou uma linha sua no `GLOSSARY`. |
| **VOCE DECIDE** | 22 | Precisa da sua palavra: ou eu discordo do revisor, ou colide com uma regra de honestidade do proprio documento, ou tem mais de uma saida com custos diferentes. Opcoes em `PENDENCIAS.md` §6. |
| **BLOQUEADO** | 1 | A verificacao falhou: FAB-28, nao consegui abrir o resumo do `wang2025hamtl`. |
| **Total** | **43** | 31 FAB + 11 GER + 1 AUT |

*(O FAB-18 mudou de balde **enquanto eu o aplicava**, e por isso os numeros aqui nao sao os do primeiro
commit desta rodada: ele pede o presente na mesma frase que o FAB-03 pede em portugues, e eu tinha
posto um como "eu aplico" e o outro como "voce decide". Nao podem ser os dois: e a mesma frase em duas
linguas, e o par Resumo/Abstract tem de ficar identico afirmacao por afirmacao. Virou uma decisao sua
sobre tres sitios. Achei isso ao digitar a edicao, nao ao classificar.)*

**Discordar de um membro da banca e decisao sua, nao minha.** Onde acho que o revisor esta errado no
merito, o item e "VOCE DECIDE" com o meu argumento anexado, por mais convicto que eu esteja. Sao tres:
**FAB-17** (o paragrafo que ele cortaria carrega material com aval registrado), **FAB-27** (as
referencias da tabela estao corretas; o defeito e outro) e **GER-02** (a prosa ja diz "extends", e
chamar HGI de "aplicacao" sub-creditaria os autores). Obsolescencia e diferente: "esta citacao nao
existe mais" e uma medicao, e essa e minha.

---

## 3 · Os itens

## Fabricio — `content.tex` (o antigo `0_main.tex`)  (11 itens)
### FAB-01 — the advisor line should appear in English too

- **Reviewer:** Fabricio, written
- **Quote:** "Orientador: Fabrício Aguiar Silva."
- **Live-source status:** **exact** — `content.tex:47`.
  - **The file he cites no longer exists.** `0_main.tex` became `preamble.tex` + `content.tex` on 2026-07-29; where the passage survives, it is in `content.tex`.
- **What he asks:** Colocar em inglês também.
- **My take:** agree. The PT resumo names the advisor in Portuguese and the EN abstract already says 'Advisor:'; his ask is satisfied at content.tex:134 for the label, but the ROLE line in the PT block is PT-only by ABNT convention. The applicable edit is the EN abstract's own line, already correct. Nothing to change beyond confirming; recorded as satisfied.
- **ALREADY SATISFIED; CONFIRMED IN THE RENDERED PDF, NOT APPLIED.** Nothing was edited for this item and nothing needed to be: `build/main.pdf` already carries `Advisor: Fabrício Aguiar Silva` in the English abstract and `Orientador: Fabrício Aguiar Silva` on the folha de rosto, and the diff against `c39b7b77` contains no advisor line added or removed. **The both-directions check that the other Wave A items carry does not apply here** — there is no superseded wording to be absent, so only the presence half is measurable, and that is what was measured. I first wrote the standard applied-and-verified note on this block, which claimed a measurement that could not exist.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** content.tex:47 (PT), :134 (EN) -> pp. i-ii
- **Probe in `check_audit_claims.py`:** none — this edit changes no string a probe can pin. Named rather than omitted, so the gap is visible.
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-02 — start a new sentence on the shared-history point

- **Reviewer:** Fabricio, written
- **Quote:** "permite que um serviço sensível à mobilidade aja antes que a visita aconteça, e as duas tarefas de previsão leem o mesmo histórico de visitas,"
- **Live-source status:** **gone** — `content.tex`. The text he read is not what the source says now; longest-common-run coverage against the closest live passage is 0.16.
  - **The file he cites no longer exists.** `0_main.tex` became `preamble.tex` + `content.tex` on 2026-07-29; where the passage survives, it is in `content.tex`.
- **What he asks:** Iniciar nova sentença com algo como: "Em termos de dados, essas duas tarefas de previsão precisam do mesmo histórico...."
- **My take:** his edit no longer applies as written. The clause he quoted is GONE: the Resumo was cut and rebuilt on 2026-07-28. The live sentence is 'as duas tarefas leem o mesmo histórico, portanto um único modelo poderia aprendê-las em conjunto'. His point (start a new sentence, foreground the data argument) can still be applied to the new sentence, but it is a rewrite of text he has not read.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** content.tex:73-74
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-03 — put the open question in the present tense

- **Reviewer:** Fabricio, written
- **Quote:** "era uma questão em aberto quando esta pesquisa começou."
- **Live-source status:** **changed** — `content.tex`. The text he read is not what the source says now; longest-common-run coverage against the closest live passage is 0.73.
  - **The file he cites no longer exists.** `0_main.tex` became `preamble.tex` + `content.tex` on 2026-07-29; where the passage survives, it is in `content.tex`.
- **What he asks:** Colocar no presente: "é uma questão em aberto", como se estivesse escrevendo no começo da pesquisa.
- **My take:** agree on substance; the sentence changed. He asked for the present tense. The live wording is 'permanecia em aberto' (imperfect), not the 'era' he quoted. Present tense would read 'permanece em aberto'. It is a claim-time question: the document elsewhere time-indexes CBIC/CoUrb conclusions, and the abstract saying 'permanece' asserts the question is open TODAY, after the dissertation answered it.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** content.tex:76
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-04 — do not mention the coletanea in the Resumo

- **Reviewer:** Fabricio, written
- **Quote:** "Esta dissertação responde a essa pergunta ao longo de três estudos, apresentados como uma coletânea de artigos..."
- **Live-source status:** **gone** — `content.tex`. The text he read is not what the source says now; longest-common-run coverage against the closest live passage is 0.15.
  - **The file he cites no longer exists.** `0_main.tex` became `preamble.tex` + `content.tex` on 2026-07-29; where the passage survives, it is in `content.tex`.
- **What he asks:** Não precisa falar aqui sobre a coletânea de artigos; deixar apenas para a introdução, na organização do texto. Aqui, falar como se fosse um único trabalho.
- **My take:** his edit is already satisfied. 'coletânea' occurs NOWHERE in the live Resumo or Abstract, and nowhere in the live tree. Either an earlier round already applied this, or he read a build that predates the rebuild. Confirm he is content.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** content.tex (absent)
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-05 — drop the negative-result / diagnosis / resolution clause

- **Reviewer:** Fabricio, written
- **Quote:** "apresentados como uma coletânea de artigos na ordem em que aconteceram: um resultado negativo, seu diagnóstico e sua resolução."
- **Live-source status:** **gone** — `chapters/1_introduction.tex`. The text he read is not what the source says now; longest-common-run coverage against the closest live passage is 0.08.
  - **The file he cites no longer exists.** `0_main.tex` became `preamble.tex` + `content.tex` on 2026-07-29; where the passage survives, it is in `content.tex`.
- **What he asks:** Em "na ordem em que aconteceram: um resultado negativo, seu diagnóstico e sua resolução.": Tirar essa parte.
- **My take:** already satisfied. Same as FAB-04: the 'na ordem em que aconteceram' clause is gone.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** content.tex (absent)
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-06 — say scenarios, not states, before the reader knows what a state is

- **Reviewer:** Fabricio, written
- **Quote:** "cinco estados dos Estados Unidos e Istambul"
- **Live-source status:** **changed** — `content.tex`. The text he read is not what the source says now; longest-common-run coverage against the closest live passage is 0.76.
  - **The file he cites no longer exists.** `0_main.tex` became `preamble.tex` + `content.tex` on 2026-07-29; where the passage survives, it is in `content.tex`.
- **What he asks:** O leitor não sabe nada de estados ainda; falar em "cenários" em vez de "estados".
- **My take:** agree, and it generalizes. 'estados' appears before the reader knows what a state is here. But 'cenário/scenario' is NOT in the GLOSSARY, which is fail-closed, so the term must be registered before it enters prose. Same ask as FAB-21 and FAB-31.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** content.tex:86
- **Probe in `check_audit_claims.py`:** `R9-scenario` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-07 — name the study instead of the stage of the research

- **Reviewer:** Fabricio, written
- **Quote:** "e não a arquitetura de compartilhamento, era o gargalo naquele estágio da pesquisa."
- **Live-source status:** **gone** — `content.tex`. The text he read is not what the source says now; longest-common-run coverage against the closest live passage is 0.30.
  - **The file he cites no longer exists.** `0_main.tex` became `preamble.tex` + `content.tex` on 2026-07-29; where the passage survives, it is in `content.tex`.
- **What he asks:** Em "naquele estágio da pesquisa", ele comenta: `no primeiro estudo (??)`
- **My take:** agree; his own note has a '??'. He wrote 'no primeiro estudo (??)', i.e. he was unsure. The quoted phrase is GONE; the live text reads 'naquela configuração'. Whether to name the study or the configuration is a claim-scope choice: 'no segundo estudo' is where the diagnosis was made, not the first.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** content.tex:82
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-08 — drop the task-pair clause from the Resumo

- **Reviewer:** Fabricio, written
- **Quote:** "; os dois primeiros pareavam a classificação de categoria com a previsão da próxima categoria, de modo que o próprio par de tarefas mudou ao longo da coletânea."
- **Live-source status:** **gone** — `content.tex`. The text he read is not what the source says now; longest-common-run coverage against the closest live passage is 0.20.
  - **The file he cites no longer exists.** `0_main.tex` became `preamble.tex` + `content.tex` on 2026-07-29; where the passage survives, it is in `content.tex`.
- **What he asks:** Tirar... está ficando confuso para o leitor
- **My take:** already satisfied. The task-pair clause is GONE from the Resumo. But note FAB-17 asks to delete the SAME content from the introduction, where it is AVAL-signed-off. Deciding 08 and 17 together avoids removing it from both places.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** content.tex (absent)
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-09 — simplify the results description; keep it higher level

- **Reviewer:** Fabricio, written
- **Quote:** "por 5,3 a 9,4 pontos de macro-F1 sob uma seleção \emph{joint-best} (um único \emph{checkpoint} por partição, escolhido na validação, com as duas tarefas avaliadas nesse \emph{checkpoint}), e, na tarefa da próxima região, supera em quatro dos seis conjuntos e equipara-se estatisticamente, com não-inferioridade dentro de uma margem de dois pontos de Acc@10 (TOST), nos outros dois. A resposta é, portanto, condicional..."
- **Live-source status:** **changed** — `content.tex`. The text he read is not what the source says now; longest-common-run coverage against the closest live passage is 0.40.
  - **The file he cites no longer exists.** `0_main.tex` became `preamble.tex` + `content.tex` on 2026-07-29; where the passage survives, it is in `content.tex`.
- **What he asks:** Simplificar essa descrição dos resultados... colocar em mais alto nível.
- **My take:** partly satisfied. The joint-best gloss he wanted simplified is GONE from the Resumo; the numbers (5,3 a 9,4) and the TOST clause remain. Cutting them further trades honesty rules (every number carries its convention) against his readability ask.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** content.tex:91-94
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Registry terms inside the quote:** `macro-F1`, `Acc@10`, `TOST`, `joint-best`
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-10 — the results sentence opens confusingly

- **Reviewer:** Fabricio, written
- **Quote:** "A resposta é, portanto, condicional, e a condição é o achado:"
- **Live-source status:** **changed** — `content.tex`. The text he read is not what the source says now; longest-common-run coverage against the closest live passage is 0.65.
  - **The file he cites no longer exists.** `0_main.tex` became `preamble.tex` + `content.tex` on 2026-07-29; where the passage survives, it is in `content.tex`.
- **What he asks:** Esse início está confuso também; começar com algo como: "Como principais resultados, identificamos que o aprendizado multitarefa etc etc..."
- **My take:** agree on substance; sentence changed. 'e a condição é o achado' is gone; the live sentence is 'A resposta é, portanto, condicional: se o aprendizado multitarefa ajuda depende...'. His proposed opener ('Como principais resultados, identificamos que...') is a first-person results framing, a register choice for the PT Resumo.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** content.tex:94
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-11 — separate keywords with commas, in both languages

- **Reviewer:** Fabricio, written
- **Quote:** "\textbf{Palavras-chave}:\ aprendizado multitarefa\ ponto de interesse\ previsão da próxima categoria\ previsão da próxima região\ representação em nível de check-in"
- **Live-source status:** **exact** (matches the rendered PDF; the source carries a `\ref`) — `content.tex`.
  - **The file he cites no longer exists.** `0_main.tex` became `preamble.tex` + `content.tex` on 2026-07-29; where the passage survives, it is in `content.tex`.
- **What he asks:** Separar por "virgula" em vez de quebra de linha; fazer o mesmo no inglês.
- **My take:** agree. Keywords are separated by \\ line breaks in both blocks. Comma separation is a presentation choice with no honesty or registry consequence, and he asked for both languages.
- **APPLIED THIS SESSION and verified in the RENDERED PDF** (`build/main.pdf` at build `386bec74`, text layer, both directions asserted: the new wording present AND the superseded wording absent), not in the source. The two-directional run was completed after an earlier pass had checked only one direction for four of the seven Wave A items; all sixteen assertions pass. Four targets rc=0, tex_errors=0.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** content.tex:120-125, :182-187
- **Probe in `check_audit_claims.py`:** `R9-keywords` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Build commit the measurement was taken against:** `d4078c75`

## Fabricio — `chapters/1_introduction.tex`  (13 itens)
### FAB-12 — users, plural

- **Reviewer:** Fabricio, written
- **Quote:** "a given user visited a given place"
- **Live-source status:** **exact** — `chapters/1_introduction.tex:34`.
- **What he asks:** `users`
- **My take:** agree. Plural 'users' reads better and the sentence is generic. No claim changes.
- **APPLIED THIS SESSION and verified in the RENDERED PDF** (`build/main.pdf` at build `386bec74`, text layer, both directions asserted: the new wording present AND the superseded wording absent), not in the source. The two-directional run was completed after an earlier pass had checked only one direction for four of the seven Wave A items; all sixteen assertions pass. Four targets rc=0, tex_errors=0.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 1_introduction.tex:34
- **Probe in `check_audit_claims.py`:** none — this edit changes no string a probe can pin. Named rather than omitted, so the gap is visible.
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-13 — say prediction tasks that are the object of study

- **Reviewer:** Fabricio, written
- **Quote:** "The two properties above are the two prediction tasks of this dissertation."
- **Live-source status:** **exact** — `chapters/1_introduction.tex:52`.
- **What he asks:** Em `prediction tasks`, consideração: `prediction tasks that are object of study of this ...`
- **My take:** agree. His phrasing is more precise about what the two tasks are to the document.
- **APPLIED THIS SESSION and verified in the RENDERED PDF** (`build/main.pdf` at build `386bec74`, text layer, both directions asserted: the new wording present AND the superseded wording absent), not in the source. The two-directional run was completed after an earlier pass had checked only one direction for four of the seven Wave A items; all sixteen assertions pass. Four targets rc=0, tex_errors=0.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 1_introduction.tex:52
- **Probe in `check_audit_claims.py`:** none — this edit changes no string a probe can pin. Named rather than omitted, so the gap is visible.
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-14 — the seven classes belong to the data, not the introduction

- **Reviewer:** Fabricio, written
- **Quote:** "The \emph{next category} task predicts the category of the next visited place, one of seven top-level classes."
- **Live-source status:** **exact** — `chapters/1_introduction.tex:52-54`.
- **What he asks:** Não precisa detalhar que são 7 aqui na introdução; isso não é característica do problema, mas dos dados, e deve aparecer apenas na hora de descrever a avaliação.
- **My take:** disagree, and it is his call. He says the 7 classes are a property of the data, not the problem. He is right in principle. But the count is what makes the next-category output space concrete against next region's hundreds-to-thousands, which is the contrast 1.2 is built on, and Appendix B's static-scope note depends on the taxonomy being introduced. Cost of removing: the reader meets 'seven' first in 2.4.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** 1_introduction.tex:52-53
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Registry terms inside the quote:** `next category`
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-15 — census tract and mahalle belong to the data, not the introduction

- **Reviewer:** Fabricio, written
- **Quote:** "The \emph{next region} task predicts the official geographic unit of the next visit, a census tract in the United States or a mahalle in Istanbul, a target space that ranges from hundreds to several thousand classes per dataset."
- **Live-source status:** **exact** — `chapters/1_introduction.tex:54-56`.
- **What he asks:** Em ", a census tract in the United States or a mahalle in Istanbul," e feito a consideração: "Isso também é inerente aos dados e não precisa entrar aqui na introdução."
- **My take:** disagree, same reason. Same class as FAB-14: census tract / mahalle is what makes 'region' concrete. Removing it leaves 'the official geographic unit' undefined until 2.4.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** 1_introduction.tex:54
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Registry terms inside the quote:** `next region`
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-16 — fewer semicolons; it reads as AI output

- **Reviewer:** Fabricio, written
- **Quote:** "The exact \emph{next place} task, predicting the specific establishment, is a third and different problem; this dissertation does not address it, and Chapter~\ref{ch:fundamentals} keeps the three tasks formally distinct."
- **Live-source status:** **exact** — `chapters/1_introduction.tex:56-59`.
- **What he asks:** Em "; this dissertation does not address it," a consideração: "not addressed in this dissertation (TENTE USAR MENOS ; no meio das frases...parece muito resultado de IA)"
- **My take:** agree. He is right on both counts and the second is a house rule already: semicolon braids are banned by WRITING_LAW 4. Rewriting as two clauses removes the AI tell he names.
- **APPLIED THIS SESSION and verified in the RENDERED PDF** (`build/main.pdf` at build `386bec74`, text layer, both directions asserted: the new wording present AND the superseded wording absent), not in the source. The two-directional run was completed after an earlier pass had checked only one direction for four of the seven Wave A items; all sixteen assertions pass. Four targets rc=0, tex_errors=0.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 1_introduction.tex:56-58
- **Probe in `check_audit_claims.py`:** none — this edit changes no string a probe can pin. Named rather than omitted, so the gap is visible.
- **Registry terms inside the quote:** `next place`
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-17 — the fourth-task paragraph is confusing and could go

- **Reviewer:** Fabricio, written
- **Quote:** "A fourth task also appears in this dissertation: the first two studies paired next category prediction with the static classification of a place's category, category classification, and Section~\ref{sec:intro:arc} explains why the final study replaced it. Next category and next region were chosen for what a mobility-aware service can act on, and both are established end targets in the literature on the way to the..."
- **Live-source status:** **exact** — `chapters/1_introduction.tex:61-66`.
- **What he asks:** Parágrafo confuso; acho que pode tirar.
- **My take:** DISAGREE, and this is the one I would push back on. The paragraph he would delete is the AVAL-signed-off task-pair acknowledgment (a) and the three-legged task-choice defense (b) recorded in NORTH_STAR 6 Ch.1 beat 4. It exists because a prior review round required the document to state plainly that the task pair EVOLVED and to defend the task choice. Deleting it reopens both. If it is confusing, the fix is to split it into two shorter sentences, not to remove it.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** 1_introduction.tex:61-64
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Registry terms inside the quote:** `next category`, `next region`
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-18 — put the open question in the present tense

- **Reviewer:** Fabricio, written
- **Quote:** "was unresolved when this research started."
- **Live-source status:** **exact** — `chapters/1_introduction.tex:85; content.tex:152-153`.
- **What he asks:** Colocar no presente.
- **My take:** agree on substance; same decision as FAB-03, not a separate one. He asks for the present tense here and at FAB-03; it is one claim in three places (1_introduction.tex:92, content.tex:156 EN, content.tex:76 PT). I first bucketed this as 'apply' and FAB-03 as 'decide', which cannot both be right: the same sentence cannot be mine to edit in English and his to rule on in Portuguese, and the Resumo/Abstract pair must stay claim-for-claim identical (WRITING_LAW 6). The substantive question is the one FAB-03 carries: 'is/permanece' asserts the question is open TODAY, after this dissertation answered it, which is what the time-indexing rule exists to prevent. Caught while applying it, not while sorting.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** 1_introduction.tex:92 + content.tex:156 (EN) + content.tex:76 (PT)
- **Probe in `check_audit_claims.py`:** `R9-tense` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-19 — cut the arc of this dissertation from the heading

- **Reviewer:** Fabricio, written
- **Quote:** "\section{Research question and the arc of this dissertation}"
- **Live-source status:** **exact** — `chapters/1_introduction.tex:87`.
- **What he asks:** Em "the arc of this dissertation" consideração: "Tirar"
- **My take:** agree. 'the arc of this dissertation' in a section heading is decoration; the section is the research question.
- **APPLIED THIS SESSION and verified in the RENDERED PDF** (`build/main.pdf` at build `386bec74`, text layer, both directions asserted: the new wording present AND the superseded wording absent), not in the source. The two-directional run was completed after an earlier pass had checked only one direction for four of the seven Wave A items; all sixteen assertions pass. Four targets rc=0, tex_errors=0.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 1_introduction.tex:87
- **Probe in `check_audit_claims.py`:** none — this edit changes no string a probe can pin. Named rather than omitted, so the gap is visible.
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-20 — standardize point of interest, hyphen or no hyphen

- **Reviewer:** Fabricio, written
- **Quote:** "Does multi-task learning help point-of-interest prediction (next category and next region), and what does the answer depend on?"
- **Live-source status:** **exact** — `chapters/1_introduction.tex:93-94`.
- **What he asks:** Padronizar a escrita de `point of interest` (POI) em todo o texto. É com ou sem hífen? Manter o mesmo sempre.
- **My take:** agree, with the standard rule. Measured live: 11 hyphenated vs 8 spaced. The principled rule is the English compound-modifier rule (attributive hyphenated, nominal open), which makes 15 of the 19 already correct. Flattening to one form would produce 'a user visits a point-of-interest', which is wrong. Registering the rule in GLOSSARY and sweeping against it.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** whole tree; 8 files
- **Probe in `check_audit_claims.py`:** `R9-poihyphen` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Registry terms inside the quote:** `next category`, `next region`
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-21 — scenario, not state

- **Reviewer:** Fabricio, written
- **Quote:** "with decomposed spatial, temporal, and categorical encoders. Category performance rose sharply at every state tested."
- **Live-source status:** **exact** — `chapters/1_introduction.tex:113-114`.
- **What he asks:** Em "state", o comentario é: `scenario`
- **My take:** agree. Same term as FAB-06/31. Depends on registering 'scenario'.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 1_introduction.tex:113-114
- **Probe in `check_audit_claims.py`:** `R9-scenario` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-22 — the result detail does not belong in the introduction

- **Reviewer:** Fabricio, written
- **Quote:** "five states of the United States and Istanbul: on the category task at all six, and on the region task at four of six, with statistical non-inferiority within a two-point margin (TOST) at the other two."
- **Live-source status:** **exact** — `chapters/1_introduction.tex:130-133`.
- **What he asks:** Não precisa incluir os detalhes dos resultados aqui.
- **My take:** his call: it collides with an honesty rule. He wants the result detail out of the introduction. WRITING_LAW 3 requires every number to carry its reference point and convention, and the region verbs to be bound to their tests. Dropping 'four of six ... TOST' from the intro removes exactly that binding, so the sentence must either keep the test or stop making the comparative claim.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** 1_introduction.tex:130-132
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Registry terms inside the quote:** `TOST`
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-23 — cut the repeated chapter title after the reference

- **Reviewer:** Fabricio, written
- **Quote:** "\textbf{Chapter~\ref{ch:fundamentals}, Fundamentals}, consolidates the background the three"
- **Live-source status:** **exact** — `chapters/1_introduction.tex:218`.
- **What he asks:** Em ", Fundamentals}," o comentario é: "Tirar."
- **My take:** agree. Repeating the chapter title after the \ref is redundant once the ref renders the number.
- **APPLIED THIS SESSION and verified in the RENDERED PDF** (`build/main.pdf` at build `386bec74`, text layer, both directions asserted: the new wording present AND the superseded wording absent), not in the source. The two-directional run was completed after an earlier pass had checked only one direction for four of the seven Wave A items; all sixteen assertions pass. Four targets rc=0, tex_errors=0.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 1_introduction.tex:218
- **Probe in `check_audit_claims.py`:** none — this edit changes no string a probe can pin. Named rather than omitted, so the gap is visible.
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-24 — cut the repeated chapter title after the reference

- **Reviewer:** Fabricio, written
- **Quote:** "\textbf{Chapter~\ref{ch:conclusion}, Conclusion}, consolidates the answer to the research question, states the limitations, and derives future work from them."
- **Live-source status:** **exact** — `chapters/1_introduction.tex:244-245`.
- **What he asks:** Em ", Conclusion}, " o comentario é: "Tirar."
- **My take:** agree. Same as FAB-23.
- **APPLIED THIS SESSION and verified in the RENDERED PDF** (`build/main.pdf` at build `386bec74`, text layer, both directions asserted: the new wording present AND the superseded wording absent), not in the source. The two-directional run was completed after an earlier pass had checked only one direction for four of the seven Wave A items; all sixteen assertions pass. Four targets rc=0, tex_errors=0.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 1_introduction.tex:244
- **Probe in `check_audit_claims.py`:** none — this edit changes no string a probe can pin. Named rather than omitted, so the gap is visible.
- **Build commit the measurement was taken against:** `d4078c75`

## Fabricio — `chapters/2_fundamentals.tex`  (6 itens)
### FAB-25 — POI hyphenation is inconsistent here

- **Reviewer:** Fabricio, written
- **Quote:** "Each record is a \emph{check-in}: a user, a point of interest (POI), and a timestamp."
- **Live-source status:** **exact** — `chapters/2_fundamentals.tex:27-28`.
- **What he asks:** Em: "point of interest (POI)". consideração: "Aqui está sem hífen; padronize em todo o texto."
- **My take:** agree with a correction. The instance he flagged, 'a user, a point of interest (POI), and a timestamp', is ALREADY CORRECT: it is the nominal use. The inconsistency is real but the fix is the rule, not flattening. Handled with FAB-20.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 2_fundamentals.tex:27
- **Probe in `check_audit_claims.py`:** `R9-poihyphen` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Registry terms inside the quote:** `point of interest`
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-26 — Check2HGI reads like an existing competing method

- **Reviewer:** Fabricio, written
- **Quote:** "The check-in-level representation, Check2HGI, completes the line."
- **Live-source status:** **exact** — `chapters/2_fundamentals.tex:228`.
- **What he asks:** Ficou parecendo que é um artigo concorrente existente; falar que é a sua proposta já no começo do parágrafo.
- **My take:** agree. Two independent readers stopped at the same sentence, which is the strongest possible signal. Naming ownership in the first clause is a one-clause fix and removes a real misreading risk (an uncited third-party method).
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 2_fundamentals.tex:228 -> 2.2
- **Probe in `check_audit_claims.py`:** `R9-check2hgi` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Registry terms inside the quote:** `check-in-level representation`, `Check2HGI`, `HGI`
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-27 — the table's chapter references are wrong

- **Reviewer:** Fabricio, written
- **Quote:** "Na tabela: "\caption{Representation and model lineage threaded through this dissertation, from the place-level graph-infomax...."
- **Live-source status:** **exact** — `tables/frame/lineage.tex:5-8 (caption) -> Table 2.1`.
  - *Correction to my own first pass:* reclassified: it scored CHANGED only because his quote is prefixed with his own words ('Na tabela: "') and ends in an ellipsis. The caption text he quotes is present verbatim in tables/frame/lineage.tex. Nothing about this anchor is stale; the item is in the TABLE file, not in 2_fundamentals.tex where he cited it.
- **What he asks:** A referência dos capítulos da tabela está errada.
- **My take:** disagree as stated; a real problem underneath. Checked directly: ch:courb -> 4 and ch:mobiwac -> 5 in build/main-aux, both resolve, nothing dangling. What is wrong is that ONE column mixes bracketed citations and chapter pointers, so the chapter numbers read as mis-rendered citations. Also ST-MTLNet HAS a published record (paiva2026stmtlnet, already in the bib and cited in Ch.4/Ch.5) and the table shows it only as 'Chapter 4'. Two fixes are possible and they differ in cost.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** tables/frame/lineage.tex -> Table 2.1
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-28 — there is more MTL-for-POI work than the two papers cited

- **Reviewer:** Fabricio, written
- **Quote:** "In mobility, MTL has been used almost entirely in the service of next place."
- **Live-source status:** **exact** — `chapters/2_fundamentals.tex:560`.
- **What he asks:** Pelo que me lembro, há outros artigos que abordam MTL para tarefas de POI, não? Ficaram apenas dois artigos aqui, o que parece pouco pelo que me lembro.
- **My take:** agree on substance; verification FAILED on the decisive paper. He is right that the coverage is thin, and the real exposure is that 2.3 claims NO multi-task model predicts next region as a co-equal end target while wang2025hamtl (hierarchy-aware MTL for user LOCATION prediction, J. Supercomputing 81(11):1196, 2025) sits uncited in the same bibliography. Whether the claim survives turns on whether that paper treats a region-like unit as an END TARGET, and I could NOT establish it: OpenAlex has no abstract, Crossref has no abstract, the configured Springer key returns 401 on meta/v2, metadata and meta/v1, the paper is closed access (Unpaywall oa_status=closed), and the landing page 303-redirects to an authentication gate. Semantic Scholar offers only a MACHINE-GENERATED tldr, which AGENT_GUARDRAILS R5 forbids as a source. Four of the five other candidates ARE verified and citable (see the ledger); this one is not, and it is the one the novelty sentence depends on.
- **Disposition:** **BLOCKED**
- **Where it renders if applied:** 2_fundamentals.tex:560 -> 2.3
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Registry terms inside the quote:** `next place`
- **Build commit the measurement was taken against:** `d4078c75`

- **CORRECTED 2026-07-30, after the citation auditor's pass.** My block said the decisive paper's
  content could not be established. The repository had already established it: `src/references.bib`
  lines 1148-1152 carry a provenance block, brought over from the MobiWac paper's own bibliography,
  recording a verification **against the Springer article page on 2026-07-06** and its finding —
  HAMTL jointly predicts the next location and its category, and **its location target is
  venue-level**. On that record the chapter's claim of absence is not threatened by this paper, and
  the sentence at `5_mobiwac/02_related.tex`:92-94 that says so is supported rather than floating.
  What this session could not do is independently reproduce that read: the article is closed access,
  the configured Springer key returns 401 on every documented endpoint, and the landing page redirects
  to an authentication gate I did not route around. **The item stays BLOCKED**, because what it
  actually asks for is a systematic count of MTL-for-POI work and no single paper settles that. But
  the question the author most likely wants answered — does this paper break the novelty claim — is
  **probably no, on the repo's own recorded reading.** I reached the wrong status by treating "I could
  not open it this session" as "it is unverified", without checking whether the repository had already
  done the work; the bibliography's provenance comments are a source of record and cost one grep.

### FAB-29 — fixes ???

- **Reviewer:** Fabricio, written
- **Quote:** "This section fixes both: the datasets the dissertation uses..."
- **Live-source status:** **exact** (matches the rendered PDF; the source carries a `\ref`) — `chapters/2_fundamentals.tex`.
- **What he asks:** `fixes ???`
- **My take:** agree. 'fixes' collides with the computing sense of repair; his three question marks are a reader report. 'sets out' keeps the meaning.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 2_fundamentals.tex:619 -> p. 2.4 opening
- **Probe in `check_audit_claims.py`:** `R9-fixes` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Build commit the measurement was taken against:** `d4078c75`
### FAB-30 — license the verbs is uncommon phrasing and reads as AI-generated

- **Reviewer:** Fabricio, written
- **Quote:** "and the tests that license the verbs used to report a comparison."
- **Live-source status:** **exact** — `chapters/2_fundamentals.tex:621-622`.
- **What he asks:** Em "license the verbs" a consideração: "Cuidado com termos muito incomuns de serem encontrados, provavelmente gerados por IA. Não é comum usar `license the verbs` em textos técnicos; revisar o texto que foi gerado por IA para evitar isso."
- **My take:** agree. 'license the verbs' is not standard technical English and appears twice. The RULE it encodes is load-bearing and survives in plain wording.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 2_fundamentals.tex:621, :670
- **Probe in `check_audit_claims.py`:** `R9-license` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Build commit the measurement was taken against:** `d4078c75`

## Fabricio — `chapters/6_conclusion.tex`  (1 itens)
### FAB-31 — scenarios, not states

- **Reviewer:** Fabricio, written
- **Quote:** "raised category macro-F1 by 20.2 to 22.0 percentage points across the three states tested."
- **Live-source status:** **exact** — `chapters/6_conclusion.tex:46-47`.
- **What he asks:** Trocar `states` para `scenarios`
- **My take:** agree. Same term as FAB-06/21.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 6_conclusion.tex:46
- **Probe in `check_audit_claims.py`:** `R9-scenario` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Registry terms inside the quote:** `macro-F1`
- **Build commit the measurement was taken against:** `d4078c75`

## Germano — verbal, transcrito pelo autor  (11 itens)
### GER-01 — add Spectral Networks and The graph neural network model to the graph paragraph

- **Reviewer:** Germano, **verbal**, transcribed by the author. The wording below is the author's paraphrase, not Germano's own words.
- **Quote:** "(anchor: the graph-neural-network paragraph of 2.2, which he was reading; the two titles he named are what he wants ADDED, not existing text)"
- **Live-source status:** **exact** — `chapters/2_fundamentals.tex:143`.
  - *Correction to my own first pass:* reclassified: my first pass scored the requested TITLES as a missing quote and called the item GONE. The item is a request, and its anchor paragraph is EXACT.
- **What he asks:** second para of 2.2: add two GNN citations
- **My take:** agree. Both requested works verified firsthand this session (arXiv:1312.6203v3; DOI 10.1109/tnn.2008.2005605 with all five authors from Crossref) and the specific claim located in each abstract. Adding them makes our own 'localized spectral rule' sentence true, since that rule IS a simplification of Bruna's spectral construction.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 2_fundamentals.tex:143 -> 2.2
- **Probe in `check_audit_claims.py`:** `R9-gnncites` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Build commit the measurement was taken against:** `d4078c75`
### GER-02 — DGI and HGI are presented as counterpoints, and they are not

- **Reviewer:** Germano, **verbal**, transcribed by the author. The wording below is the author's paraphrase, not Germano's own words.
- **Quote:** none — he described the passage instead of quoting it: DGI/HGI presented as counterpoints
- **Live-source status:** **paraphrase** (no quoted string to locate) — `not located`.
- **What he asks:** DGI/HGI presented as counterpoints
- **My take:** partially disagree, and the disagreement is mine to state, not to settle. The prose already says HGI 'builds directly on' DGI and 'extends' the objective, which is inheritance language, not contrast. I do not think the paragraph sets them against each other. His reading has a real cause though: the lineage table lists them as adjacent rows under 'What it added'. Also his framing 'HGI e uma aplicacao' would UNDER-credit Huang et al., and would sit badly beside our claim that Check2HGI extends the same hierarchy.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** 2_fundamentals.tex:143-165 + Table 2.1
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`
### GER-03 — the HGI tuning sweep is thrown into the text with no connection to it

- **Reviewer:** Germano, **verbal**, transcribed by the author. The wording below is the author's paraphrase, not Germano's own words.
- **Quote:** "The baseline was also tuned rather than taken as published: the cross-region edge weight of their Equation 2, set to 0.4 for the dense Chinese cities they study, was raised to 0.7 for the sparser United States state datasets used here."
- **Quote (GER-03b):** "from $0.7388 \pm 0.0205$ at the published setting to $0.8186 \pm 0.0123$ at the adopted one"
- **Live-source status:** **exact** — `chapters/2_fundamentals.tex:167-170`.
- **What he asks:** HGI tuning sweep reads as thrown in
- **My take:** agree it does not belong; the gate constrains HOW. Strongly agree the four-point sweep is a methods result in a fundamentals chapter, reported to four decimals under an averaging convention the chapter has not yet fixed. BUT the sentence is probe NUM-4 in check_audit_claims.py, which requires 0.8186 to be PRESENT with its spreads and averaging convention. Relocating is compatible with the probe if the probe moves with it; deleting the numbers is not.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** 2_fundamentals.tex:167-174 -> 2.2
- **Probe in `check_audit_claims.py`:** `NUM-4 (must move with the text)`
- **Load-bearing collision:** `NUM-4` on `chapters/2_fundamentals.tex` (pattern `0\.8186`, want_present=True) — same file, 505 chars from the probe string
- **Build commit the measurement was taken against:** `d4078c75`
### GER-04 — the static-vector paragraph reads like introduction prose, and it matters

- **Reviewer:** Germano, **verbal**, transcribed by the author. The wording below is the author's paraphrase, not Germano's own words.
- **Quote:** "A place embedding, however it is trained, shares one property: it assigns each place a single fixed vector."
- **Quote (GER-04b):** "CTLE makes the point concrete by learning location embeddings that are context- and time-aware, so that the vector for a place depends on the visit"
- **Live-source status:** **exact** — `chapters/2_fundamentals.tex:192-193`.
- **What he asks:** static-vector paragraph reads like introduction
- **My take:** agree it reads as introduction; he also says keep it. He called it well written and important, and only observed it reads like introduction prose. There is no defect to fix here, only a placement question, and it is 108 chars from the NUM-4 probe string.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** 2_fundamentals.tex:192-199
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Load-bearing collision:** `NUM-4` on `chapters/2_fundamentals.tex` (pattern `0\.8186`, want_present=True) — same file, 108 chars from the probe string
- **Registry terms inside the quote:** `place embedding`
- **Build commit the measurement was taken against:** `d4078c75`
### GER-05 — remove the HGI-roles sentence and the announcement after it

- **Reviewer:** Germano, **verbal**, transcribed by the author. The wording below is the author's paraphrase, not Germano's own words.
- **Quote:** "HGI is the place-level baseline representation the later chapters measure against, and it is the direct base of the representation the dissertation contributes. Two qualifications belong with that use."
- **Live-source status:** **exact** — `chapters/2_fundamentals.tex:162-164`.
- **What he asks:** remove the HGI two-roles + announcement sentences
- **My take:** agree in part. 'Two qualifications belong with that use.' is scaffolding and goes. The HGI two-roles sentence STAYS: it is the only place 2.2 tells the reader HGI is both the baseline and the ancestor of our contribution, and deleting it makes GER-02 worse. I merge the two into one sentence that states the roles.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 2_fundamentals.tex:162-164
- **Probe in `check_audit_claims.py`:** `R9-hgiroles` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Load-bearing collision:** `NUM-4` on `chapters/2_fundamentals.tex` (pattern `0\.8186`, want_present=True) — same file, 969 chars from the probe string
- **Registry terms inside the quote:** `HGI`
- **Build commit the measurement was taken against:** `d4078c75`
### GER-06 — the encoder paragraph lists papers without connecting them, FiLM is misfiled, and Ch.3/Ch.4 method arrives here

- **Reviewer:** Germano, **verbal**, transcribed by the author. The wording below is the author's paraphrase, not Germano's own words.
- **Quote:** "Before that step, several general"
- **Quote (GER-06b):** "In the models of Chapters 3 and 4 it conditions"
- **Live-source status:** **exact** — `chapters/2_fundamentals.tex:203`.
- **What he asks:** encoder paragraph: works listed without connection; FiLM misfiled
- **My take:** agree on all three counts. (i) five encoders arrive as consecutive one-sentence descriptions with no organizing claim; (ii) FiLM is a conditioning mechanism, not a mobility representation, and belongs with the sharing topologies in 2.3; (iii) the Ch.3/Ch.4 walk-through is method detail. The forward-pointing CLAIM stays, compressed to one sentence.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 2_fundamentals.tex:203-227 -> 2.2
- **Probe in `check_audit_claims.py`:** `R9-film` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Load-bearing collision:** `NUM-4` on `chapters/2_fundamentals.tex` (pattern `0\.8186`, want_present=True) — same file, 915 chars from the probe string
- **Build commit the measurement was taken against:** `d4078c75`
### GER-07 — have we defined what Check2HGI is before naming it

- **Reviewer:** Germano, **verbal**, transcribed by the author. The wording below is the author's paraphrase, not Germano's own words.
- **Quote:** "The check-in-level representation, Check2HGI"
- **Live-source status:** **exact** — `chapters/2_fundamentals.tex:228`.
- **What he asks:** is Check2HGI defined before it is named
- **My take:** agree. Same sentence as FAB-26; one fix serves both.
- **Disposition:** **YOU APPLY**
- **Where it renders if applied:** 2_fundamentals.tex:228
- **Probe in `check_audit_claims.py`:** `R9-check2hgi` — **NAME RESERVED, NOT YET IMPLEMENTED.** The edit has not been made, so there is nothing to probe yet. The probe lands in the same commit as the edit (GUARDRAILS §4b V15); until then this row is a plan, not a measurement.
- **Registry terms inside the quote:** `check-in-level representation`, `Check2HGI`, `HGI`
- **Build commit the measurement was taken against:** `d4078c75`
### GER-08 — several concepts have no formal definition, starting with a check-in

- **Reviewer:** Germano, **verbal**, transcribed by the author. The wording below is the author's paraphrase, not Germano's own words.
- **Quote:** none — he described the passage instead of quoting it: no formal definition of a check-in
- **Live-source status:** **paraphrase** (no quoted string to locate) — `not located`.
- **What he asks:** no formal definition of a check-in
- **My take:** strongly agree; it is a cross-chapter edit. The chapter defines a check-in in prose only and then writes L_c2p over check-in and place embeddings with no notation for a check-in, a user, a place, a category, or a region. His reason is the right one: the later chapters' equations need symbols with an origin. But notation must be checked against Chapters 3-5 AS COMMITTED and every new symbol registered in the fail-closed GLOSSARY first, so this is not a Chapter 2 edit.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** new 2.1 subsection
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`
### GER-09 — 2.3 needs MTL formalism, the balancer lineage, and a definition of loss conflict

- **Reviewer:** Germano, **verbal**, transcribed by the author. The wording below is the author's paraphrase, not Germano's own words.
- **Quote:** "\section{Multi-task learning}"
- **Live-source status:** **exact** — `chapters/2_fundamentals.tex:383`.
- **What he asks:** 2.3 lacks MTL formalism, provenance, and a conflict measure
- **My take:** strongly agree, and it is the largest item here. 2.3 defines MTL in one prose clause and never writes the total loss; names eight balancers in eight sentences of identical shape with no taxonomy; credits almost no lineage; and never defines what conflict IS, which is what PCGrad, CAGrad and Aligned-MTL all act on. That last gap is why Chapter 6's +0.001 cosine lands with no definition behind it.
- **PART 1 OF FOUR IS NOW SATISFIED, by the same concurrent edit.** The MTL objective he said was missing is now written: `eq:fund:mtl-total`, a weighted sum over K tasks, with the explicit statement that every balancer named next is a different answer to how the weights are set. **The other three parts are still open:** the balancers are still eight sentences of identical shape with no taxonomy (no grouping into loss-weighting versus gradient-surgery), the lineage is still uncredited, and gradient conflict is still not defined in the CHAPTER's prose. On that last point the concurrent edit registered `gradient conflict` in `GLOSSARY.md` with the cosine definition and a pointer to `yu2020pcgrad` Def. 1, so the definition exists in the registry but not yet where the reader meets the concept.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** 2_fundamentals.tex:383-508 -> 2.3
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`
### GER-10 — the fundamentals need a logical narrative built on formal definition blocks

- **Reviewer:** Germano, **verbal**, transcribed by the author. The wording below is the author's paraphrase, not Germano's own words.
- **Quote:** none — he described the passage instead of quoting it: the chapter needs formal definition blocks
- **Live-source status:** **paraphrase** (no quoted string to locate) — `not located`.
- **What he asks:** the chapter needs formal definition blocks
- **My take:** agree, as a drafting principle. This is the synthesis of his other points, and the comparative evidence agrees: our Ch.2 has 5 sections and ZERO subsections; the approved same-advisor precedent (Viegas) has 5 sections and 19 subsections at similar length. Adding two heading levels is what gives GER-08 and GER-09 somewhere to go.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** whole chapter
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`
### GER-11 — the task non-conflict finding needs stronger evidence, and generalizes into future work

- **Reviewer:** Germano, **verbal**, transcribed by the author. The wording below is the author's paraphrase, not Germano's own words.
- **Quote:** none — he described the passage instead of quoting it: non-conflict finding: future work + thin evidence
- **Live-source status:** **paraphrase** (no quoted string to locate) — `not located`.
- **What he asks:** non-conflict finding: future work + thin evidence
- **My take:** agree on both halves. The non-conflict evidence is thinner than the claim: one mean (+0.001), four seeds, four Gowalla states of which GA is not one of the six datasets, taken during development on an earlier data preparation, with no spread and no Istanbul. A mean cannot distinguish 'consistently orthogonal' from 'strongly conflicting in both directions and cancelling'. Either strengthen it or downgrade the sentence.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** 6_conclusion.tex + Appendix F
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`

## Autor  (1 itens)
### AUT-01 — does the MTL fundamentals need Pareto optimality

- **Reviewer:** the author, written (added under "Add by author after the last reviewers")
- **Quote:** "On the MTL fundamentals that we need to improve do we talk about the optimality of pareto, and do we need to talk about it ? I have a feeling that since we talk a bit of the balancers we need at least breif take about this."
- **Live-source status:** not applicable — a question about content that is missing, not a quoted passage.
- **PARTIALLY SATISFIED BY A CONCURRENT EDIT (02:23:31, uncommitted, not mine).** `2_fundamentals.tex` now carries the total-loss equation `eq:fund:mtl-total`, definitions of Pareto dominance and Pareto optimality, the Pareto-stationary distinction, the per-method guarantee levels for Nash-MTL, CAGrad, Aligned-MTL and PCGrad, and the sentence that this dissertation claims no Pareto property. Measured: 2 'Pareto dominance', 7 'Pareto optimal', 8 'Pareto-stationary', 1 'claims no Pareto'. `GLOSSARY.md` gained the four matching registry rows at 02:11:37, which closes PENDENCIAS_RESOLVIDOS 2.12 (arquivado 2026-08-02) by option (a). So your instinct was right and the work is largely done; what remains is your approval of the four PT renderings, three of which that edit itself flags as proposed rather than settled.
- **My take:** agree it needs a brief treatment. The author's own added question: does the MTL fundamentals need Pareto optimality. Since 2.3 names gradient-surgery balancers, and MGDA/CAGrad/Nash-MTL are all argued in terms of Pareto-stationary points, the concept is already implicit. Note 'Pareto-stationary point' is ALREADY in the prose and is PENDENCIAS_RESOLVIDOS 2.12 (arquivado 2026-08-02) (unregistered in the fail-closed GLOSSARY), so this item and 2.12 are the same decision.
- **Disposition:** **I DECIDE** — options and costs in `PENDENCIAS.md` §6
- **Where it renders if applied:** 2_fundamentals.tex 2.3
- **Probe in `check_audit_claims.py`:** none yet. A probe lands in the same commit as the fix, never as a later tidy-up (GUARDRAILS §4b V15).
- **Build commit the measurement was taken against:** `d4078c75`

---

## 4 · Ledger de fontes — toda referencia tocada nesta rodada

Nove referencias. Para cada uma: identificador, onde foi aberta NESTA sessao, os atributos copiados da
fonte de registro, a alegacao especifica que ela sustentaria, e se essa alegacao foi **localizada** no
texto. Uma referencia so entra em prosa quando as tres condicoes do `AGENT_GUARDRAILS` §1 valem.

### `bruna2014spectral`

- **Obra:** Bruna, Zaremba, Szlam, LeCun, Spectral Networks and Locally Connected Networks on Graphs
- **Identificador:** arXiv:1312.6203v3
- **Aberta em:** arXiv API export.arxiv.org/api/query?id_list=1312.6203, this session
- **Atributos:** title, 4 authors, published 2013-12-21, v3 updated 2014-05-21, primary cs.LG, comment '14 pages'. No DOI and no journal_ref in the arXiv record.
- **Alegacao:** convolution can be defined on a graph through the graph Laplacian
- **Localizada:** abstract, sentence 3: 'we propose two constructions, one based upon a hierarchical clustering of the domain, and another based on the spectrum of the graph Laplacian.'
- **Veredito:** ADMISSIBLE for GER-01
- **[VERIFY] / nota:** Cite as ICLR 2014 only if the ICLR record is opened; the arXiv record carries no journal_ref, so the safe entry is the arXiv one.

### `scarselli2009gnn`

- **Obra:** Scarselli, Gori, Tsoi, Hagenbuchner, Monfardini, The Graph Neural Network Model
- **Identificador:** DOI 10.1109/tnn.2008.2005605
- **Aberta em:** Crossref api.crossref.org/works/... + OpenAlex works/doi:..., this session
- **Atributos:** IEEE Transactions on Neural Networks 20(1):61-80, issued 2009-01, journal-article, ISSN 1045-9227/1941-0093. FIVE authors from Crossref: F. Scarselli, M. Gori, Ah Chung Tsoi, M. Hagenbuchner, G. Monfardini.
- **Alegacao:** this paper defined the graph neural network model class
- **Localizada:** abstract (via OpenAlex inverted index): 'In this paper, we propose a new neural network model, called graph neural network (GNN) model, that extends existing neural network methods for processing the data represented in graph domains.'
- **Veredito:** ADMISSIBLE for GER-01
- **[VERIFY] / nota:** CLOSES the prior audit's open [VERIFY] on the author list: Crossref returns all five including Monfardini, so the earlier four-author read was a truncated fetch on its side, not a defect in the paper record. YEAR DISCREPANCY RECORDED: Crossref issued=2009-01, OpenAlex publication_year=2008, DOI slug carries 2008. Use 2009 (the issue of record, consistent with vol 20 iss 1 pp. 61-80).

### `wang2025hamtl`

- **Obra:** Wang, Chen, Liu, Zhang, Wu, Cui, Hu, Hierarchy aware-based multi-task learning for user location prediction
- **Identificador:** DOI 10.1007/s11227-025-07643-7
- **Aberta em:** Crossref (attributes) + OpenAlex (attributes) + Semantic Scholar (attributes) + Unpaywall via fetch_article_fulltext, this session. ABSTRACT NOT OPENED.
- **Atributos:** The Journal of Supercomputing 81(11), article 1196, issued 2025-07-29, journal-article, ISSN 1573-0484. SEVEN authors per Crossref AND Semantic Scholar; OpenAlex lists six and mangles the second to 'M.'. The committed bib entry's seven-author list MATCHES Crossref exactly.
- **Alegacao:** whether it treats a region-like unit as a co-equal END TARGET (the claim FAB-28's novelty sentence turns on)
- **Localizada:** NOT LOCATED. No abstract in Crossref or OpenAlex; oa_status=closed; the configured Springer key returns 401 on meta/v2, metadata and meta/v1; link.springer.com 303-redirects to idp.springer.com (authentication). Semantic Scholar returns only a machine-generated tldr, barred by R5.
- **Veredito:** INADMISSIBLE for any claim. Attributes are verified and correct in the bib; the CLAIM is not.
- **[VERIFY] / nota:** FAB-28 is BLOCKED on this. Do not cite it for the absence claim, and do not weaken 2.3's novelty sentence on the strength of its title either.

### `Zhang2020`

- **Obra:** Zhang, Sun, Zhang, Lei, Li, Wu, An Interactive Multi-Task Learning Framework for Next POI Recommendation with Uncertain Check-ins
- **Identificador:** DOI 10.24963/ijcai.2020/491
- **Aberta em:** OpenAlex works/doi:..., this session
- **Atributos:** IJCAI 2020, conference-paper, 6 authors.
- **Alegacao:** an MTL-for-POI framework proper (iMTL)
- **Localizada:** abstract: 'we propose a novel interactive multi-task learning (iMTL) framework to better exploit the interplay...' — targets next POI recommendation under uncertain check-ins.
- **Veredito:** ADMISSIBLE as an MTL-for-POI example; CLOSES the prior audit's second open [VERIFY].

### `Halder2021`

- **Obra:** Halder, Lim, Chan, Zhang, Transformer-Based Multi-task Learning for Queuing Time Aware Next POI Recommendation
- **Identificador:** DOI 10.1007/978-3-030-75765-6_41
- **Aberta em:** OpenAlex, this session
- **Atributos:** PAKDD 2021 (LNCS), conference-paper, 4 authors.
- **Alegacao:** transformer MTL for POI; auxiliary-task pattern
- **Localizada:** TITLE ONLY. OpenAlex returned an empty abstract.
- **Veredito:** attributes admissible; claim NOT located
- **[VERIFY] / nota:** Citable for existence/attribution, NOT for a characterization beyond its title.

### `Halder2022`

- **Obra:** Halder, Lim, Chan, Zhang, POI recommendation with queuing time and user interest awareness
- **Identificador:** DOI 10.1007/s10618-022-00865-w
- **Aberta em:** OpenAlex, this session
- **Atributos:** Data Mining and Knowledge Discovery 36, 2022, article, 4 authors.
- **Alegacao:** journal extension; adds user interest and queuing time
- **Localizada:** abstract present (1,987 chars) and read: 'Prior studies... do not pay attention to user personal interests... Besides user interests, queuing time also play...'
- **Veredito:** ADMISSIBLE

### `Xu2023`

- **Obra:** Xu, Chen, Gong, Liu, Yu, Nie, TME: Tree-guided Multi-task Embedding Learning towards Semantic Venue Annotation
- **Identificador:** DOI 10.1145/3582553
- **Aberta em:** OpenAlex, this session
- **Atributos:** ACM Transactions on Information Systems 41(4), 2023, article, 6 authors.
- **Alegacao:** already cited in 2.1 for static category classification, but it IS a multi-task method and 2.3 never says so
- **Localizada:** abstract present (1,354 chars) and read; it is about venue category annotation from check-ins. The MULTI-TASK characterization is in the title ('Multi-task Embedding Learning'); the abstract text read did not restate it in the portion retrieved.
- **Veredito:** ADMISSIBLE for the MTL characterization on the strength of the title plus the ACM record
- **[VERIFY] / nota:** Note GLOSSARY bans 'venue' in our own prose; the paper's title keeps it, quoted.

### `kohavi1995crossval`

- **Obra:** Kohavi, A Study of Cross-Validation and Bootstrap for Accuracy Estimation and Model Selection
- **Identificador:** committed entry has NO DOI: booktitle 'Proc. IJCAI', 1995, vol 14, pp. 1137-1143
- **Aberta em:** NOT OPENED this session
- **Atributos:** as committed in references.bib
- **Alegacao:** stratified k-fold cross-validation (the backbone of the validation protocol)
- **Localizada:** NOT LOCATED this session
- **Veredito:** UNCHANGED from the prior audit's PLAUSIBLE grade
- **[VERIFY] / nota:** M8 stays open. I did not attempt it: it is a Recommended item the prior audit already graded, and re-opening it was not needed for any decision in this pass.

### `wongso2025massivesteps`

- **Obra:** Wongso, Xue, Salim, Massive-STEPS: Massive Semantic Trajectories for Understanding POI Check-ins
- **Identificador:** arXiv:2505.11239v3
- **Aberta em:** arXiv API, this session; plus a Crossref bibliographic title search
- **Atributos:** v1 2025-05-16, v3 updated 2026-02-09. NO arxiv:doi, NO journal_ref, NO comment.
- **Alegacao:** M9 asked whether a peer-reviewed version now exists
- **Localizada:** NO peer-reviewed record found. The arXiv record carries no journal_ref or DOI; a Crossref bibliographic search on the title returned five unrelated works. Semantic Scholar returned HTTP 429 and was not retried.
- **Veredito:** STILL A PREPRINT as of this session
- **[VERIFY] / nota:** M9's recommendation stands: if it is cited as the source of the Istanbul data, the chapter should say it is a preprint. The Crossref negative is weak evidence (title search, not an exhaustive check).
---

## 5 · Bandeiras `[VERIFY]` desta rodada

1. **`wang2025hamtl` — resumo NAO aberto, e e o que decide o FAB-28.** Nenhuma fonte de registro
   entrega o resumo: Crossref e OpenAlex nao tem, `oa_status=closed`, a chave Springer configurada
   devolve 401 em `meta/v2`, `metadata` e `meta/v1`, e `link.springer.com` faz 303 para
   `idp.springer.com` (autenticacao). O Semantic Scholar oferece um `tldr` **gerado por modelo**, que a
   regra R5 proibe usar como fonte. Os ATRIBUTOS estao verificados e a entrada no `.bib` bate com o
   Crossref (sete autores). A ALEGACAO nao esta.
2. **Ano do `scarselli2009gnn`:** Crossref diz `issued 2009-01` (vol 20, num 1, pp. 61-80), OpenAlex diz
   `publication_year 2008`, e o proprio DOI carrega 2008. Adotei **2009**, o fasciculo de registro.
   Registrado em vez de silenciado.
3. **`bruna2014spectral` e ICLR 2014:** o registro do arXiv nao tem `journal_ref` nem DOI. A entrada
   segura e a do arXiv; citar como ICLR exige abrir o registro da ICLR, que eu nao abri.
4. **Convencao de media do F1 do sweep do HGI** (macro vs ponderada): continua sem resolucao no fonte,
   e o `[VERIFY]` original esta la. Ela precisa ser fixada antes de esses numeros aparecerem em
   qualquer lugar, inclusive depois de uma mudanca de capitulo (GER-03).
5. **O cosseno +0,001:** nao rederivei o valor, a dispersao, nem a procedencia alem do fonte do Cap. 6 e
   dos comentarios dele (GER-11).
6. **`kohavi1995crossval`** continua com a nota PLAUSIBLE da auditoria anterior. Nao tentei reabrir: e um
   item "Recomendado" que nenhuma decisao desta rodada precisava.
7. **Massive-STEPS continua preprint** (arXiv:2505.11239v3, atualizado em 2026-02-09; sem `journal_ref`,
   sem DOI). A busca no Crossref por titulo nao achou versao revisada, mas e evidencia fraca: uma busca
   por titulo nao e uma verificacao exaustiva, e o Semantic Scholar devolveu HTTP 429 e nao foi repetido.
8. **`Halder2021`:** o OpenAlex devolveu resumo vazio. Citavel por atributo, nao para uma caracterizacao
   alem do que o titulo diz.

---

## 6 · O que a passagem de revisao NAO cobriu

- **Os itens do Fabricio sao sobre quatro arquivos** (`content.tex`, `1_introduction.tex`,
  `2_fundamentals.tex`, `6_conclusion.tex`). Os capitulos 3, 4 e 5 e os apendices nao receberam pontos
  dele nesta rodada, e a ausencia nao e um atestado.
- **Os pontos do Germano sao quase todos sobre §2.2 e §2.3.** §2.1, §2.4 e §2.5 aparecem apenas de
  relance, e §2.4 e onde vivem duas correcoes do Fabricio (FAB-29, FAB-30).
- **A auditoria de 2026-07-28 propos 31 itens de trabalho** (M1-M10, Partes III e V, itens 1-31 da lista
  consolidada) que **nao sao** pontos de revisor e nao receberam ID aqui. Eles seguem validos como
  proposta; tres das medicoes que os sustentam foram refeitas nesta rodada e mudaram (§1).
- **`make selftest` reporta 10 de 14 verificadores como UNPROVEN ou HALF**, com rc=0 porque so tres estao
  na lista REQUIRED. Isso nao e um achado desta rodada, e sim o estado registrado da suite, e vale
  lembrar dele antes de tratar "22 gates verdes" como cobertura.

---

*Medido em 2026-07-30 contra o commit `d4078c75` (`make check` rc=0, 22 gates, lidos direto e nao
por pipe; `make selftest` rc=0). Nada foi aplicado a nenhum capitulo nesta passagem: este arquivo e a
divisao, e §6 do `PENDENCIAS.md` e a fila da sua decisao. Os comandos que produziram cada numero de §1
estao em [`_history/_round9/31_stale_quote_pass.md`](_history/_round9/31_stale_quote_pass.md).*


--- NEW WAVE ---

## Fabricio — `chapters/1_introduction.tex` 
### FAB-32

- **Reviewer:** Fabricio, written
- **Quote:** "visits. The first two studies also use \emph{category classification}, a static task"
- **Live-source status (SEU registro):** **exact** — `chapters/1_introduction.tex:30`.
- **What he asks:** `não falou nada de estudos ainda...falar de outra forma aqui, como: Durante o desenvolvimento da dissertação, também usamos a category classification.....`
- **Author considerations:** Indeed we no metion the studies, I belive that we could take this opotunites to try to finds others contradictions like this one in the introduction and fundamentals, that are the two more proeminets to have ths kind of error
- **Live-source status (RE-MEDIDO por mim):** **exata**, mas a coordenada andou: vive hoje em
  `chapters/1_introduction.tex:90` cru, que e `:28` com os comentarios removidos — a contagem que voce usou.
  A deriva vem de uma passagem paralela da rodada 13 no mesmo arquivo, nao de erro seu. A citacao esta
  **exata**, palavra por palavra.
- **Claude take:** **Voce esta certo, e este item e o mesmo defeito do FAB-33.** Medido, nao suposto: os
  tres estudos sao apresentados ao leitor pela primeira vez em `:125` ("The three studies conducted in
  this dissertation answer this question in sequence"), na §1.2. A frase marcada esta em `:90`, na §1.1 —
  trinta e cinco linhas e uma fronteira de secao **antes**. Entao "the first two studies" enderecava um
  conjunto que o leitor ainda nao conhece. E exatamente a classe de defeito que o redesenho do Cap. 2
  removeu nesta rodada, e a mesma que a sua propria edicao da Definicao 2.2 precisou corrigir horas
  antes; as duas caem nela pelo mesmo motivo, que e terem sido escritas de tras para frente.
  **Apliquei na sua forma:** descrever o trabalho em vez de indexar um conjunto nao apresentado.
- **Disposition:** VOCE APLICA (aplicado nesta rodada; nenhuma alegacao muda, so a ordem de apresentacao)
- **Where it renders:** §1.1, p. 1 do `main.pdf` (conferido no PDF renderizado, nao no fonte)
- **Probe:** `R13-fab32` (a forma nova) + `R13-fab32b` (proibe a volta da antiga)
- **Build commit:** `fd94d0a2`

### FAB-33

- **Reviewer:** Fabricio, written
- **Quote:** "The task pair changes in the final study, as explained in Section~\ref{sec:intro:arc}."
- **Live-source status (SEU registro):** **exact** — `chapters/1_introduction.tex:33`.
- **What he asks:** `mesmo coisa, não falou nada de estudo...mudar aqui`
- **Author considerations:** Same problem that the previus review
- **Live-source status (RE-MEDIDO por mim):** **exata**, e a frase **quebra em duas linhas** no fonte
  (`:92-93` cru; `:30` com comentarios removidos). Registro isso porque a minha primeira medicao reportou
  o quote como DESAPARECIDO, e o errado era o meu instrumento: um `grep` de uma linha nao ve uma frase que
  quebra depois de "The task". A sua citacao esta exata.
- **Claude take:** **Certo, e e a segunda ocorrencia do FAB-32 e nao um item separado.** A mesma medicao
  vale: "the final study" chegava antes de existir um estudo para o leitor. Duas coisas que eu
  deliberadamente **nao** fiz. Nao removi o ponteiro para a §1.3 (`sec:intro:arc`), porque e la que a
  variacao do par de tarefas e de fato explicada e apagar o ponteiro trocaria um defeito por outro. E nao
  trouxe a explicacao para ca: a §1.1 esta apresentando as tarefas, e o arco e assunto da §1.3.
- **Disposition:** VOCE APLICA (aplicado nesta rodada)
- **Where it renders:** §1.1, p. 1 do `main.pdf` (conferido no render)
- **Probe:** `R13-fab33` (a forma nova) + `R13-fab33b` (proibe a volta da antiga)
- **Build commit:** `fd94d0a2`


### FAB-34

- **Reviewer:** Fabricio, written
- **Quote:** "here the category space has seven classes, and a region is a census tract in the United States or a \emph{mahalle} in Istanbul."
- **Live-source status (SEU registro):** **exact** — `chapters/1_introduction.tex:137`.
- **What he asks:** On the word ` \emph{mahalle}`: "o que é isso? defina"
- **Author considerations:** This is a census tract for istambu, but is the name of theri censu trac search if needed
- **Live-source status (RE-MEDIDO por mim):** **exata**, quebrando em duas linhas em
  `chapters/1_introduction.tex:301-302` cru (`:135` com comentarios removidos).
- **Claude take:** **Certo — e a glosa tinha de vir de uma fonte, nao de mim.** Medido primeiro: e a
  **unica** ocorrencia viva de `mahalle` na introducao, e portanto o primeiro uso do capitulo, sem
  nenhuma glosa. O Cap. 2 **ja** glosa ("a \emph{mahalle}, a municipal neighborhood",
  `2_fundamentals.tex:1450`), mas isso esta 1.148 linhas adiante e em outro capitulo, e a `WRITING_LAW`
  §1 pede a definicao no **primeiro** uso. A lista de siglas tambem nao e a casa dela: aquele bloco
  carrega CBIC, Check2HGI, CoUrb, DGI, FiLM, HGI, LBSN, MobiWac, MTL, POI, SBRC e TOST — conferido — e
  `mahalle` nao e sigla.
  **UMA CORRECAO A SUA PROPRIA NOTA, e e por isso que a sua instrucao de buscar estava certa.** Voce
  escreveu "This is a census tract for istambul". Nao e, e a diferenca importa para o texto: o mahalle e
  a **menor unidade da administracao local turca**, abaixo do distrito, chefiada por um *muhtar* eleito.
  E equivalente ao census tract apenas no sentido de ser a menor unidade areal disponivel, **nao** no de
  ser uma unidade **estatistica** — o census tract e desenhado pelo recenseamento para agregar populacao,
  o mahalle e uma unidade de **governo**. Por isso o texto diz "administrative unit" em vez de sugerir
  que os dois sejam a mesma especie de objeto, e o aposto de duas palavras repete a formulacao que o
  Cap. 2 ja usa, para os dois capitulos nao divergirem.
- **Disposition:** VOCE APLICA (aplicado nesta rodada), com **uma correcao factual a sua consideracao**
- **Where it renders:** §1.4 Scope and assumptions, `main.pdf` (conferido no render)
- **Probe:** `R13-fab34`
- **Build commit:** `fd94d0a2`
 
