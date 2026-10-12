# Terceiro aval — as decisões que a re-revisão do arco completo levantou

> **O que é este documento.** Você pediu a re-revisão do arco inteiro com os especialistas antes de
> seguirmos. Cinco revisores rodaram (leitor frio, honestidade de alegações, simulador de banca,
> orientador adversarial, avaliador de excelência). **Veredito: 5/5 "pronto para redigir, com
> correções"** — todos respondem "sim, agora é uma boa narrativa", e todos acharam a mesma categoria
> de defeito: não a história, mas a **transmissão** dela (a espinha NORTH_STAR/GLOSSARY ainda
> carregava frases de antes das correções). **A maioria já corrigi nesta sessão** (lista completa em
> `11_full_arc_rereview/full_arc_rereview.md`). Sobraram **três decisões que são suas** — este
> arquivo. Os cinco vereditos completos estão em `11_full_arc_rereview/five_verdicts.txt`.

---

## D1 — A sua pergunta do N3, respondida: rodar o experimento ou escrever a concessão?

**A sua pergunta.** No N3 você escreveu que a evidência de *onde vem a melhoria do MTL* ainda não te
convence muito, pediu minha opinião, e ofereceu experimentos (local ou nespedgpu).

**Minha opinião honesta.** A evidência que você tem é melhor do que você está dando crédito — o
controle de congelamento é um experimento de verdade e prova que o ganho é efeito do tronco, não de
uma tarefa ensinando a outra. Mas ela tem **um** buraco real, e o simulador de banca formulou a
pergunta exata que o pacote ainda não responde bem:

> *"Se o ganho vem do tronco e não da interação entre as tarefas, um modelo dedicado de tarefa única
> com a mesma capacidade não recuperaria o mesmo ganho? O senhor rodou esse baseline?"*

O congelamento não responde isso; hoje a defesa é a divulgação honesta (parâmetros como custo) mais
uma concessão. Defensável num mestrado, mas é o ponto mais fraco sob arguição.

**As opções (escolha uma):**

- **(a) Rodar o baseline dedicado com capacidade equiparada — recomendo, se o tempo permitir.** UM
  experimento: o modelo dedicado de categoria (e opcionalmente o de região) escalado para ~o número
  de parâmetros do conjunto, mesmo protocolo (user-disjoint, 5 folds, mesmas sementes, mesmo
  orçamento de ajuste). Responde a pergunta da banca com um número em vez de uma concessão. É
  viável: o pipeline está no repo e o nespedgpu (A40, 46GB) está conectado. **Regra de
  licenciamento obrigatória:** os números novos NÃO entram no Cap. 5 (versão de registro sob
  revisão no MobiWac); vivem na moldura (discussão adjacente ou apêndice) como análise
  pós-submissão, datada, com o próprio portão de fatos. Qualquer resultado te fortalece: se o
  dedicado equiparado ≈ dedicado, a vitória conjunta não é artefato de capacidade (o tronco se
  confirma); se recuperar parte do ganho, você reporta honestamente e a história ganha uma nuance
  quantificada — achado seu, não de um revisor.
- **(b) Só a concessão (o piso, já aprovado).** A concessão do §3.4 já está na espinha (limitações
  do Cap. 6, amarrada ao trabalho futuro). É o mínimo defensável se não houver experimento.

O que eu **não** recomendo: estudos amplos de mecanismo (congelamentos simétricos, sondas de
representação) antes da defesa — é dispersão contra o prazo de agosto; o baseline equiparado é o
único experimento que responde a única pergunta viva.

**Esta decisão trava o Cap. 5/6** (o parágrafo do mecanismo é redigido diferente em cada opção); os
Caps. 1–4 não dependem dela.

**Author:** Vamos lá, o que eu responderia ao simulador da banca que talvez você tenha deixado de lado: Não por que no
tronco ainda temos o mecanimos de gate que permite a troca de conhecimetno entre as tarefas.(Vale estudar mais a
arquitetura para elaborar melhor essa resposta). Mas, eu gostaira de seguir pela opção A. E se caso a resposta não for
muito a favor do MTL eu acredito que valha não mecionar ou trabalhar muito disso no texto, já que corremos o risco de
gerar mais confusão no leitor.

> **Registrado: opção A.** O desenho do experimento, com o contrato de licenciamento fechado ANTES
> de existir resultado, está em `13_capacity_baseline/experiment_design.md`. Dois avisos honestos,
> registrados lá em detalhe: (1) a resposta "não, porque o gate permite a troca de conhecimento"
> **não se sustenta** como está — o próprio controle de congelamento do MobiWac mostra que o ganho
> de categoria sobrevive com o caminho da região congelado ("not the region task teaching the
> category one", enunciado como achado); o que a atenção cruzada explica é por que compartilhar
> **não atrapalha**, não uma troca que o congelamento mostra ser desnecessária — por isso a resposta
> forte é o experimento, não o gate. (2) Sobre "não mencionar se não for a favor": prominência é
> decisão sua; **supressão não é** — uma vez rodado, o resultado vincula a concessão do §3.4 (uma
> frase honesta basta; silêncio não), pela lei do §7 (correção silenciosa). O quanto de espaço dar é
> seu; se aparece, não é negociável.

---

## D2 — O título da dissertação (achado do leitor frio; a decisão já está aberta no NORTH_STAR §5)

Dois dos três candidatos de título violam a regra dos dois fatores (F1) que todo o resto do texto
obedece: *"One Model, Two Tasks: Representation-Driven Multi-Task Learning…"* credita a vitória só à
representação; *"Check-in-Level Representations for Multi-Task POI Prediction"* nomeia só o primeiro
fator. O título é o primeiro contato do leitor mais frio com o arco.

**Recomendação:** o primeiro candidato (*"From Representations to a Single Joint Model…"*) é o único
que sobrevive ao teste como está. Se preferir outro, a regra é: o título nomeia os dois fatores (ou
nenhum), nunca só a representação.

**Author:** I like the "From Representations to a Single Joint Model…", but don't have a lot of creative, the first
title, call more attention due the crativite and games with the words. I belie that we sould try to think on somthing in
more this line. One exemple: "Representation Drives, Multi-Task cares"

> **Resposta (candidatos criativos que passam no teste dos dois fatores).** A sua linha
> ("Representation Drives, Multi-Task Cares") funciona — só precisa nomear o segundo fator com um
> verbo que a evidência sustenta. Candidatos, todos com o subtítulo técnico obrigatório:
>
> 1. **"Representation Drives, Sharing Delivers: A Check-in-Level Multi-Task Study of Next Category
>    and Region Prediction"** — o mais próximo do seu exemplo; nomeia os dois fatores com verbos
>    honestos (a representação é o fator dominante; o compartilhamento redesenhado entrega a vitória).
> 2. **"The Visit, Not the Place: Check-in-Level Representations and a Joint Model for Next Category
>    and Region Prediction"** — joga com o mecanismo central (o vetor por visita); "place" é o termo
>    canônico (nunca "venue").
> 3. **"One Visit, One Vector: From a Published Null to a Joint Model for Next Category and Region
>    Prediction"** — nomeia o arco honesto no próprio título (null → método), que é a assinatura da
>    dissertação.
> 4. **"When One Model Learns Two Tasks: Check-in-Level Representations and Redesigned Sharing for
>    POI Prediction"** — neutro no primeiro plano, dois fatores no subtítulo.
>
> Regra que todos respeitam: ou nomeia OS DOIS fatores, ou nomeia NENHUM e deixa o subtítulo
> carregar; nunca só a representação. Cuidado com o estilo "X Carries, Y Pays" — é o padrão do
> título do BRACIS rejeitado; evitar a semelhança. Escolha um, ajuste à vontade, ou mande outra
> direção — a decisão é sua e entra no NORTH_STAR §5 item 8.

---

## D3 — O orçamento de beats do Cap. 1 (achado do leitor frio)

Quase todos os movimentos aprovados apontam para o Cap. 1, e vários itens têm colocação "e/ou"
(Cap. 1 e/ou prefácio do 4 e/ou recap do 5). O risco: uma Introdução que responde toda objeção
possível antes de mostrar qualquer evidência lê-se como defensiva e atrasa a história.

**Recomendação:** antes de redigir o Cap. 1, eu preparo uma página de "orçamento de beats" que dá a
cada movimento aprovado **um** endereço (Cap. 1 vs prefácio do 4 vs recap do 5 vs Cap. 6) — a
Introdução *narra* o arco; as defesas detalhadas moram nos prefácios/recaps/Cap. 6. Você aprova essa
página antes da redação.

**Author:** Aprove, great ideia!

---

## Registro: o que já foi corrigido sem precisar de você

A re-revisão achou e eu já apliquei (detalhe em `11_full_arc_rereview/`): a retração do protocolo do
CoUrb propagada para NORTH_STAR §4/§6 e GLOSSARY (era o único BLOCKER); a espinha sincronizada com
tudo o que você aprovou (o reconhecimento da troca de par, a defesa de três pernas, o N2 na forma de
cautela, a concessão do §3.4 nas limitações, os beats do mecanismo N3 com escopo completo); a
promessa de "menor custo" da Introdução redefinida para simplicidade operacional (o custo real é
maior e divulgado); a logline do PANORAMA corrigida (compartilham *através de* um tronco de atenção
cruzada — a versão anterior negava o tronco que o mecanismo credita); e duas regras de redação
registradas (nunca "o trabalho futuro do CBIC pediu representações melhores"; as tarefas são "de
granularidade mais grossa", nunca "mais simples").

Pendências que não dependem de decisão (só de execução): verificação do split do CoUrb no código
(github.com/TarikSalles/Spatial_Embeddings ou judge_feedback), autorização do conector OpenAlex no
app para a busca além-da-mobilidade, e os consertos de página do Cap. 2 já catalogados (viram a
primeira ordem de serviço da onda de redação).

Codigo do tarik: /Users/vitor/Desktop/mestrado/temp/tarik-new
On the openAlex I ahve add more founds so you can use it now.

---

## Atualização pós-decisões (2026-07-23)

- **Split do CoUrb: VERIFICADO E FECHADO.** Li o código que você apontou
  (`tarik-new/PoiMtlNet_Novo`): `src/etl/mtl/create_fold.py` L190–199 lê o `userid` e **descarta a
  coluna**; os folds são `StratifiedKFold` puro sobre amostras, estratificado por classe (L225–228);
  `src/etl/next/fold.py` idem; nenhum splitter com grupos existe no código do projeto. **A alegação
  original estava certa: o protocolo do CoUrb é estratificado por amostra, mais fraco que o
  user-disjoint do Cap. 5.** O beat do prefácio do Cap. 4 foi RESTAURADO no NORTH_STAR/GLOSSARY, agora
  com evidência de arquivo/linha (UW-3 fechado). Nota: o GLOSSARY agora pede a mesma verificação para
  o CBIC antes de afirmar o split dele em prosa.
- **D1 (opção A): desenho pronto** em `13_capacity_baseline/experiment_design.md`; próximo passo é a
  auditoria de contagem de parâmetros e o piloto no nespedgpu.
- **D3 (aprovado): o orçamento de beats do Cap. 1 está pronto** em
  `12_ch1_beat_budget/ch1_beat_budget.md` — cada movimento aprovado com UM endereço; o Cap. 1 narra,
  os prefácios/recaps/Cap. 6 litigam. Aguarda o seu OK (é a última aprovação antes da redação do
  Cap. 1).
- **D2 (título): quatro candidatos criativos** que passam no teste dos dois fatores foram adicionados
  acima, na sua linha "Representation Drives…". Decisão sua, sem pressa (trava só o front matter).
- **OpenAlex: ainda bloqueado, mas por AUTORIZAÇÃO, não por créditos.** Os fundos que você adicionou
  resolvem a cota, mas o conector re-registrado continua "attached but not connected" — falta
  autorizá-lo no app (Configurações → Conectores → conectar o servidor de literatura). Enquanto isso,
  a busca além-da-mobilidade segue represada (nenhuma citação de memória entrou).