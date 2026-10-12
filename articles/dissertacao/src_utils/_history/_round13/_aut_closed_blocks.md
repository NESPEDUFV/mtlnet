# _aut_closed_blocks.md — os 26 blocos `AUT-` fechados na rodada 13, verbatim

> Preservados em 2026-08-04 ao remove-los do `PENDENCIAS.md` §4. Estes sao os blocos de auditoria
> COMPLETOS, com a evidencia que a tabela resumida do `PENDENCIAS_RESOLVIDOS.md` nao carrega:
> DOIs verificados, file:line de cada defeito, os comandos de medicao, e as sobreposicoes.
>
> Por que existe: comprimir e uma afirmacao de que nada foi perdido, e medindo depois da remocao,
> 32 numeros e 20 caminhos entre backticks do texto removido nao apareciam em nenhum outro arquivo.
> A tabela do arquivo guarda o ruling e o commit; este arquivo guarda a prova.
>
> 26 blocos: AUT-03, AUT-04, AUT-05, AUT-06, AUT-07, AUT-10, AUT-11, AUT-12, AUT-13, AUT-15, AUT-16, AUT-17, AUT-18, AUT-19, AUT-20, AUT-21, AUT-22, AUT-23, AUT-24, AUT-25, AUT-27, AUT-28, AUT-30, AUT-31, AUT-33, AUT-34

---

### AUT-03 — padronizacao dos termos tecnicos, e tres citacoes danificadas

- **§4 item:** 2
- **Source status:** [N/A] como citacao (pedido de varredura), mas a varredura achou tres ancoras [CHANGED] que ninguem
  pediu.
- **Minha leitura e avaliacao:** **A sua premissa esta metade certa e metade errada, e a varredura que ja foi feita na
  direcao que voce pediu causou dano.** Certo: `multi-task` em prosa viva = **0** (as 19 ocorrencias estao todas em
  comentario `%` ou nos titulos alternativos comentados em `preamble.tex`:201-206), e o titulo de registro do Caruana e
  mesmo `Multitask Learning` sem hifen (DOI `10.1023/A:1007379606734`, PDF da Springer aberto, pagina 1). Errado: **o
  APA nao governa este documento** (deposito ABNT, classe `abntex2`, `.bst` numerico ABNT) e a regra do APA nao e "sem
  hifen", e sim a regra do modificador composto, a mesma do IEEE (manual do IEEE aberto, paginas 21-27). E na literatura
  que voce cita a forma hifenizada e a **maioria**: 6 de 7 titulos de balanceadores verificaveis usam `Multi-Task`/
  `Multi-task`. **O achado grave:** a normalizacao apagou o hifen DENTRO de tres citacoes textuais. Ver §4.1.
- **Plano de resolucao proposto:** Quatro decisoes, todas pequenas, detalhadas em §4.1: (1) restaurar o hifen nas tres
  citacoes (3 strings, 3 arquivos); (2) registrar a normalizacao `Multi-Task`->`Multitask` da prosa reproduzida no
  Apendice B, seguindo o precedente `MTLNet`->`MTLnet` que ja esta la; (3) registrar a regra de hifen de POI no GLOSSARY
  (uma linha, so voce pode); (4) implementar o probe `R9-poihyphen`, reservado desde o FAB-20 e ainda inexistente.
  **Nenhuma edicao de prosa e devida pela hifenizacao em si:** a arvore ja esta consistente sob a regra correta, 22 de
    22.
- **Sobreposicoes e dependencias:** **FAB-20 e FAB-25 sao o mesmo trabalho para POI** (ambos ja [YOU APPLY], probe
  `R9-poihyphen` reservado). As contagens do FAB-20 (11/8) estao obsoletas: hoje sao 13/9. O AUT-26 (renomear o modelo)
  toca os mesmos arquivos de nome.
- **Disposicao alvo:** **[I DECIDE]** — o seu warrant declarado (APA, Caruana) esta errado de um jeito que muda o que
  deve ser feito, e ha dano de citacao para reparar.
- **Onde renderiza:** titulo do Cap.3 p.33; titulo do Cap.5 p.64; tabela de errata p.48; bibliografia p.88
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-04 — "while place categories provide the semantic information..." parece solta

- **§4 item:** 3
- **Source status:** [CHANGED] — a sua citacao e do PDF (onde `\cite{Xu2023}` imprime `[4]`); a frase existe em
  `1_introduction.tex`, com a referencia por chave. Conteudo identico.
- **Minha leitura e avaliacao:** Concordo com a leitura. A frase fecha um periodo que ja mudou de assunto duas vezes:
  comeca em planejamento urbano e analise de doencas, e a oracao das categorias entra sem conector que explique por que
  ela pertence ali. E uma frase de ligacao que nao liga.
- **Plano de resolucao proposto:** Uma frase, reescrita para ligar a categoria ao que vem depois (as duas tarefas) em
  vez de pendura-la no final do periodo anterior. Sem numero novo, sem citacao nova: `Xu2023` continua.
- **Sobreposicoes e dependencias:** AUT-05 (a frase seguinte, mesmo paragrafo) — resolver os dois juntos, e um paragrafo
  so.
- **Disposicao alvo:** **[YOU APPLY]**
- **Onde renderiza:** §1.1 p.13
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-05 — "neighboring geospatial tasks" no primeiro paragrafo

- **§4 item:** 4
- **Source status:** [CHANGED] — mesma razao do AUT-04 (`[5, 6]` no PDF = `\cite{mai2023...,wu2024torchspatial}` no
  fonte); a frase esta viva, e as palavras "species recognition and remote-sensing classification" tambem.
- **Minha leitura e avaliacao:** Concordo. Voce esta construindo o problema para o leitor e a frase salta para
  metodologia do segundo estudo, com um termo ("neighboring geospatial tasks") que o texto nunca define. Nao e falso, e
  prematuro. O lugar natural desse conteudo e §2.2, onde os codificadores espaciais sao apresentados.
- **Plano de resolucao proposto:** Duas saidas, ambas pequenas: (A) cortar as duas frases do §1.1 e verificar que
  §2.2.3.1 ja carrega o conteudo (carrega: cita os mesmos dois trabalhos); (B) manter uma frase, sem o termo
  "neighboring geospatial tasks", nomeando o que sao (reconhecimento de especies, classificacao de sensoriamento remoto)
  e por que importam. Recomendo (A): o §1.1 fica mais curto e nada se perde.
- **Sobreposicoes e dependencias:** AUT-04 (mesmo paragrafo). AUT-22 (o conteudo de codificadores em §2.2.3.1).
- **Disposicao alvo:** **[YOU APPLY]** — se voce preferir (B), viraria [I DECIDE]; a recomendacao e (A).
- **Onde renderiza:** §1.1 p.13
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-06 — "one model may serve both tasks" depois de tres tarefas definidas

- **§4 item:** 5
- **Source status:** [EXACT] — `1_introduction.tex`, prosa viva, palavra por palavra.
- **Minha leitura e avaliacao:** Concordo, e o defeito e logico, nao estilistico. O paragrafo define **tres** tarefas
  (proxima categoria, proxima regiao, classificacao estatica) e a frase seguinte diz "both tasks" sem dizer quais duas.
  O leitor tem de adivinhar que "both" exclui a estatica. A sua reescrita proposta resolve isso ao dizer que as tarefas
  citadas consomem o mesmo historico.
- **Plano de resolucao proposto:** Uma frase. Nomear as duas tarefas explicitamente em vez de "both", e manter o motivo
  (o mesmo historico de visitas alimenta as duas). Cuidado com o registro: a sua versao rascunho tem "consumes" e "unify
  model"; a redacao final usa os nomes canonicos do GLOSSARY ("next category", "next region", "joint model").
- **Sobreposicoes e dependencias:** AUT-07 (a nomenclatura da tarefa estatica no mesmo paragrafo) — a mesma frase
  resolve os dois se a correcao nomear a estatica pelo nome canonico.
- **Disposicao alvo:** **[YOU APPLY]**
- **Onde renderiza:** §1.1 p.13
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-07 — "static place categories" versus "category classification"

- **§4 item:** 6
- **Source status:** [EXACT] nas duas ancoras. `1_introduction.tex` define *category classification, a static task that
  predicts the category of a POI held out from classifier training* e, mais adiante no mesmo capitulo, escreve *predicts
  static place categories and the next category in a sequence*.
- **Minha leitura e avaliacao:** **Confirmado, e e mais grave do que voce colocou.** Nao e so confusao para o leitor
  novato: `category classification` e o nome **registrado** no GLOSSARY §1, e `static place categories` nao esta no
  registro. A regra fail-closed do GLOSSARY diz que um termo fora do registro nao pode ser usado, e WRITING_LAW §2
  proibe rotacao de sinonimo. Sao duas violacoes na mesma pagina, e voce achou lendo.
- **Plano de resolucao proposto:** Uma substituicao: `static place categories` -> `category classification` (ou "the
  static category of a place", se a frase precisar de forma nominal). Uma ocorrencia. Depois varrer o resto da arvore
  pelo mesmo padrao antes de fechar, porque uma so ocorrencia e exatamente o caso que a amostragem perde.
- **Sobreposicoes e dependencias:** AUT-06 (mesma regiao do texto). AUT-32 (a tarefa estatica na abertura do Cap.6).
- **Disposicao alvo:** **[YOU APPLY]** — troca de termo por nome canonico registrado, sem juizo de conteudo.
- **Onde renderiza:** §1.1 p.13; §1.2 p.13-14
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-10 — "hard parameter sharing" usado na introducao sem explicacao

- **§4 item:** 9
- **Source status:** [N/A] como citacao (pedido de avaliacao); as ocorrencias sao [EXACT].
- **Minha leitura e avaliacao:** **Confirmado.** `hard parameter sharing` aparece tres vezes no Cap.1
  (`1_introduction.tex`:131, :168, :302) sem nenhuma glosa. E **e** definido, mas depois: no Cap.2 (§2.3.1, p.25) e, em
  prosa publicada, no Cap.3 (`3_cbic/basis.tex`:31, "where a common set of hidden layers is shared"). Entao o defeito
  nao e "nunca explicamos", e "usamos antes de definir", que e a regra do WRITING_LAW §1 (definir uma vez, no primeiro
  uso). A sua propria glosa proposta esta correta e e curta.
- **Plano de resolucao proposto:** Uma oracao aposta no primeiro uso do Cap.1, glosando o termo (um tronco de camadas
  comum as tarefas, que se divide apenas nas saidas), e depois usar o termo sem repetir a glosa. O Cap.2 mantem a
  definicao formal. Nenhuma citacao nova: `caruana1997multitask` ja esta no lugar.
- **Sobreposicoes e dependencias:** AUT-11 (o mesmo termo no objetivo 1). Se a glosa entrar no Cap.1, o objetivo 1 nao
  precisa de outra.
- **Disposicao alvo:** **[YOU APPLY]**
- **Onde renderiza:** §1.2 p.13-14 (primeiro uso, `1_introduction.tex`:131)
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-11 — o objetivo 1 poderia incluir "como construir" um modelo MTL

- **§4 item:** 10
- **Source status:** [CHANGED] — sua citacao e do PDF ("(Chapter3)"); o fonte usa `\ref{ch:cbic}`. Texto identico.
- **Minha leitura e avaliacao:** Discordo em parte, e a decisao e sua. O que voce propoe acrescenta um **segundo**
  objetivo (como um modelo MTL pode ser construido e funcionar no dominio de POI) a um item que hoje declara um objetivo
  avaliativo. O `NORTH_STAR` §6 beat 5 fixa os objetivos em 1:1 com os capitulos, e o Cap.3 e um estudo avaliativo, nao
  um estudo de construcao. Alargar o objetivo 1 muda a estrutura, nao a redacao. **Porem** ha um argumento a seu favor
  que o item nao diz: o MTLnet **e** uma contribuicao de software e hoje isso aparece na secao de Contribuicoes, nao nos
  objetivos.
- **Plano de resolucao proposto:** Duas saidas: (A) manter o objetivo 1 como esta e deixar a construcao onde ela ja esta
  (Contribuicoes, bullet Software) — custo zero; (B) reescrever o objetivo 1 para nomear projeto **e** avaliacao, o que
  obriga a reler os quatro objetivos para manter o 1:1 e a simetria. Recomendo (A).
- **Sobreposicoes e dependencias:** AUT-14 (a secao de Contribuicoes, onde a construcao ja e reivindicada). AUT-10 (o
  mesmo termo).
- **Disposicao alvo:** **[I DECIDE]** — mudanca estrutural nos objetivos, e eu discordo da premissa.
- **Onde renderiza:** §1.3 p.15
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-12 — o objetivo 4 aponta para o Capitulo 6 e deveria ser o 5

- **§4 item:** 11
- **Source status:** [CHANGED] — sua citacao e do PDF, com as palavras coladas ("Consolidatetheevidence..."); o fonte
  esta correto em `1_introduction.tex`:176-178.
- **Minha leitura e avaliacao:** **Confirmado, e e um defeito real que passa por todos os gates.** O objetivo 4 diz "the
  protocol used in **the final study** (Chapter~\ref{ch:conclusion})", e `ch:conclusion` resolve para o Cap.6, que nao e
  um estudo. O estudo final e o Cap.5. Como o `\ref` **resolve**, o build reporta 0 referencias indefinidas, o lint L4
  passa, e o PDF imprime "(Chapter 6)" com confianca. Verificado no PDF renderizado, p.15. **Uma ressalva que faz disso
  uma decisao e nao uma troca:** o objetivo 4 tambem pode ser lido como "a consolidacao acontece na Conclusao", e nesse
  caso o errado e a redacao, nao a referencia. As duas leituras pedem edicoes diferentes.
- **Plano de resolucao proposto:** (A) Se o objetivo e o protocolo: `ch:conclusion` -> `ch:mobiwac`, um token. (B) Se o
  objetivo e a consolidacao: manter a referencia e trocar "used in the final study" por algo que descreva consolidacao.
  Recomendo (A), porque a oracao nomeia o protocolo (validacao cruzada com usuarios disjuntos, teste de significancia,
  nao-inferioridade), e esse protocolo e do Cap.5.
- **Sobreposicoes e dependencias:** Nenhuma. Item isolado, um token.
- **Disposicao alvo:** **[I DECIDE]** — uma linha sua escolhe entre (A) e (B); depois disso e trivial.
- **Onde renderiza:** §1.3 p.15
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-13 — "The joint setting imposes a single-model constraint" — que joint setting?

- **§4 item:** 12
- **Source status:** [CHANGED] — a frase viva ja **nao** diz "joint setting": diz *The joint model operates under a
  single-model constraint: one trained artifact must produce both outputs in one forward pass* (`1_introduction.tex`:
  222-223).
- **Minha leitura e avaliacao:** **A sua objecao ja foi atendida por outra esteira, e exatamente do jeito que voce
  pediu.** O sujeito abstrato sem referente ("the joint setting") virou um sujeito nomeado e registrado ("the joint
  model", que e o nome canonico do GLOSSARY §2). Nao ha nada a fazer alem de confirmar.
- **Plano de resolucao proposto:** Confirmar e fechar. Se voce ainda achar que "single-model constraint" precisa de
  glosa, isso e um item novo e pequeno; a oracao apos os dois-pontos ja funciona como glosa.
- **Sobreposicoes e dependencias:** Nenhuma.
- **Disposicao alvo:** **[YOU APPLY]** — no sentido de fechar como ja satisfeito, com a citacao acima. Nenhuma edicao de
  prosa.
- **Onde renderiza:** §1.4 p.15
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-15 — "mobility is learnable, but it is not a reference point" — a frase invertida

- **§4 item:** 14
- **Source status:** [CHANGED] na versao atual; [GONE] na anterior que voce prefere.
- **Minha leitura e avaliacao:** **Concordo com voce no merito, e a frase viva e melhor do que a que voce citou.** A
  viva diz: *Because this estimate concerns next-location prediction at a coarse spatial resolution, it shows that
  mobility contains learnable regularity but does not provide a reference point for the category and region metrics
  defined in Section~\ref{sec:fund:eval}*. Ou seja, ela **ja** carrega a clausula de escopo ("at a coarse spatial
  resolution") que a sua citacao tinha perdido, e e essa clausula que torna a frase correta. O seu argumento (estudos de
  mobilidade e proximo lugar **podem** servir de referencia para categoria e regiao) e verdadeiro em geral e falso para
  **este numero especifico**: 93 por cento e a previsibilidade potencial do proximo **lugar** em resolucao grosseira, e
  nao limita macro-F1 de categoria nem Acc@10 de regiao. As duas coisas nao se contradizem.
- **Plano de resolucao proposto:** Nenhuma edicao obrigatoria. Se voce ainda quiser o ponto positivo declarado, uma
  frase separada pode dizer que a literatura de proximo lugar fornece a base metodologica para as duas tarefas (o que
  §2.1.2 **ja** diz, p.20), mantendo a frase do 93 por cento como ela esta. Confirmar e fechar.
- **Sobreposicoes e dependencias:** AUT-30 (o mesmo `sec:fund:eval` como destino de referencia).
- **Disposicao alvo:** **[YOU APPLY]** — fechar como ja satisfeito pela clausula de escopo, com a citacao acima.
- **Onde renderiza:** §2.1 p.18
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-16 — "sequenciais" e "estaticas": explicamos antes de usar?

- **§4 item:** 15
- **Source status:** [CHANGED] — a sua citacao ("three experimental tasks, two sequential and one static") nao esta
  viva; o texto vivo inverte a ordem: *This dissertation studies three tasks: one static and two sequential*
  (`2_fundamentals.tex`:49), e ha um `\subsubsection{The three experimental tasks}` (§2.1.1.3, p.19).
- **Minha leitura e avaliacao:** Auditei o seu medo e ele **e** justificado, mas nao onde voce pensou. No Cap.2 a
  distincao esta bem resolvida: a frase de :49 introduz a tipologia antes de usar, e §2.1.1.3 abre com *Three
  definitions separate the targets. The first is static and reads a place; the other two are sequential and read a
  history*, que e uma glosa explicita dos dois adjetivos. O problema e no **Cap.1**: la os termos aparecem sem essa
  glosa, e o leitor encontra "static task" antes de qualquer definicao de "sequential". E o mesmo padrao do AUT-10.
- **Plano de resolucao proposto:** Verificar o primeiro uso no Cap.1 e, se estiver nu, glosar em meia oracao (uma tarefa
  le uma sequencia de visitas, a outra le um lugar). A lista de abreviaturas nao e o lugar, e voce esta certo em
  desconfiar disso: ela nao carrega nenhum dos dois termos, e nao deve.
- **Sobreposicoes e dependencias:** AUT-10 (mesma classe: termo usado no Cap.1 antes de definido no Cap.2). AUT-32 (as
  tres tarefas na abertura do Cap.6).
- **Disposicao alvo:** **[YOU APPLY]**
- **Onde renderiza:** §1.1 p.13; §2.1 p.18; §2.1.1.3 p.19
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-17 — §2.1.1.1 nao explica x_i, H_i, c_p, c_i, r_i

- **§4 item:** 16
- **Source status:** [N/A] como citacao (pedido de avaliacao). E **[GONE] como defeito:** ele foi corrigido por outra
  esteira enquanto voce escrevia.
- **Minha leitura e avaliacao:** **Este item esta resolvido, e eu verifiquei nos dois lugares.** O §2.1.1.1 vivo agora
  abre declarando os conjuntos (*Let $\\mathcal{U}$, $\\mathcal{P}$, $\\mathcal{C}$, and $\\mathcal{R}$ denote the sets
  of users, POIs, category classes, and region classes*), liga a categoria e a regiao ao POI (*Each
  POI $p\\in\\mathcal{P}$ carries a category $c_p\\in\\mathcal{C}$ and lies in a region $r_p\\in\\mathcal{R}$*), e entao
  da os dois blocos de definicao numerados: **Check-in**, que escreve $x_i= (u,p_i,t_i,c_i,r_i)$ e nomeia **cada**
  componente incluindo $c_i=c_{p_i}$ e $r_i=r_{p_i}$, e **Check-in history**, que escreve $H_i$. Confirmado tambem no
  PDF renderizado (p.18), nao so no fonte. Todos os cinco simbolos que voce lista estao ligados.
- **Plano de resolucao proposto:** Confirmar e fechar. Os blocos sao defendidos por probes (`R12-s1bind`, `R12-s2type`,
  `R11-def27`), entao nao regridem em silencio.
- **Sobreposicoes e dependencias:** GER-08 e GER-10 (que pediram exatamente estes blocos de definicao formal e estao com
  voce em aberto) — **resolver o AUT-17 e reconhecer que o trabalho do GER-08 ja foi feito**. AUT-27 (o simbolo que
  **continua** sem explicacao e o $\\mathcal{L}_k$).
- **Disposicao alvo:** **[YOU APPLY]** — fechar como ja satisfeito, com as duas definicoes como evidencia.
- **Onde renderiza:** §2.1.1.1 p.18
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-18 — listar as sete categorias e nomear os datasets numa definicao tecnica

- **§4 item:** 17
- **Source status:** [CHANGED] — a frase viva nao e a que voce citou. Hoje: *All three studies use seven categories:
  Community, Entertainment, Food, Nightlife, Outdoors, Shopping, and Travel. For the region task, the target is a census
  tract in the United States datasets and a \\emph{mahalle} in Istanbul.* Esta em §2.1.1.3 (p.19), nao em §2.1.1.1.
- **Minha leitura e avaliacao:** Concordo com a primeira metade e discordo em parte da segunda. **Primeira:** listar as
  sete classes dentro de uma definicao formal mistura a definicao da tarefa com o instanciamento dos dados, e o seu
  argumento e correto — o modelo aceita N categorias, sete e uma propriedade do dado. **Segunda:** os nomes das unidades
  (setor censitario, mahalle) nao sao so dados, sao o que torna "regiao" concreto; sem eles o leitor fica sem referente
  ate §2.4 (p.28). Este e literalmente o mesmo argumento que ja esta em aberto nos **FAB-14 e FAB-15**, onde eu tambem
  discordei e a decisao ficou com voce.
- **Plano de resolucao proposto:** Uma edicao coordenada com os FAB-14/FAB-15, porque sao a mesma decisao em dois
  capitulos: (A) mover a enumeracao das sete para §2.4.1 e deixar em §2.1.1.3 apenas a cardinalidade ("seven top-level
  classes"); (B) mover tambem as unidades geograficas; (C) manter tudo. Recomendo (A) sem (B).
- **Sobreposicoes e dependencias:** **FAB-14 e FAB-15 sao a mesma decisao** (as sete classes e o par setor
  censitario/mahalle na introducao). AUT-02 (a mesma lista, no Resumo). AUT-31 (a reorganizacao de §2.4, que e o destino
  proposto).
- **Disposicao alvo:** **[I DECIDE]** — decidir junto com FAB-14/FAB-15 numa unica passada, para os tres capitulos nao
  divergirem.
- **Onde renderiza:** §2.1.1.3 p.19; destino proposto §2.4.1 p.29
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-19 — explicar o que e graph infomax em linhas gerais

- **§4 item:** 18
- **Source status:** [N/A] como citacao (pedido de conteudo).
- **Minha leitura e avaliacao:** **Largamente satisfeito, e mais do que voce lembra.** O §2.2.2 (p.21) tem 584 palavras
  e ja explica o mecanismo: que o treino **maximiza a informacao mutua entre representacoes de dois niveis adjacentes da
  hierarquia**, sem avaliar essa quantidade em forma fechada; que um **discriminador bilinear** combina dois embeddings
  por uma matriz de pesos aprendida e passa o resultado por uma **funcao logistica**; e que a perda premia pontuacao
  alta para um par verdadeiro e baixa para um falso. Depois percorre os quatro estagios do HGI. O que **falta** e menor
  do que o item sugere: uma frase de entrada em linguagem simples dizendo o que "infomax" **e** antes de dizer o que ele
  maximiza.
- **Plano de resolucao proposto:** Uma frase no inicio do §2.2.2, antes da cadeia MINE/DIM/DGI, dizendo em palavras
  comuns o objetivo (aprender representacoes fazendo o modelo distinguir um par verdadeiro de um par corrompido, sem
  rotulos). Os termos `bilinear discriminator` e `logistic function` **ja estao registrados** no GLOSSARY §3, entao nao
  ha bloqueio fail-closed.
- **Sobreposicoes e dependencias:** GER-02, GER-04, GER-05, GER-07 (todos sobre a mesma subsecao e ja em aberto com
  voce). **AUT-20 esta na primeira frase do corpo desta mesma subsecao**, entao as duas edicoes se tocam.
- **Disposicao alvo:** **[YOU APPLY]** — uma frase didatica, sem afirmacao nova e sem citacao nova.
- **Onde renderiza:** §2.2.2 p.21
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-20 — "trained without category or region labels" — a frase de honestidade

- **§4 item:** 19
- **Source status:** [EXACT] — `2_fundamentals.tex`:382, primeira frase do corpo do §2.2.2.
- **Minha leitura e avaliacao:** **Confirmado que a frase esta forte demais, e a sua premissa esta certa no essencial e
  errada sobre onde o rotulo entra.** Verificado no spec E no codigo, nesta sessao. Existem **dois** caminhos de rotulo
  de categoria, nenhum deles no objetivo proprio do HGI:
    1. **Reconstrucao de categoria de POI mascarado, no Check2HGI (Cap.5).** Spec §6.5: amostra 15 por cento dos POIs
       por epoca, zera seus vetores e decodifica so as linhas mascaradas; *"The target for each POI is the mean category
       one-hot vector of all its check-ins"*. Peso **0.3** de cinco termos na perda ativa. Confirmado no codigo
       (`research/embeddings/check2hgi/preprocess.py`, `model/variants.py`, e o `build_design_k_delaunay.py` que passa
       `mae_poi_target_kind="category_aggregate"` — o default do modulo e 0.0, ou seja desligado, **e ele e pedido
       explicitamente**).
    2. **POI2Vec, a montante dos dois:** um termo L2 que aproxima o embedding da categoria do da classe fina, com peso
       `1e-8`. O comentario do proprio codigo chama isso de *"the only explicit category-label path"*. Numericamente
       desprezivel, mas **esta no objetivo**, e a frase e sobre o objetivo. **O que E verdade e o que a frase deveria
       dizer:** nenhum objetivo de representacao le a categoria ou a regiao de uma visita **futura**, que e a protecao
       que importa para vazamento nas tarefas sequenciais. A frase atual promete mais do que isso.
- **Plano de resolucao proposto:** Substituir a afirmacao de **ausencia** por uma afirmacao de **escopo**: nenhum
  objetivo de representacao le o alvo de predicao (a categoria ou a regiao da proxima visita), e dizer que a categoria
  observada da visita atual **e** usada, como feature e num termo auxiliar de reconstrucao. Uma a duas frases. **Isso e
  uma afirmacao nova (C2)** e e exatamente o tipo de mudanca que o WRITING_LAW §3 chama de bug e nao de estilo, entao
  vai para voce com a redacao proposta em `_history/_round13/61_check2hgi_audit.md` § (d).
- **Sobreposicoes e dependencias:** **AUT-08 tem a mesma base factual e vai na direcao contraria** (voce quer dizer que
  o vazamento da categoria atual e desejavel). Resolver um sem o outro produz contradicao no mesmo capitulo. **AUT-21**
  (o quinto termo omitido da perda **e** o ancora POI2Vec). **AUT-23** (as afirmacoes A3, A5 e A11 do §2.2.3.2 sao o
  mesmo excesso). AUT-35 (c) (o vazamento na tarefa estatica).
- **Disposicao alvo:** **[I DECIDE]** — edicao de honestidade sobre o nosso proprio sistema, com afirmacao nova.
- **Onde renderiza:** §2.2.2 p.21
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-21 — o POI2Vec precisa ser citado?

- **§4 item:** 20
- **Source status:** [N/A] como citacao (pergunta). O papel do POI2Vec no spec e [EXACT]: §6.6 "POI2Vec anchor", linhas
  111-116, 140, 205-207, 335-340, 431, 528, 657.
- **Minha leitura e avaliacao:** **Voce esta certo que ele esta no pipeline, e ha um risco de citacao que o item nao
  previu.** O papel, preciso: uma tabela de POIs treinada a montante entra no caminho **espacial** como inicializacao e
  como **buffer ancora imutavel**, com um termo L2 (`L_anchor`, peso 0.1) puxando a tabela treinavel de volta para ela.
  Nao e um modulo citado de terceiros rodando dentro do nosso: e uma tabela pre-treinada por caminhadas aleatorias sobre
  o grafo de Delaunay. **O risco:** existe um POI2Vec publicado de verdade (Feng et al., AAAI 2017), e o que o nosso
  codigo implementa **nao e o metodo daquele artigo**. Citar `feng2017poi2vec` para o nosso componente seria uma
  **misatribuicao**, que e precisamente a classe de erro do POI-RGNN que este projeto ja carrega como errata
  (`capanema2023poirgnn`).
- **Plano de resolucao proposto:** Tres saidas, com a evidencia em `_history/_round13/61_check2hgi_audit.md` § (d): (i)
  **recomendada** — nao citar nada novo e **nomear o mecanismo** no Cap.2 (uma tabela de nivel de lugar pre-treinada por
  caminhadas sobre o grafo de Delaunay, usada como inicializacao e como ancora), o que tambem repara o quinto termo
  omitido do AUT-23; (ii) citar o trabalho cujo **metodo** o codigo de fato usa, se ele for identificavel com
  identificador resolvivel; (iii) citar `feng2017poi2vec` — **nao recomendado**, seria misatribuicao. Sob nenhuma
  hipotese o nome interno `poi2vec` entra na prosa como se fosse um metodo publicado.
- **Sobreposicoes e dependencias:** **AUT-20** (o ancora e o termo de perda que falta na frase "sem rotulos").
  **AUT-23** (a afirmacao A5 omite este mesmo termo).
- **Disposicao alvo:** **[I DECIDE]** — decisao de atribuicao de citacao com risco de misatribuicao vivo; R2 poe isso do
  seu lado da linha.
- **Onde renderiza:** §2.2.3.2 p.23; §2.2.2 p.21
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-22 — a frase do FiLM/MTLnet esta na subsecao errada

- **§4 item:** 21
- **Source status:** [CHANGED] — sua citacao e do PDF com palavras coladas; a frase esta viva em `2_fundamentals.tex`,
  dentro de `\subsubsection{Context encoders}` (§2.2.3.1, p.23).
- **Minha leitura e avaliacao:** **Confirmado, e voce e o segundo a achar.** A frase do FiLM esta numa subsecao sobre
  **representacoes** de mobilidade, e o FiLM nao e uma representacao: e um mecanismo de condicionamento, que pertence a
  §2.3 com as topologias de compartilhamento. **O Germano levantou identicamente isto no GER-06**, que ja esta
  dispositionado **[YOU APPLY]** com as palavras "FiLM is a conditioning mechanism, not a mobility representation, and
  belongs with the sharing topologies in 2.3". As duas frases seguintes (o Cap.4 mantem a arquitetura e troca a entrada)
  sao detalhe de metodo dos Caps.3/4 e o GER-06 tambem as marca.
- **Plano de resolucao proposto:** Executar como **parte do GER-06**, nao como item separado: mover a frase do FiLM para
  §2.3.1 e decidir o destino das duas frases de metodo. O `FiLM` esta registrado no GLOSSARY §2 com a nota "Ch.2 or Ch.3
  (gloss once)", entao mover nao cria pendencia de registro.
- **Sobreposicoes e dependencias:** **GER-06 e o mesmo defeito e ja esta aprovado para aplicacao** — este item nao
  precisa de decisao nova, so de nao ser executado duas vezes. AUT-19 e AUT-23 (mesma secao §2.2).
- **Disposicao alvo:** **[YOU APPLY]** — via GER-06, para nao duplicar a edicao.
- **Onde renderiza:** §2.2.3.1 p.23 -> §2.3.1 p.25
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-23 — conferir §2.2.3.2 contra o spec do Check2HGI

- **§4 item:** 22
- **Source status:** [N/A] como citacao (pedido de verificacao). A subsecao viva e §2.2.3.2 "The check-in level" (p.23).
- **Minha leitura e avaliacao:** Feito, afirmacao por afirmacao, contra o spec e contra o codigo. A maioria confere;
  **tres afirmacoes nao**, e as tres sao o mesmo excesso com cabecas diferentes: a subsecao descreve o objetivo do
  Check2HGI como puramente hierarquico e **sem rotulos de tarefa**, quando a configuracao usada no Cap.5 acrescenta
  **dois termos auxiliares** — a reconstrucao de categoria de POI mascarado (peso 0.3) e o ancora POI2Vec (peso 0.1). A
  equacao apresentada como o objetivo e o **nucleo** hierarquico, nao a perda completa de cinco termos que foi treinada.
  Detalhe por afirmacao em `_history/_round13/61_check2hgi_audit.md` §ITEM 22.
- **Plano de resolucao proposto:** Uma edicao coordenada, porque A3/A5/A11 sao um defeito com tres cabecas: dizer que a
  equacao e o nucleo hierarquico e que a configuracao do Cap.5 acrescenta os dois auxiliares que aquele capitulo nomeia,
  com um ponteiro para frente. Isso repara simultaneamente a frase do AUT-20 e o termo omitido do AUT-21.
- **Sobreposicoes e dependencias:** **AUT-20 e AUT-21 sao a mesma edicao vista de outro angulo** — os tres devem ser
  resolvidos numa unica passada, ou o capitulo fica se contradizendo. GER-07 (se o Check2HGI e definido antes de ser
  nomeado).
- **Disposicao alvo:** **[I DECIDE]** — muda o que o capitulo afirma sobre o objetivo do nosso proprio sistema (C2) e
  esta entrelacado com AUT-20 e AUT-21.
- **Onde renderiza:** §2.2.3.2 p.23
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-24 — "The representation changes are paired with a controlled progression..." nao e boa transicao

- **§4 item:** 23
- **Source status:** [EXACT] — `2_fundamentals.tex`, primeira frase de `\subsection{Model lineage}` (§2.2.4, p.24).
- **Minha leitura e avaliacao:** Concordo, e o diagnostico e nomeavel. A frase e uma transicao que nao transiciona: "are
  paired with" nao diz **quem** emparelha nem **por que**, e "controlled progression" e um substantivo abstrato fazendo
  o trabalho que um verbo deveria fazer. E a forma que WRITING_LAW §1 proibe. Ela tambem abre uma subsecao cujo conteudo
  real e concreto (o modelo final permanece na linhagem do MTLnet, troca as camadas residuais por blocos de atencao
  cruzada), entao a abertura esta mais abstrata que o corpo.
- **Plano de resolucao proposto:** Uma frase, reescrita para nomear o sujeito e o que ele faz: as tres arquiteturas
  mudam junto com a representacao, e a tabela de linhagem mostra o que muda em cada passo. Sem numero novo, sem
  afirmacao nova.
- **Sobreposicoes e dependencias:** AUT-25 (a frase de fechamento da mesma subsecao). Resolver os dois juntos: sao a
  abertura e o fechamento de §2.2.4.
- **Disposicao alvo:** **[YOU APPLY]**
- **Onde renderiza:** §2.2.4 p.24
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-25 — "differ in their sharing topology and in the private input" precisa explicar melhor

- **§4 item:** 24
- **Source status:** [EXACT] — `2_fundamentals.tex`, ultima frase antes da tabela de linhagem (§2.2.4, p.24).
- **Minha leitura e avaliacao:** **A sua analise tecnica esta correta nos dois pontos que dependiam da codebase, e
  parcialmente correta no terceiro.** Verificado: (a) **sim**, o MTLnet ja recebia duas entradas, e ambas eram vistas do
  **mesmo** embedding de lugar; (b) **sim**, no modelo conjunto os dois fluxos leem **tabelas exportadas diferentes** do
  Check2HGI (o fluxo semantico le o vetor por visita; o espacial le o vetor treinado do no de regiao); (c) a
  **correlacao** que voce afirma e direcionalmente defensavel mas nao e medida: o spec diz que o caminho espacial recebe
  uma copia com **stop-gradient** do pool de POIs, o que faz os dois compartilharem origem por construcao. Afirmar
  "correlacao" como quantidade exigiria um numero que ninguem mediu.
- **Plano de resolucao proposto:** Duas ou tres frases em §2.2.4 carregando o contraste que voce quer: as duas
  arquiteturas sempre tiveram duas entradas; o que mudou e que elas deixaram de ser duas vistas de uma tabela e passaram
  a ser duas tabelas exportadas de uma representacao. A relacao entre elas entra como **fato de construcao** (origem
  comum via copia com stop-gradient), nunca como "correlacao" quantificada, a menos que voce autorize medir.
- **Sobreposicoes e dependencias:** AUT-24 (mesma subsecao). AUT-23 (as duas descrevem o Check2HGI no Cap.2).
- **Disposicao alvo:** **[I DECIDE]** — tres frases novas sobre a nossa arquitetura (C2), e voce precisa decidir entre
  hedge e medicao para a palavra "correlacao".
- **Onde renderiza:** §2.2.4 p.24
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-27 — o §2.3.3 nao explica o que e L_k, e §2.3.2/§2.3.3 podem ficar mais faceis

- **§4 item:** 26
- **Source status:** [EXACT] — o simbolo existe uma unica vez, em `2_fundamentals.tex`:822, dentro de
  `eq:fund:mtl-total`.
- **Minha leitura e avaliacao:** **Confirmado, e verifiquei de novo porque o meu primeiro instrumento mentiu:** a busca
  normalizada por "L_k" reduz a duas letras e casa com quase qualquer texto, entao aquele veredito foi artefato e foi
  descartado. Medido pelo simbolo em si: a prosa em volta da equacao glosa **K** (o numero de tarefas), **theta** (os
  parametros compartilhados) e **w_k** ("A balancing method changes the weights $w_k$"), e **nunca diz o
  que $\\mathcal{L}_k$ denota**. E o unico simbolo da equacao sem glosa, e e o mais importante deles.
- **Plano de resolucao proposto:** Meia oracao onde a equacao e introduzida, dizendo que $\\mathcal{L}_k$ e a perda da
  tarefa $k$. A segunda metade do seu item (deixar o fluxo logico de §2.3.2/§2.3.3 mais facil de seguir) e o mesmo
  pedido do AUT-29, e deve ser decidida la, nao aqui.
- **Sobreposicoes e dependencias:** **AUT-29 e a metade estrutural deste item** (a reordenacao de §2.3.2/§2.3.3). GER-09
  (que pediu o formalismo de MTL, incluindo esta equacao, e esta em aberto com voce).
- **Disposicao alvo:** **[YOU APPLY]** — a glosa do simbolo. A parte de reorganizacao vai para o AUT-29.
- **Onde renderiza:** §2.3.2 p.26
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-28 — deveriamos afirmar algo sobre a propriedade de Pareto do Cap.5?

- **§4 item:** 27
- **Source status:** [N/A] como citacao (pergunta).
- **Minha leitura e avaliacao:** **A resposta honesta e: uma afirmacao limitada vale em quatro dos seis conjuntos e esta
  BLOQUEADA nos outros dois.** Aplicando a definicao que o proprio documento registra (dominancia = nao pior em todas as
  tarefas e melhor em pelo menos uma), com os numeros **citados** da fonte de registro, nunca calculados: em Istambul,
  FL, TX e CA os dois deltas sao positivos e ambos carregam teste de superioridade, entao a dominancia vale. Em **AL** o
  delta de regiao e $-0.41$ e em **AZ** e $-0.00$: os dois sao **nao-inferiores por TOST**, e nao-inferioridade **nao
  e** "nao pior". O WRITING_LAW §3 proibe promover TOST a vitoria, e o whitelist do MobiWac poe "Pareto-dominates
  everywhere" na lista do que **nao** se pode dizer, nominalmente. Duas ressalvas de forma, mesmo onde vale: a
  dominancia de Pareto e definida na literatura sobre **perdas de tarefa de um mesmo modelo**, e aqui seria aplicada a
  **duas metricas de um modelo contra dois modelos treinados separadamente**; e dominancia nao diz nada sobre
  **otimalidade**.
- **Plano de resolucao proposto:** Duas a tres frases no Cap.6, e uma decisao de vocabulario. **Recomendada (A), sem a
  palavra Pareto:** "Em quatro dos seis conjuntos o modelo conjunto e melhor que os modelos dedicados nas duas tarefas
  ao mesmo tempo. Nos outros dois e melhor em categoria e estatisticamente nao-inferior em regiao dentro de uma margem
  de dois pontos, entao nenhuma afirmacao de dominancia e feita ali." (B) nomeia o conceito explicitamente. **O Apendice
  F e o lugar errado** para isso, ao contrario do que o item sugere: ele mede cosseno de gradiente, nao desfecho de
  tarefa, e a propria margem dele e outra quantidade em outra escala. **Se qualquer forma entrar, a frase "claims no
  Pareto property" do §2.3 fica falsa como escrita** e precisa ser estreitada para otimalidade — e ela e guardada por
  quatro probes.
- **Sobreposicoes e dependencias:** **AUT-01 (o item que ja existe) e vizinho mas nao e o mesmo:** ele pergunta se os
  **fundamentos** precisam de tratamento de Pareto (largamente satisfeito; falta o seu aval em tres traducoes PT); este
  pergunta se os **resultados** autorizam a afirmacao. AUT-14 (c) e (d), GER-11.
- **Disposicao alvo:** **[I DECIDE]** — afirmacao cientifica nova fora do whitelist, cuja forma global o whitelist
  proibe, e que obriga a estreitar uma frase protegida por probe.
- **Onde renderiza:** §6.2 p.84; §2.3.2 p.26 (a frase a estreitar)
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-30 — a frase do Acc@10 descontado por OOD, e o OOD nao explicado

- **§4 item:** 29
- **Source status:** [EXACT] — `2_fundamentals.tex`, §2.4.2.2 (p.29).
- **Minha leitura e avaliacao:** **Confirmado, e sao dois defeitos, nao um.** (a) A sigla `OOD` aparece em prosa
  **antes** de qualquer expansao: a forma completa "out-of-distribution" aparece cerca de 80 caracteres **depois**,
  dentro da propria frase que voce nao entendeu. WRITING_LAW §7 exige expandir no primeiro uso. (b) `OOD` **nao esta na
  Lista de Abreviaturas**, e o comentario que justifica a omissao (`content.tex`:262-264) diz que STL, CV, GRU, OOD e
  outras "never appear in prose" — o que hoje e **falso para OOD**, que aparece tres vezes. O GLOSSARY §5 lista OOD como
  sigla, entao o registro e a lista impressa discordam. Sobre a frase em si: ela e uma identidade aritmetica dita em
  palavras, e por isso pesa; ela existe porque a metrica tem duas leituras equivalentes.
- **Plano de resolucao proposto:** Tres edicoes pequenas: expandir OOD no primeiro uso; reescrever a frase de
  equivalencia como uma definicao direta (Acc@10 na parte in-distribution, multiplicada por um menos a fracao fora de
  distribuicao, com regioes ausentes do treino contando como erro); e decidir se `OOD` entra na Lista de Abreviaturas,
  corrigindo o comentario de `content.tex` de qualquer forma, porque ele afirma um fato medido que deixou de ser
  verdade.
- **Sobreposicoes e dependencias:** AUT-31 (a reorganizacao de §2.4, onde esta frase vive). AUT-15 (`sec:fund:eval` como
  destino).
- **Disposicao alvo:** **[YOU APPLY]** — expansao de sigla e reescrita de uma definicao, sem afirmacao nova. A entrada
  na Lista de Abreviaturas e uma linha sua se voce quiser inclui-la.
- **Onde renderiza:** §2.4.2.2 p.29; Lista de Abreviaturas p.10
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-31 — reorganizar §2.4 e criar "Preparation and data split"

- **§4 item:** 30
- **Source status:** [N/A] como citacao (pedido estrutural).
- **Minha leitura e avaliacao:** Concordo com a estrutura que voce propoe, e ela e mais coerente que a atual. Medido:
  §2.4 tem 741 palavras em tres subsecoes — Datasets (80), Metrics and reference points (23, mais tres subsubsecoes de
  106/101/169) e Validation and statistical decisions (227). O material de preparacao e split que voce quer promover
  **esta** dentro do §2.4.3, misturado com as decisoes estatisticas: as frases sobre validacao cruzada estratificada, a
  diferenca de split entre capitulos, e a aritmetica de sementes e particoes. Separa-las deixa o §2.4.3 fazendo uma
  coisa (como comparar e decidir) em vez de duas.
- **Plano de resolucao proposto:** Quatro subsecoes em vez de tres: `Datasets` (fica), **nova**
  `Preparation and data split` (recebe as frases de split do §2.4.3 e o que voce quiser acrescentar sobre preparacao),
  `Metrics and reference points` (fica), e §2.4.3 renomeada `Comparison and statistical decisions`. Custo: um titulo
  novo, um renome, movimentacao de tres a quatro frases, e conferencia dos `\ref` que apontam para `sec:fund:eval`.
  **Atencao:** o `\label{sec:fund:eval}` e citado de fora do capitulo, entao o label deve continuar apontando para a
  secao que as outras referencias esperam.
- **Sobreposicoes e dependencias:** AUT-18 (as sete categorias, cujo destino proposto e §2.4.1). AUT-30 (a frase do OOD
  vive em §2.4.2.2). AUT-29 (a mesma classe de pedido, em §2.3).
- **Disposicao alvo:** **[I DECIDE]** — reorganizacao estrutural com um label citado de fora; a arvore de secoes e sua.
- **Onde renderiza:** §2.4 p.28-30
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-33 — "o ganho nao vem da regiao ensinando a categoria" estaria errado

- **§4 item:** 32
- **Source status:** **[GONE]** — a string que voce cita nao existe em nenhum lugar da prosa viva. Verificado com cinco
  padroes diferentes, cada um validado antes contra uma passagem que **contem** o conceito.
- **Minha leitura e avaliacao:** **Este e o item mais importante de todos, e a boa noticia e que o texto vivo ja faz
  exatamente a sua distincao.** O Cap.6 vivo diz: *Within this control, the category improvement therefore does not
  require training transfer from the region task. The result rules out that explanation, but it does not determine
  whether the gain comes from the category encoder, the feed-forward blocks, the added depth, cross-attention, or a
  combination of these components.* Isto e precisamente o seu ponto: o controle elimina o **sinal de treino** e deixa em
  aberto que a atencao cruzada e os outros artefatos continuam contribuindo. **A varredura que voce pediu ("avalie se
  esse mesmo erro esta acontecendo em outras partes do texto") encontrou zero defeitos.** A unica frase que fica sozinha
  demais e uma oracao no Cap.5 (`5_mobiwac/06_results.tex`:203-204), e a frase seguinte ali ja a repara. Tambem
  confirmado que a restricao de redacao do `NORTH_STAR` §6 ("Sharing stopped hurting", nunca "the tasks teach each
  other") esta respeitada: nenhuma prosa credita as tarefas ensinando uma a outra.
- **Plano de resolucao proposto:** Fechar como **ja satisfeito**, com a citacao acima como evidencia. Nenhuma mudanca de
  prosa e necessaria nem recomendada. A unica opcao aberta e apertar a oracao isolada do Cap.5, que e prosa
  **republicada** de um capitulo em revisao e portanto tem custo de errata; recomendo nao mexer.
- **Sobreposicoes e dependencias:** AUT-37 (o que os controles descartam e exatamente o material do "o que erramos na
  tese inicial" que a conclusao quer narrar).
- **Disposicao alvo:** **[YOU APPLY]** — no sentido de fechar como satisfeito. Sem edicao.
- **Onde renderiza:** §6.2 p.84; Cap.5 p.70 (a oracao opcional)
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

### AUT-34 — "Contributions by chapter" com menos numeros e mais conceito

- **§4 item:** 33
- **Source status:** [N/A] como citacao (pedido de reequilibrio).
- **Minha leitura e avaliacao:** Medido, e a proporcao que voce assume **ja vale**: §6.1 tem 21 numerais e §6.2 tem 53,
  ou seja os resultados ja estao concentrados onde voce quer. Dos sete numerais arabes de §6.1, apenas um e um resultado
  que §6.2 ja repete (a faixa de ganho de categoria); os outros sao convencao de protocolo (sementes, particoes, n,
  margem), que WRITING_LAW §3 exige que acompanhem qualquer afirmacao quantificada. Entao o item nao e "tirar numeros",
  e "tirar **um** numero e verificar que o resto e convencao".
- **Plano de resolucao proposto:** Uma exclusao barata (a faixa de ganho em §6.1, que §6.2 restabelece integralmente) e
  uma decisao sua sobre se algum recap quantificado pode virar qualitativo. Nao se apaga um numero sozinho: ele sai com
  o seu ponto de referencia e a sua convencao, ou fica.
- **Sobreposicoes e dependencias:** **AUT-37 pede o mesmo reequilibrio de outro angulo** e a mesma edicao serve aos
  dois — decidir juntos.
- **Disposicao alvo:** **[I DECIDE]** — a proporcao ja esta a seu favor; o que resta e se um recap quantificado pode
  virar qualitativo, e isso o WRITING_LAW reserva a voce.
- **Onde renderiza:** §6.1 p.83; §6.2 p.84
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)



---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-04 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
