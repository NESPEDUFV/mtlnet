# Guia didático — como este projeto decide se um número é real

> **Leia isto antes de comparar dois modelos, e antes de rodar um estudo grande.** É o guia do
> protocolo de avaliação: o que se mede, com que instrumento, e por que as regras que parecem
> burocráticas existem.
>
> Companheiro do [`TELEMETRY_GUIDE.md`](TELEMETRY_GUIDE.md), que explica *quais números cada execução
> grava*. Este explica *como esses números viram conclusões*. Para "qual conjunto eu uso agora?",
> o quadro de bolso é [`QUAL_CONJUNTO_USAR.md`](QUAL_CONJUNTO_USAR.md).
>
> A especificação formal e congelada é [`plans/EVALUATION_PROTOCOL.md`](plans/EVALUATION_PROTOCOL.md);
> ela não pode ser editada depois da primeira execução confirmatória, e é por isso que existe este
> guia separado, que pode. Onde este guia diverge do protocolo congelado, ele o **declara** — nunca
> o edita (o caso do §7.5 foi declarado aqui e depois registrado como a emenda §12.3 do protocolo).

## Para onde ir

| você vai… | leia |
|---|---|
| rodar um estudo grande (N variantes, sweeps, ablações) | **§7** inteiro; a receita de bolso é §7.9; qual conjunto usar: §7.5 + [`QUAL_CONJUNTO_USAR.md`](QUAL_CONJUNTO_USAR.md) |
| obter ou citar um número final | §7.10 (`--confirmatory`), §6 (o que cada veredito permite dizer), §8 (por que nunca contra números do v18) |
| interpretar um delta que já existe | §1 (convenção de agregação), §3 (Tier A × Tier B — qual `n`), §5 (a margem δ), §6 (NI → superioridade) |
| entender por que as regras existem | §0 (o mapa), §2 (quem escolhe a época), §4 (orçamento de réplicas), §0.2 (o que conta como verificação) |
| entender partição × semente de modelo, ou medir o eixo de partição num ciclo novo | **§9**; a emenda formal é o §12.6 do protocolo; a medição da v19: [`../studies/v19_defence/S10_4_PARTITION_AXIS.md`](../studies/v19_defence/S10_4_PARTITION_AXIS.md) |
| conferir uma citação | ledger de fontes, no fim do documento |

## 0 · O mapa, em um diagrama

Toda execução divide os **usuários** em três blocos disjuntos, e cada bloco tem um dono:

```
┌──────────── 70 % ────────────┬──── 10 % ────┬──────── 20 % ────────┐
│           TREINO             │  VAL INTERNA │    TESTE EXTERNO     │
│  o modelo aprende            │  escolhe a   │  lido UMA vez, no    │
│                              │  época       │  fim de tudo         │
└──────────────────────────────┴──────────────┴──────────────────────┘
     ↑ olhe à vontade             ↑ à vontade      ↑ gasta uma leitura

     ESTÁGIO 1 · execução                    ESTÁGIO 2 · comparação
     treina · seleciona época          ──▶   lê linhas de ≥2 braços
     grava LINHAS, nenhum número              Tier B · Tier A · NI/TOST
     de teste externo                         multiplicidade
```

O Estágio 1 **não calcula métrica de teste externo**, nem para monitorar. Não é disciplina — é
estrutura: não existe o que olhar cedo, então não há como olhar cedo. Pedir o número é chamar o
Estágio 2, um ato deliberado e datado.

E uma precisão que desfaz uma falsa contradição: o bloco de 20 % **não é um pedaço fixo do
estado** — é o fold externo da vez, e ele **roda**. São 5 folds externos user-disjoint; cada
usuário é outer-test em exatamente **um** deles e treino/val-interna nos outros quatro. Assim,
todo usuário do estado recebe exatamente uma predição fora-de-amostra, e "ler o teste uma vez"
significa pontuar **uma vez, por braço e por ciclo de congelamento, a tabela concatenada dessas
predições out-of-fold dos cinco folds** (o "OOF agrupado" do §1). "20 % lacrados" e "todo usuário
é avaliado" descrevem a mesma tabela, por dois ângulos.

## 0.1 · Os sete erros que este protocolo existe para impedir

Cada seção adiante conserta um destes, e todos já aconteceram aqui:

| # | o erro | onde se conserta |
|---|---|---|
| 1 | média de folds em vez de agrupar as contagens (viés de −0,24 pp sob desbalanceamento) | §1 |
| 2 | escolher a época no mesmo fold que reporta o número (otimismo de seleção — ver o quadro de cifras abaixo) | §2, §8 |
| 3 | citar `n = 20` quando há 4 réplicas e 5 folds correlacionados | §3 |
| 4 | ler "sem diferença significativa" como "sem custo" | §5, §6 |
| 5 | uma semente movendo dois fatores experimentais ao mesmo tempo | [`NOMENCLATURE.md`](NOMENCLATURE.md) |
| 6 | ajustar o modelo depois de ver o teste, e continuar chamando de confirmatório | §7 |
| 7 | aceitar consistência interna como verificação | §0.2 |

### As três cifras de otimismo de seleção — a hierarquia obrigatória

Circulam três cifras para "quanto vale o otimismo de seleção", e elas **não são a mesma
quantidade**. Somá-las, trocá-las, ou promover a de baixo é o erro. A hierarquia é a do
[`DIVERGENCE_REGISTER.md §3.1`](DIVERGENCE_REGISTER.md), que é a fonte de verdade:

| cifra | o que é |
|---:|---|
| **≈3,7 pp** | a mais limpa das três — mesmo código, mesmo substrato, mesma partição (o registro a cita como 3,66, dos valores não arredondados; nas tabelas do §8, 73,72 − 70,05 = 3,67). Ainda assim um **pacote**, não uma medição pura: entre as duas leituras mudam também a população de avaliação, a fração de treino e o número de réplicas — ver a ressalva no §8 |
| ~1 pp | ordem de grandeza — mistura protocolo **com** convenção de agregação (§8) |
| ~0,66 pp | **sugestivo** — um único fold de Alabama (`waves/sealed_bridge.toml:9`), e nada mais. Nunca foi "medido" |

E o fecho que a hierarquia exige: **o instrumento que mediria o otimismo de verdade existe e nunca
rodou** — `src/mtlcheck/eval/optimism.py` (o §8a do protocolo), que decompõe a1−b1 e b1−b2
co-registrados na mesma trajetória e exige `retain_checkpoints != "none"` (o default é `"none"`).
Enquanto ele não rodar, nenhuma das três cifras pode ser citada como "o otimismo medido".

(Como a cifra de baixo chegou a circular como "medida" em cinco sítios de código — e sobreviveu a
uma varredura declarada completa, que olhou `src/` e não olhou `docs/` — é um caso do §0.2:
consistência entre sítios não é verificação, e uma varredura só vale o escopo que de fato cobriu.)


## 0.2 · Consistência interna não é verificação

A regra, e ela é geral:

> **Consistência interna descarta "um número foi inventado". Nunca descarta "todos vieram de uma
> configuração que não é a que rodou".**

Só uma medição independente separa os dois casos — recontar com outra implementação, ou ler o
artefato que a execução gravou.

**O procedimento, porque a regra sozinha não diz o que fazer:**

> Antes de aceitar um teste como verificação, **aplique-o ao defeito conhecido e veja se ele
> reprova.** Um teste que não reprova o caso conhecido não verifica nada.

Isto não é retórica; foi o que aconteceu. O ajuste quadrático abaixo passou primeiro e ia ser
entregue como verificação. O que o descartou foi aplicá-lo ao defeito do apêndice de capacidade e ver
que ele o **aprovaria também** — as razões 6,53 e 8,15 são tão coerentes quanto a curva. O teste era
incapaz de falhar no caso que importava, e um teste incapaz de falhar produz confirmação vazia com
cara de verificação.

**O contraexemplo que a prova**, e é deste projeto. Um apêndice de controle de capacidade publicava
644 359 parâmetros para o modelo dedicado e 4 207 399 / 5 249 719 para dois braços alargados,
concluindo que os alargados alcançavam 100,2 % e 101,9 % do orçamento do conjunto. As razões entre os
três eram perfeitamente coerentes (6,53 e 8,15). O que rodou foi 1 433 863 / 9 634 471 / 12 044 791 —
**230 % e 234 %** do orçamento — e as razões reais (6,72 e 8,40) continuam quase idênticas às
publicadas, porque as duas pontas foram construídas pelo mesmo caminho errado e a largura domina.
Nenhum teste de coerência entre os números publicados podia detectar isso.

**O contraste**, mesmo projeto, mesma família de alegação. Um controle de capacidade no eixo de
região publica uma curva de três larguras. Ela também é internamente perfeita: os três pontos caem
sobre `16·d² + 8589·d + 9150` — e, fixando o termo constante em zero e ajustando os **dois**
coeficientes restantes apenas aos dois primeiros pontos, o terceiro é previsto a 99,9 % (uma
quadrática tem três coeficientes e não se ajusta com dois pontos; o que se fez foi isso, e é o que
se pode dizer). Isso não provou nada. O que provou foi recontar com a cabeça de região **deste**
pacote, que é implementação independente: 3 256 509 / 5 014 941 / 9 004 685 contra 3 256 510 /
5 014 942 / 9 004 686 publicados — um parâmetro a menos nas três, e esse um explicado (o escalar do
prior de trajetória, que aqui é ramo ausente por desenho, R6). Diferença conhecida e do tamanho
certo, constante nas três larguras.

### A mesma regra vale para GUARDAS EM CÓDIGO, e é aí que ela escapa

O acima está escrito para análises. Em **2026-08-21** o mesmo erro apareceu três vezes num só dia,
todas em código, todas por sessões que conheciam a regra:

| a verificação | por que não podia falhar |
|---|---|
| teste de sanidade das predições, prescrito na família `cat` | o modo de falha registrado era a família **joint** — duas correntes, caminho de captura próprio. `cat` não passa por aquele código |
| conferência de substrato da wave, em `identify(cells[0])` | cobria **1 de 6** estados numa campanha multi-estado, **enquanto a wave anunciava que conferia** |
| guarda do `save_predictions`, apontando para um caminho literal | protegia aquela campanha e **nenhuma futura** |

Nenhuma das três estava quebrada: todas rodavam, todas passavam, todas apareciam no relatório como
verificação feita. **Passar é o sintoma, não a prova.**

O que as três teriam exigido é a mesma pergunta do procedimento acima, com uma palavra trocada:

> **Qual é o caso que esta guarda existe para pegar — e ela o pega?**
>
> Se você não consegue nomear uma entrada concreta que a faça falhar, ela não é uma guarda; é uma
> linha que passa.

Na prática: escreva o mutante. Neutralize a condição, rode, e veja o teste ficar vermelho. Se ficar
verde, o que você tem é decoração. Custa um minuto e é o único jeito de distinguir os dois.

### A terceira: a cadeia de resumos parece suficiente em cada elo

Em 2026-08-21, cinco alegações deste projeto foram corrigidas indo à fonte primária. Todas tinham a
mesma forma, e **nenhuma foi resolvida por argumento** — só por leitura direta:

| a alegação | de onde vinha | o que a primária dizia |
|---|---|---|
| "TX é maior que CA" | do nosso próprio `REFERENCE_DEFECTS` §R15, sem número | TX tem **menos** lugares (160 938 contra 169 145) |
| "a coluna de lugares da tabela é pós-join espacial" | de uma coincidência em um estado | é corpus bruto, como as outras duas; a coincidência significa que o join **não descarta nada** em AL e AZ |
| "CA/TX não entraram na busca de LR (quatro dos seis)" | de uma correção nossa do dia anterior | o **Texas entrou**; só FL e CA nunca tiveram LR variado |
| "batch size buscado em every dataset" | da nota de rodapé da tabela | formulação **superada pelo próprio autor** por conflar dois botões |
| "a Califórnia não aparece na enumeração — possível lacuna" | de ler a enumeração de folds como se fosse de datasets | está coberta pelo "all six"; e dez linhas acima havia o registro de que a cobertura foi **auditada duas vezes, com a segunda derrubando a primeira** |

O padrão não é "o primeiro leitor foi descuidado". Repare no terceiro e no quinto: **eram correções de
outras leituras secundárias, e também estavam erradas.** A quinta foi corrigida por mim a partir da
frase certa — e mesmo assim nenhum dos dois tinha lido as dez linhas acima, que continham a história
inteira e a invertiam de novo.

> **Só a fonte primária acerta, e ela estava ali em todas as vezes.**
>
> O problema não é alguém ser desatento; é que **a cadeia de resumos parece suficiente em cada elo**.
> Cada resumo é fiel ao anterior, e a distância da fonte cresce sem que nenhum passo pareça errado.

Na prática, e é barato: **antes de propagar um fato que sustenta uma decisão, abra o arquivo.** Não o
documento que cita o arquivo — o arquivo. E leia o parágrafo inteiro, não a linha que confirma o que
você já pensava; três das cinco acima estavam a menos de dez linhas de distância do que foi lido.

### A irmã disso: conhecimento não age, verificação age

O acima é sobre guardas que **não conseguem** falhar. Há um segundo modo, e em 2026-08-21 ele foi mais
frequente: **o aviso estava escrito, lido e recente — e não agiu.**

| o que aconteceu | o aviso existia? |
|---|---|
| manifesto da campanha omitiu `save_predictions`, o que teria custado ~34 h | sim: eu tinha escrito o bloco de aviso sobre exatamente isso **duas horas antes** |
| `git add -A` capturou trabalho de outra sessão em voo, duas vezes | sim: o §9 do `BEST_PRACTICES_NESPEDGPU`, escrito **naquela manhã**, manda commitar por caminho explícito |
| `ARTIFACTS_ROOT` apontado para o substrato de uma sondagem, não o da campanha | sim: a própria seção que descreve as duas raízes |

Nos três, quem errou tinha escrito ou lido o texto certo. Ler não impediu nada.

**O que impediu, nos casos em que algo impediu, foi sempre um mecanismo que recusa:** a resolução dos
overrides conferida antes de lançar, o `git diff --cached --stat` antes do commit, a declaração de
substrato que abortou a wave com os dois hashes na mensagem.

E o caso decisivo, porque separa recusar de avisar: a guarda de `substrate.identity.digest()` pegou o
seu próprio autor **dez minutos depois de ser escrita** — um script que a usava errado receberia um
hash plausível e constante, e teria propagado identidades idênticas para seis estados. Ela estourou
com as chaves recebidas na mensagem.

> Das cinco falhas daquele dia, **a única que agiu antes de custar alguma coisa foi a que não
> conseguia passar em silêncio.**

A regra prática, para quem escreve guarda: **recuse, não avise.** Um aviso num log de 500 épocas é
uma linha que ninguém lê; uma recusa é uma decisão que alguém toma. E se você acabou de documentar
uma regra, isso não te protege dela — escreva o mecanismo, não só o parágrafo.

⚠ E o limite dessa verificação, porque ele também é geral: recontar confirma que os números
publicados são os da arquitetura que o documento **nomeia**. Não confirma que a execução usou essa
configuração — para isso é preciso o artefato que ela gravou. São duas etapas, e o defeito acima
falhou na primeira.


## 1 · Pooling de OOF vs. média-de-fold — o que muda e por que importa

### O problema concreto

O protocolo antigo calculava macro-F1 fold a fold e depois tirava a média dos cinco valores. O
protocolo novo faz uma coisa diferente: junta as predições **out-of-fold (OOF)** dos cinco folds
num único conjunto e calcula macro-F1 **uma vez**, sobre esse conjunto agregado. São dois
estimadores diferentes do mesmo "macro-F1 do estado", e eles não coincidem sob desbalanceamento de
classe.

### A aritmética, lado a lado

Macro-F1 é a média não-ponderada do F1 de cada classe, e F1 de uma classe é uma função de
TP/FP/FN **daquela classe**. A pergunta é: em que estágio agregar os contadores brutos e em que
estágio tirar a média.

**Média-de-fold** (o que o protocolo antigo fazia):
```
para cada fold k = 1..5:
    para cada classe c:
        F1_k(c) = 2·TP_k(c) / (2·TP_k(c) + FP_k(c) + FN_k(c))
    macroF1_k = média_c F1_k(c)
macroF1_final = média_k macroF1_k        # média de 5 números já resumidos
```

**Pooling OOF** (o que o protocolo novo propõe):
```
para cada classe c:
    TP(c) = Σ_k TP_k(c)          # soma os contadores brutos dos 5 folds primeiro
    FP(c) = Σ_k FP_k(c)
    FN(c) = Σ_k FN_k(c)
    F1(c) = 2·TP(c) / (2·TP(c) + FP(c) + FN(c))
macroF1_final = média_c F1(c)     # uma única divisão por classe, no final
```

A diferença fica visível numa classe rara. Suponha uma classe c com **dois** usuários de suporte,
caídos em folds diferentes — dois, não um, porque o desenho é user-disjoint: as janelas de um mesmo
usuário nunca se repartem entre folds, então uma classe com um único usuário de suporte só pode ter
verdade-terreno num único fold. No fold A, o usuário de suporte rende 1 TP e o modelo ainda comete
2 FP na classe; no fold B, o outro usuário rende 0 TP e 1 FN. A média-de-fold calcula F1
separadamente em cada fold (o fold B, com TP=0 e FN=1, dá F1=0) e tira a média dos F1s — dando peso
igual a um fold que teve pouquíssima informação sobre a classe. O pooling soma os contadores
primeiro (TP=1, FP=2, FN=1) e calcula F1 uma única vez sobre a soma. O protocolo cita essa
diferença como responsável por um viés medido de **−0,24 pp na estrutura de Alabama**, superior a
metade da margem de não-inferioridade que o próprio documento adota (δ = 0,4 pp) — ou seja, o vício
de agregação, sozinho, já consome mais da metade do orçamento de decisão do teste principal.

### A literatura por trás

Duas fontes sustentam essa escolha, com papéis diferentes:

- Forman & Scholz, "Apples-to-apples in cross-validation studies" (*ACM SIGKDD Explorations
  Newsletter*, 2010), é a referência clássica sobre por que a forma de agregar métricas por fold
  decide o que a comparação mede, e recomenda tratar contagens agregadas como a unidade correta em
  vez de médias de métricas já resumidas.
- Tsamardinos, Greasidou & Borboudakis, "Bootstrapping the out-of-sample predictions for efficient
  and accurate cross-validation" (*Machine Learning*, 2018), formalizam o princípio geral de
  reunir as predições fora-de-amostra de todos os folds antes de calcular a métrica, em vez de
  calcular a métrica fold a fold e depois resumir — o método de bootstrap que propõem reamostra
  linhas, e é citado no protocolo apenas pelo princípio de pooling, não pelo esquema de
  reamostragem (esse é outro, ver §3).

### A convenção de macro-F1 em si

Existe uma armadilha adicional, independente de pooling: "macro-F1" tem **duas definições
não-equivalentes** na literatura — uma que calcula F1 por classe e tira a média (a que o protocolo
usa), e outra que calcula precisão e recall macro separadamente e só então combina os dois macro-
médios num único F1. Opitz & Burst, "Macro F1 and Macro F1" (arXiv:1911.03347, 2019 — conferido
via busca web em 21-08, ver ledger de fontes), documentam essa duplicidade e mostram que as duas
fórmulas produzem números diferentes no caso geral (a diferença pode chegar a 0,5 em construção
adversarial). É por isso que o protocolo fixa por escrito, em texto, qual das duas convenções está
usando — a ambiguidade não é cosmética, é uma fonte de erro de comparabilidade entre trabalhos que
dizem medir "a mesma coisa".

**Diagnóstico obrigatório.** Pooling OOF pode mascarar quando um ganho de macro-F1 é carregado por
uma única classe rara que teve sorte de amostragem. Por isso o protocolo exige, ao lado de todo
delta de macro-F1, uma tabela de 7 linhas (uma por classe) com o delta pareado por classe,
rotulada como descritiva — não como um segundo teste de hipótese.

---

## 2 · O fluxo outer-test / inner-val / treino — onde a época é escolhida e por quê isso importa

### Os três blocos, e o que cada um faz

O desenho particiona os usuários de cada estado em três blocos por fold, sempre **user-disjoint**
(nenhum usuário aparece em mais de um papel dentro do mesmo fold):

| Bloco | Fração | Papel | Quem pode olhar |
|---|---:|---|---|
| **treino** | ~70% | ajusta os pesos do modelo | o otimizador |
| **inner-val** | 10% (um fold de um SGKF 8-way sobre o bloco de 80%) | escolhe qual checkpoint (época) reportar | a regra de seleção — **nunca** o outer-test |
| **outer-test** | 20%, um dos 5 folds do StratifiedGroupKFold externo | é lido **uma vez** por braço, por ciclo de congelamento | ninguém, até a leitura final |

O ponto estruturante: o outer-test é **lacrado**. Ele não participa de nenhuma decisão — nem de
qual época usar, nem de qual hiperparâmetro promover. Ele existe só para ser lido, uma vez, depois
que todas as decisões já foram tomadas usando apenas o inner-val. (E "uma vez" é sobre a tabela OOF
concatenada dos cinco folds, não sobre cada fold — a rotação está desenhada no §0.)

### A época não é escolhida pela loss de validação

Esse é o ponto que o protocolo torna explícito e que é fácil de assumir errado por hábito: o
critério de seleção de checkpoint **não é necessariamente a menor loss de validação**. É a métrica
que o braço realmente reporta:

- Para os braços STL (categoria dedicada, região dedicada): a época com o **melhor valor da própria
  métrica de interesse** no inner-val — macro-F1 para o braço de categoria, Acc@10 (`top10_raw`)
  para o braço de região.
- Para o braço conjunto (joint): a época com o melhor valor de um seletor único,
  `geom_simple = sqrt(cat_macroF1 × reg_Acc@10)`, calculado também só sobre o inner-val
  (implementado em `train/stats.py::geometric_joint`).

### A defesa do `geom_simple` — a verdadeira, não a de sala limpa

A defesa do `geom_simple` **não é uma derivação de primeiros princípios**, e o protocolo proíbe
apresentá-la assim. O seletor foi adotado **pós-hoc**, à luz de resultados em estados de
desenvolvimento (o episódio C21: o seletor anterior, `0.5·(cat_f1+reg_f1)`, estava quebrado, e a
troca recuperou +5,62 pp de reg deployable), e o próprio protocolo registra esses +5,62 pp como
**otimismo de nível de seletor a favor do braço joint** (§8a do protocolo). A defesa real tem três
pés, todos verificáveis:

1. a adoção é **declarada** — com origem, data e magnitude, não escondida;
2. o seletor foi **congelado no pré-registro antes de qualquer leitura confirmatória**, datado em
   git — depois disso ele não pôde mais ser trocado à luz de resultado nenhum;
3. o contrato é **simétrico**: todo braço, joint e STL, escolhe checkpoint no inner-val sob uma
   regra fixada de antemão, e nenhum lê o outer-test para escolher nada.

(A média geométrica em vez da aritmética tem uma razão mecânica — as duas métricas vivem em escalas
de dificuldade muito diferentes, 7 classes contra até 8.501, e a aritmética deixaria a tarefa fácil
dominar o seletor — mas isso é racionalização registrada **depois** da escolha, não a justificativa
da escolha. Confundir as duas é exatamente a alegação-acima-da-evidência que o §0.1 cataloga.)

### Por que essa regra é o ponto mais estruturante do protocolo

Se o braço STL puder colher, para cada tarefa separadamente, a época que maximiza aquela tarefa no
outer-test (ou pior, "max-over-epochs" sem nem passar pelo inner-val), e o braço joint for
obrigado a reportar um único checkpoint escolhido de antemão, a comparação principal do trabalho
inteiro fica estruturalmente enviesada a favor do STL — não porque o STL seja melhor, mas porque
teve mais chances de acertar por sorte de qual época parar. Isso é exatamente o mecanismo descrito
por Cawley & Talbot, "On Over-fitting in Model Selection and Subsequent Selection Bias in
Performance Evaluation" (*Journal of Machine Learning Research*, 11(70):2079–2107, 2010 —
conferido via busca web em 21-08 na página do JMLR, ver ledger de fontes): quando a variância do
próprio critério de seleção não é contabilizada, o desempenho relatado carrega um viés otimista
que pode ser confundido com uma diferença real entre métodos.

O protocolo fecha esse buraco com uma regra de **simetria de seleção**: todo braço — joint e STL —
usa exatamente o mesmo contrato (checkpoint escolhido no inner-val, uma única leitura do
outer-test). Nenhuma tabela-manchete pode usar "melhor época" lida diretamente do outer-test para
nenhum braço.

### Um efeito vizinho, medido — e o que ele não é

`GATES_2026-08-17.md` registra que, em Alabama, um schedule de treino de **20 épocas supera um de
50 épocas** em macro-F1 de categoria por **+0,354 ± 0,095 pp**. O piso aplicável a esse número é a
banda de **delta pareado entre configurações diferentes** (0,05–0,15 pp entre repetições, §3), e o
efeito fica ~2,4× acima do topo dela — separado, mas não "7×": o piso de 0,02–0,05 pp entre duas
execuções idênticas governa re-rodar a MESMA configuração, e não se aplica a um delta entre dois
schedules distintos. O mecanismo, visível no baseline: o modelo atinge seu melhor resultado por
volta da época 13 de 50, e o schedule de 50 épocas acaba bancando um checkpoint no meio da rampa de
anneal. Isso é uma medição sobre **duração do schedule**, não uma medição do custo da regra de
seleção por max-over-epochs discutida acima — as duas questões são vizinhas (ambas giram em torno
de que ponto do treino um checkpoint é lido), mas não são a mesma medição, e não devem ser
fundidas.

---

## 3 · Tier A e Tier B — duas perguntas diferentes, dois "n" diferentes

### A distinção central

O protocolo separa toda inferência estatística em dois níveis, e exige que **todo número publicado
diga a qual nível pertence**:

**Tier A — generalização de usuário.** A pergunta: "se eu pegasse outra amostra de usuários deste
mesmo estado, esse delta se manteria?" A unidade de reamostragem é o **usuário**, via bootstrap
pareado em cluster de usuário sobre as predições OOF agregadas (≥10.000 réplicas). Como cada
usuário cai em exatamente um fold (desenho user-disjoint), reamostrar um usuário carrega consigo
todas as suas janelas, os dois braços e todas as seeds — um replicate é então uma soma ponderada,
recalculável em segundos. É este nível que sustenta toda alegação-manchete e toda margem de
equivalência.

**Tier B — comparação condicional de configuração.** A pergunta: "dado exatamente os dados e os
ajustes que eu já rodei, esta versão bate a outra?" A unidade é a **réplica** (o que o projeto
chamava de "seed" — ver `NOMENCLATURE.md`): o delta pareado OOF por réplica, com uma banda sobre
o desvio dessas réplicas, exatamente o que `train/stats.py::compare` já calcula hoje. Este nível
nunca é citado como intervalo de generalização — ele resolve efeitos de 0,05–0,15 pp, mas resolve
apenas "v2 bate v1 nestes dados fixos", não "v2 bateria v1 numa nova amostra de usuários".

### A analogia

Pense em Tier B como pesar duas vezes o **mesmo saco de arroz** em duas balanças diferentes: a
diferença de leitura entre as balanças é real e mensurável, mas não diz nada sobre se um saco
diferente do mesmo fornecedor pesaria igual. Tier A é pesar **vários sacos** amostrados do estoque
inteiro do fornecedor: a variação entre sacos é a incerteza que realmente importa para "o
fornecedor entrega X kg em média", mas custa mais para medir (é preciso reamostrar usuários, não só
reler o mesmo resultado já rodado).

### A literatura por trás de cada peça do Tier A

- Field & Welsh, "Bootstrapping Clustered Data" (*Journal of the Royal Statistical Society, Series
  B*, 2007), é a referência para reamostrar clusters — aqui, usuários — em vez de linhas
  individuais, quando as observações dentro de um cluster (as janelas de um mesmo usuário) não são
  independentes entre si.
- Efron, "Better Bootstrap Confidence Intervals" (*Journal of the American Statistical
  Association*, 82(397):171–185, 1987 — DOI 10.1080/01621459.1987.10478410, conferido via busca
  web em 21-08 na página da Taylor & Francis, ver ledger de fontes), é a fonte do intervalo BCa
  (bias-corrected and accelerated) — o protocolo reporta tanto o intervalo percentil quanto o BCa
  e sinaliza quando os dois discordam, em vez de escolher um só e esconder a discrepância.
- Chung & Romano, "Exact and asymptotically robust permutation tests" (*Annals of Statistics*,
  2013), sustentam o teste de permutação de sinal para a superioridade dentro do Tier A: a
  estatística é **estudentizada** para que o teste permaneça válido tanto sob a hipótese nula
  pontual (as duas distribuições são idênticas) quanto sob a hipótese nula mais fraca (só as médias
  das métricas coincidem) — uma permutação não-estudentizada só é exata sob a hipótese pontual, que
  é mais forte do que o que o protocolo quer afirmar.

### O motivo de o Tier B nunca ser promovido a Tier A

Como o `NOMENCLATURE.md` deste projeto documenta (achado interno, não da literatura externa): os
folds dentro de uma partição compartilham ~75–80% dos dados de treino, então cinco leituras de um
mesmo "seed" não são cinco réplicas independentes — são cinco pedaços complementares de um único
particionamento. O `n` correto para o Tier B é o número de **réplicas** (R = 4 nos estados-ponte,
R = 2 nos estados grandes), nunca `réplicas × folds`. O protocolo herda essa regra diretamente:
`stderr` em `PairedComparison` é calculado sobre `seed_deltas` (um delta por réplica, com os
folds já promediados dentro dela), nunca sobre os pares (réplica, fold) individuais.

---

## 4 · Quantas réplicas cada conjunto banca, e quem decide isso

> **Réplica ≠ repetição** — [`NOMENCLATURE.md`](NOMENCLATURE.md) §2 é o normativo. A campanha v19
> pina a partição e varia a semente de modelo: são **réplicas**.
>
> ⚠ **DESFECHO, 2026-08-24.** Esta seção argumenta que 2 réplicas bastariam nos conjuntos grandes.
> O gate abaixo foi computado na leitura da ponte e **REPROVOU em região** — os três grandes vão a
> quatro. O argumento continua aqui porque explica o gate; **a conclusão dele não vale**. Estado
> corrente: [`studies/v19_defence/STATE.md`](../studies/v19_defence/STATE.md); a regra e o porquê:
> protocolo §12.7.
>
> A banda de 0,05–0,15 pp citada abaixo é **escala, não limite**: foi medida quando `seed` movia os
> dois fatores, noutro estado. A medida real da ponte (região do Arizona: 0,317, mais que o dobro do
> teto) é o que o gate usa — `sd_source = "bridge"`.

### As duas fontes de ruído não escalam da mesma forma

O desenho distingue duas fontes de incerteza que se comportam de maneiras opostas quando o estado
cresce:

1. **Ruído de repetição** (partição + inicialização, confundidos — ver `NOMENCLATURE.md` §1):
   medido em **0,05–0,15 pp** para o delta pareado entre repetições. Esse número **não depende do
   tamanho do estado** — é uma propriedade de como a otimização e o particionamento variam de uma
   repetição para outra, não de quantos usuários existem no estado.
2. **Ruído de amostragem de usuário**: escala aproximadamente como **1/√(número de usuários)**.
   Alabama tem **1.101 usuários** sob o substrato v18 — a contagem selada em
   [`SEALED_BRIDGE_READ.md §4`](../studies/porting_validation/SEALED_BRIDGE_READ.md); a cifra
   3.858, que este guia e o próprio protocolo (§6, §9.2) carregaram, vem da janelagem v17
   (MIN_SEQ=5, stride 9) e está errada para este desenho, fator 3,5. A meia-largura de bootstrap
   de usuário **realizada** em AL foi **0,199–0,222 pp** (a projeção pré-leitura, ~0,25–0,3 pp,
   era pessimista — provavelmente por não creditar todo o ganho do pareamento). Texas tem ~35×
   mais usuários — **38.644 na contagem v17; a contagem v18 não foi medida e será menor, pelo
   mesmo corte de janelagem** — e meia-largura projetada de ~0,02–0,08 pp: há muito mais usuários
   para "diluir" a variação de amostragem.

A consequência aritmética: em Texas, o ruído de amostragem de usuário já é **menor** do que o
próprio ruído de refit. Rodar 4 réplicas em vez de 2 reduziria a meia-largura efetiva desse
componente em no máximo ~0,06 pp (fator 1/√2 sobre uma banda que já é pequena) — um ganho invisível
ao lado do componente de usuário, que domina. Em Alabama, onde o componente de usuário é maior, a
mesma lógica não se aplica automaticamente — é por isso que os estados-ponte recebem 4 réplicas:
elas servem tanto para a comparação com o sistema legado quanto para **calibrar** se a suposição
"2 réplicas bastam" realmente se sustenta antes de aplicá-la aos estados grandes.

### O gate de calibração — não é uma suposição livre

O protocolo não assume "2 é suficiente para estados grandes" por decreto. Ele condiciona a decisão
a uma regra mecânica, verificável a partir dos números medidos nos estados-ponte:

> S = 2 réplicas **apenas se** o desvio-padrão de réplica calibrado, dividido por √2, for menor
> ou igual a um terço do menor entre (o menor efeito de interesse, a folga da margem de TOST) —
> caso contrário, começar com S = 4 desde o início.

E, além do gate inicial, há uma **regra de escalada durante a execução**, também mecânica e
pré-registrada, não uma decisão pontual:

1. as duas réplicas discordam em sinal e a diferença absoluta excede o envelope calibrado
   (2 desvios-padrão);
2. `|Δ_réplica0 − Δ_réplica1| > 3·desvio·√2` (envelope de ~99,7%, com taxa de falso disparo
   conhecida de ~0,3%);
3. **teste de sensibilidade do veredito**: recalcular o veredito da §3 do protocolo deslocando
   Δ̂ em ±2·desvio/√S — se o veredito muda de lado, escalar para 4 réplicas; se ainda ficar
   instável, reportar "limitado por réplicas nesta margem", nunca forçar uma conclusão.

O documento também é honesto sobre a alternativa que descartou: um gatilho fixo de 0,15 pp
dispararia entre 3% e 48% das vezes, dependendo de onde na banda medida o ruído real cai — um
gatilho calibrado tem uma taxa de falso disparo conhecida e constante, o que um limiar fixo não
oferece.

### A fonte geral sobre por que medir variância antes de decidir orçamento de réplicas

Bouthillier et al., "Accounting for Variance in Machine Learning Benchmarks" (MLSys, 2021 —
conferido via busca web em 21-08, ver ledger de fontes), argumentam pelo mesmo princípio em escala
mais ampla: comparar dois métodos de forma defensável exige medir empiricamente, e não presumir,
cada fonte de variação — amostragem de dados, inicialização, escolha de hiperparâmetros — antes de
decidir quantas réplicas cada uma delas exige. É a mesma lógica que aqui vira uma tabela de
"1,2 pp entre folds; 0,05–0,15 pp entre repetições; 0,02–0,05 pp entre execuções idênticas;
0,18 pp numa reinstanciação ponta-a-ponta (medida uma vez); 0,034 pp entre quatro sorteios do
substrato" — os dois últimos são quantidades **diferentes**, distinguidas na próxima seção, e é a
tabela inteira que alimenta a âncora de δ.

---

## 5 · Por que δ = 0,4 pp é mais rigoroso que o costume de ~1 pp, não menos

### O ponto que costuma confundir

É tentador ler "nossa margem é 0,4 pp, mais estreita que a margem-exemplo de ~1 pp citada por
Benavoli et al." e concluir que o protocolo relaxou o padrão. É o oposto: δ entra **apenas** nos
testes que usam margem — a não-inferioridade (um teste unilateral, §6) e a equivalência (TOST,
§6) — nunca no teste de superioridade. Um δ menor torna a equivalência **mais difícil** de
declarar — porque a banda que os dados precisam caber dentro dela é mais estreita — não mais fácil.

Para deixar isso concreto: TOST declara equivalência quando o intervalo de confiança de 90% do
delta está inteiramente contido em (−δ, +δ). Encolher δ encolhe a janela de aceitação. Um efeito
real de +0,3 pp, por exemplo, passaria facilmente numa janela de ±1 pp mas pode falhar numa janela
de ±0,4 pp se o intervalo de confiança for largo o bastante para tocar a borda — é exatamente o
caso documentado em `GATES_2026-08-17.md` (Arizona/região a 30 épocas: delta de +0,148 pp, banda
recalculada de ±0,224 pp, portanto **não separado**, apesar de ter sido reportado como separado sob
a banda antiga com multiplicador errado).

### A cadeia de âncoras — por que 0,4 e não outro número

O protocolo deriva δ de três pisos, em ordem, e nenhum deles depende de nenhum delta A-vs-B —
é isso que o torna não-circular:

1. **Piso de decidibilidade**: δ precisa exceder 2× o maior componente de ruído relevante ao
   par. O topo da banda medida de repetição pareada é 0,15 pp, então δ ≥ 0,3 é o mínimo para o
   teste sequer ser decidível.
2. **Piso de reinstanciação**: reconstruir a mesma configuração do zero, **ponta a ponta** (mesmo
   método, execução nova, pipeline inteiro), moveu o número em ~0,18 pp — **medido uma vez**, e é
   esse valor, pré-registrado no protocolo, que ancora δ. Não confundir com o outro piso de
   reconstrução que este projeto mediu depois: **0,034 pp entre quatro sorteios do substrato**
   ([`SUBSTRATE_FROM_SCRATCH.md`](../studies/porting_validation/SUBSTRATE_FROM_SCRATCH.md) — só a
   semente do sorteio muda, mesmo construtor, mesmo downstream, medido em validação interna). São
   quantidades diferentes, e os 5× entre elas são esperados: 0,18 é a reinstanciação do pipeline
   inteiro; 0,034 é a dispersão de UM componente (o sorteio do substrato) com todo o resto fixo.
   O protocolo trata medições novas de piso como **validação da âncora, nunca reajuste** — só uma
   discrepância acima de 0,2 pp seria reportada contra a âncora, e 0,034 não é uma (fica abaixo,
   como deveria: mede menos coisa). Para uma alegação que precisa valer além de "rodei de novo e
   deu um número um pouco diferente", um efeito abaixo de ~2×0,18 ≈ 0,4 pp é operacionalmente
   indistinguível de reconstruir você mesmo. Bouthillier et al. (MLSys, 2021 — conferido via busca
   web em 21-08) são o precedente direto: medir o ruído de reconstrução como a régua para decidir o
   que conta como diferença que importa.
3. **Teto externo**: o valor final ainda fica **mais estrito** que o exemplo de referência de ~1
   pp discutido por Benavoli, Corani, Demšar & Zaffalon, "Time for a Change: a Tutorial for
   Comparing Multiple Classifiers Through Bayesian Analysis" (*Journal of Machine Learning
   Research*, 18(77):1–36, 2017 — conferido via busca web em 21-08, ver ledger de fontes), que
   citam uma região de equivalência prática (ROPE) da ordem de ~1 pp como exemplo costumeiro na
   literatura de comparação de classificadores — citado no protocolo como exemplo de prática
   comum, não como uma convenção formal a seguir.

### O apêndice de sensibilidade obrigatório

Como δ é, por admissão do próprio protocolo, "um julgamento de valor vestido de medição", todo
veredito de equivalência é obrigatoriamente reapresentado em δ ∈ {0,2; 0,4; 1,0} pp — de modo que
o leitor veja em que ponto exato a decisão mudaria se a margem fosse outra, em vez de confiar
apenas no número único escolhido.

### 5.1 · O δ-crítico — publicar a nota, não o carimbo

Os três pontos de sensibilidade acima são três amostras de uma curva contínua. O **δ-crítico** é
essa curva resumida num número, e responde a pergunta que o veredito binário engole:

> *A partir de que margem esta célula mudaria de veredito?*

**Ele não é escolhido. É lido do intervalo, por subtração.**

A regra de não-inferioridade é "o limite inferior do IC está acima de −δ". Escrevendo o intervalo
como `[L, U]`:

```
não-inferior em δ   ⟺   L > −δ   ⟺   δ > −L
```

Logo o ponto de virada é exatamente `δ_NI = max(0, −L)`. E, simetricamente, a célula é declarada
inferior enquanto `δ < δ_inf`, com `δ_inf = max(0, −U)`. A meia-largura `(U − L)/2` é a **resolução
do instrumento** naquela célula — o menor efeito que ela conseguiria distinguir.

Exemplo real, da primeira leitura selada (Alabama, região):

| o carimbo diz | o δ-crítico diz |
|---|---|
| "inconclusivo a δ = 0,4" | "seria não-inferior a partir de **δ = 1,149 pp**" |

A segunda frase carrega tudo que a primeira carrega, e mais: 1,149 pp está **acima do teto de ~1 pp**
que a literatura de comparação em ML usa como ROPE generoso. Nenhuma margem defensável salva aquela
célula — o que é uma afirmação mais forte e mais honesta do que "inconclusivo".

#### Por que isto importa mais do que parece

1. **É a única peça da leitura cuja validade não depende da arquitetura que produziu as linhas.**
   Todo o resto deste guia — a margem, os gatilhos, a regra de réplicas — saiu de medições feitas
   nesta arquitetura e neste corpus. O δ-crítico é uma subtração sobre um intervalo que já existe.
   Um leitor futuro, com outro modelo e outra margem, relê a nossa tabela sem reconstruir nada.

2. **Torna a transferência entre conjuntos verificável em vez de suposta.** O δ-crítico de região é
   monótono no tamanho do conjunto — 1,149 pp com 1 101 usuários, 0,636 com 2 136, 0,282 com
   14 530. Quem for aplicar este protocolo a outro conjunto olha essa coluna e sabe o que esperar,
   em vez de herdar uma margem calibrada nos nossos seis. ⚠ A monotonia está confundida com o
   número de classes e com a fonte dos dados; é legenda de tabela, não achado.

3. **Não é análise nova.** Recomputados sobre os intervalos da leitura selada, os quatro δ-críticos
   reproduzem 6/6 dos vereditos já bancados. É re-expressão do mesmo objeto — e por isso é
   conformidade com o apêndice de sensibilidade que o §3 do protocolo já torna obrigatório, e não
   uma margem nova entrando pela porta dos fundos.

#### O que ele NÃO é

Não é licença para escolher a margem depois de ver o resultado. O veredito pré-registrado continua
sendo o de δ = 0,4 pp, e é ele que a manchete carrega. O δ-crítico vai **ao lado**, como o mapa
completo do qual aquele veredito é um ponto.

#### Onde ele sai

A leitura imprime os três, e o payload de `--json` os traz em `delta_critical`: `non_inferiority`
(acima dela o veredito é não-inferior ou superior), `inferiority` (abaixo dela o intervalo inteiro
fica sob −δ) e `tost` (a meia-largura, que é o δ a partir do qual o TOST é reivindicável). São
subtrações do intervalo de 90 %, e são do veredito **marginal** — o Holm move o p, não o intervalo.

Um invariante que vale conhecer: na margem crítica, o p unilateral de não-inferioridade vale
exatamente o α do nível. Os dois saem do **mesmo** endpoint BCa, então a coluna do p e a coluna do
intervalo não podem discordar. Medido: 0,049915 contra o alvo de 0,05, num bootstrap de 400.

---

## 6 · O gatekeeping sequencial NI → superioridade, passo a passo

### O problema que o gatekeeping resolve

Sem uma regra fixada de antemão, seria possível escolher, depois de ver os dados, se testar
superioridade ou equivalência em cada estado — e isso é exatamente o tipo de grau de liberdade que
infla a taxa de falsos positivos sem nunca aparecer como "p-hacking" óbvio. O protocolo fecha essa
porta com uma ordem fixa, testada com o mesmo α em ambos os passos (não é necessário corrigir por
múltiplas comparações entre os dois passos porque a segunda pergunta só é feita quando a primeira
já foi respondida positivamente — o mecanismo de troca NI → superioridade padrão em ensaios
clínicos, referenciado no protocolo via a orientação regulatória CPMP/EWP/482/99 da EMA, 2000).

### Os nomes certos, antes do passo a passo

Três testes diferentes usam o mesmo vocabulário e é fácil trocá-los — a prosa deste guia já os
trocou; o código nunca:

| teste | o que é | condição (como em `eval/compare.py::Equivalence`) |
|---|---|---|
| **não-inferioridade (NI)** | **UM** teste unilateral | limite inferior do IC > −δ (`non_inferior`: `interval[0] > -margin`) |
| **equivalência (TOST)** | **DOIS** testes unilaterais (*two one-sided tests*) | IC de 90% inteiramente contido em (−δ, +δ) — os dois limites checados separadamente (`equivalent`) |
| **superioridade** | teste de diferença contra zero | permutação estudentizada significativa **e** IC excluindo 0 na mesma direção |

Equivalência implica não-inferioridade; a recíproca não vale. NI **não é** TOST — TOST é o ramo de
equivalência, e chamá-lo de NI esconde que a NI só constrange um dos dois lados.

### O passo a passo

Para cada par (estado, tarefa):

**Passo 1 — não-inferioridade (NI), sempre testado primeiro.**
Hipótese nula: o joint é pior que o STL por mais que δ (H0: Δ ≤ −δ). Um único teste unilateral:
rejeita-se a nula quando o limite inferior do intervalo de confiança do delta fica acima de −δ.
Se a nula é rejeitada, o joint é declarado **não-inferior**. (Quando *também* o limite superior
cai abaixo de +δ, os dois testes unilaterais do TOST passaram e pode-se declarar, adicionalmente,
**equivalência prática** — é isso que o relatório anota como "(and equivalent)".)

**Passo 2 — superioridade, testado apenas se o passo 1 passou.**
Hipótese nula: não há diferença (H0: Δ = 0), testada pelo teste de permutação estudentizado do
Tier A (§3), com confirmação exigindo que o intervalo de confiança do bootstrap exclua zero na
mesma direção.

### As quatro saídas possíveis — o "termômetro"

```
        inferior          inconclusivo         não-inferior          superior
   ──────┼───────────────────┼──────────────────────┼───────────────────┼──────
        −δ                   0
   (todo o IC        (não passou NI          (passou NI,        (passou NI e
    abaixo de −δ)      nem superioridade)     não passou            passou
                                              superioridade)      superioridade)
```

| Veredito | Condição | O que pode ser dito |
|---|---|---|
| **superior** | passou NI **e** passou superioridade (permutação + IC excluindo 0) | "melhor que o STL, com diferença separada de zero" — isto **não** diz que a diferença excede δ; superioridade é sobre o zero, não sobre a margem. Se \|Δ̂\| < δ, a dupla notificação abaixo é obrigatória |
| **não-inferior** | passou NI, não passou superioridade | "não pior que o STL além de δ; diferença não distinguível de zero" |
| **inferior** | IC inteiramente abaixo de −δ | "pior que o STL além da margem pré-registrada" |
| **inconclusivo** | não passou NI nem inferioridade clara | "indeterminado nesta margem" — nunca colapsado em "não-inferior" nem em "inferior" |

### A regra que impede esconder metade da informação

Um caso frequente e fácil de reportar mal: o teste de superioridade dá **significativo**, mas o
tamanho do efeito medido (|Δ̂|) é **menor que δ**. O protocolo proíbe reportar isso como só
"superior" (que sugere um efeito grande) ou só "dentro da margem" (que esconde que havia um sinal
estatístico real). A regra de **dupla notificação** exige a frase completa: *"significativo, e
dentro da margem prática pré-registrada"* — as duas metades, sempre juntas, nunca uma no lugar da
outra. (É a mesma aritmética da tabela acima: "superior" fala do zero, δ fala da relevância
prática, e os dois eixos são independentes.)

### As fontes por trás de cada peça

- Schuirmann, "A comparison of the Two One-Sided Tests Procedure and the Power Approach for
  assessing the equivalence of average bioavailability" (*Journal of Pharmacokinetics and
  Biopharmaceutics*, 1987), é o artigo original do procedimento TOST.
- Lakens, "Equivalence Tests: A Practical Primer for t-Tests, Correlations, and Meta-Analyses"
  (*Social Psychological and Personality Science*, 8(4):355–362, 2017 — DOI
  10.1177/1948550617697177, conferido via busca web em 21-08 na página da SAGE, ver ledger de
  fontes), é a referência didática moderna para aplicar TOST fora do contexto farmacocinético
  original, incluindo a prática de pré-registrar a margem antes de ver os dados.
- Wellek, *Testing Statistical Hypotheses of Equivalence and Noninferiority* (2ª ed., Chapman &
  Hall/CRC, 2010 — a **existência** da obra foi conferida via busca web em 21-08; o conteúdo não
  foi consultado nesta sessão e a linha abaixo é citação de segunda mão), é o tratamento de
  referência mais completo sobre a teoria de testes de equivalência e não-inferioridade.
- Chung & Romano (2013, já citado no §3) sustenta o teste de superioridade que só roda depois do
  NI passar.

---

## 7 · Como rodar um estudo GRANDE sem gastar o conjunto de teste

> Escrito 2026-08-18, a pedido do autor, porque a explicação anterior não ficou clara. Esta é a
> seção prática: se você vai testar dez arquiteturas, vinte features ou cinquenta variações, leia
> **só esta seção** antes de começar.

### 7.1 · A resposta curta

**Você não congela dados antes do estudo. Os dados já estão congelados — desde sempre, em toda
execução.** O que você administra é *outra coisa*: **quantas vezes você tem permissão de OLHAR** o
pedaço congelado.

O quase-mal-entendido a desfazer: não é "separo um teste agora para este estudo". É "o teste já
está separado; a pergunta é quando eu gasto o direito de vê-lo".

### 7.2 · Os três pedaços, e quem pode ver o quê

A partição é a do mapa do §0 — 70 % treino, 10 % validação interna, 20 % teste externo, sempre
**disjuntos por usuário** (nenhum usuário aparece em dois papéis; é isso que faz o número final
significar "usuários novos"). O que importa aqui é o orçamento de olhadas:

- **Treino (70 %)** e **validação interna (10 %)**: olhe quantas vezes quiser. Rode cinquenta
  variantes, compare todas contra a base, escolha vencedores. **Custo para o teste: zero.**
- **Teste externo (20 %)**: sua reserva. Cada leitura gasta — e "uma leitura" é a pontuação da
  tabela OOF concatenada dos 5 folds externos, uma vez por braço, por ciclo (§0).

### 7.3 · O ciclo prático — o que você realmente faz

Exatamente o fluxo que o autor descreveu (`cat`, `cat+f1`, `cat+f1+f2`, …), mas com o instrumento
certo em cada etapa:

**Etapa 1 — TRIAGEM (quantas variações quiser, custo zero de teste).**
Rode tudo. Compare tudo contra a base. Use **só a validação interna**. A ferramenta é o **Tier B**:
delta pareado sobre réplicas numa partição congelada, que enxerga diferenças de 0,05–0,15 pp — de
sobra para ordenar candidatos.
Regra de promoção do protocolo: Δ pareado ≥ 0,15 pp entra na lista curta.

**Etapa 2 — CONGELAMENTO.**
Você escolheu 3–5 braços em que acredita. Congele: receita, arquitetura, hiperparâmetros, regra de
seleção. A partir daqui, **nada muda**.

**Etapa 3 — CONFIRMAÇÃO (uma leitura, todos os braços de uma vez).**
Agora sim leia o teste externo — **uma vez**, para a lista curta inteira, com uma correção de
multiplicidade só (Holm na família manchete). É o `mtlcheck compare`.

> **A frase que resume tudo:** o teste externo **não é um instrumento por experimento; é um
> instrumento por ciclo de congelamento.** Você não o lê N vezes para N arquiteturas. Lê uma vez,
> para a lista curta.

### 7.4 · "E se, depois de ver, eu quiser mudar algo?"

Pode — mas então aquela leitura **deixa de ser confirmatória** e vira exploratória (critério de
auditoria 7). Não é castigo moral, é aritmética: se você escolheu a variante *porque* ela ganhou no
teste, o número dela contém a sorte que a fez ganhar. É o *winner's curse*, e nenhuma correção
estatística o desfaz — só uma confirmação nova, em dado que não participou da escolha.

O que **não** contamina, e você pode fazer à vontade depois de olhar:

| mudança | contamina? | por quê |
|---|---|---|
| telemetria, monitoramento, logging | **não** | não toca modelo, dado, receita nem estimando |
| correção de bug | **não** (mas declare) | o número anterior estava errado; o novo não foi escolhido pelo teste |
| refatoração, performance, infraestrutura | **não** | mesmo modelo, mesma matemática |
| **receita, arquitetura, hiperparâmetro, cabeça, regra de seleção** | **SIM** | foi escolhida à luz do teste |

### 7.5 · O que dá fôlego: dividir os CONJUNTOS, não os experimentos — e o mapa honesto de quem já foi tocado

Os conjuntos não precisam ser gastos juntos — essa é a parte prática que resolve o problema de
verdade. **São sete**: cinco estados do Gowalla (Alabama, Arizona, Flórida, Califórnia, Texas),
Istambul e Jakarta (Massive-STEPS).

Mas a divisão só funciona se o mapa de contaminação for verdadeiro. O estado real de cada
conjunto, com as fontes:

| conjunto | leitura de teste | decisões tomadas nele (modelo dedicado de categoria, salvo indicação) |
|---|---|---|
| Alabama | teste externo selado **lido em 2026-08-18** ([`SEALED_BRIDGE_READ.md`](../studies/porting_validation/SEALED_BRIDGE_READ.md)) | batch **e** LR buscados em 5 folds; receita H3-alt desenvolvida aqui; joint buscado |
| Arizona | idem, **lido em 2026-08-18** | batch **e** LR buscados em 5 folds; joint buscado |
| Istambul | idem, **lido em 2026-08-18** | batch **e** LR buscados em 5 folds; joint buscado |
| Flórida | números do protocolo legado publicados (a "leitura" legada não era selada) | batch buscado; **LR nunca variado** (carrega o valor das buscas menores); receita B9 desenvolvida aqui; joint sondado |
| Califórnia | números do protocolo legado publicados | batch buscado (oito braços sobre {2048, 8192}); **LR nunca variado** (ponto único, 0.005); joint **transferido** |
| Texas | números do protocolo legado publicados | batch buscado (menos folds); **LR buscado em folds únicos** (três pontos); joint **transferido** |
| Jakarta | nunca lida | nenhuma |

A fonte que governa a coluna de decisões é o setup da própria dissertação
(`articles/dissertacao/src/chapters/5_mobiwac/05_setup.tex`), que — depois de duas correções de
escopo, registradas lá em 2026-08-05/12 — declara os dois botões **separadamente**: para o modelo
dedicado de categoria, *batch size foi buscado nos seis conjuntos* (5 folds em Istambul/Alabama/
Arizona, menos folds em Flórida e Texas, oito braços na Califórnia) e *a taxa de aprendizado foi
buscada em quatro dos seis* — Istambul/Alabama/Arizona em 5 folds e **Texas em folds únicos** —
ficando **Flórida e Califórnia sem variação de LR** (carregam o valor que as buscas menores
escolheram). Para o joint, batch e LR da cabeça de categoria foram buscados em IST/AL/AZ e sondados
em FL; **Texas e Califórnia rodam configuração transferida**. O dedicado de região usa uma
configuração fixa nos seis. A nota da tabela (`tables/mobiwac/results.tex`) diz o mesmo. Uma
formulação mais forte que já circulou — "o dedicado foi tunado por dataset em batch **e** LR" —
superestima o escopo e foi corrigida na própria dissertação; e a formulação que já esteve neste
guia — "CA e TX não entraram na busca de LR" — erra para o Texas, que entrou, em folds únicos.
Os artefatos sustentam só a forma acima, com os dois botões separados.

**O que segue disso, e não é negociável:**

- **Não existe "reserva confirmatória" entre os sete, exceto Jakarta.** Pela definição deste
  próprio guia — um conjunto deixa de ser reserva no instante em que informa uma decisão ou é
  visto — todos os outros seis estão contaminados em algum grau: AL/AZ/IST por **leitura** (o ato
  mais caro) e por decisão; FL/CA/TX por **decisão** (busca de batch nos três, LR fino no TX,
  números legados publicados), ainda que nenhum dos três tenha tido o teste selado lido. CA e TX
  **nunca foram reserva**. O rótulo honesto para eles é **confirmatório-adjacente**: os menos
  contaminados dos seis — a contaminação é de decisão, relativamente rasa, não de leitura — e a
  única faixa grande que existe: os três maiores estados do Gowalla são TX, CA e FL, e o maior
  livre é Nova York, com 715 mil check-ins, seis vezes menor que o Texas.
- **Reserva de verdade é o pool nunca aberto — e as contagens precisam de reconciliação.** O
  protocolo (§11.2, verificação datada de 2026-08-17) conta em `data/checkins/` **67 corpora, dos
  quais o estudo usa 7; 60 nunca foram tocados** por decisão nenhuma. Contando por estado — as
  variantes `Arizona_cat*` são o mesmo estado — são 58 corpora distintos e ~51 nunca tocados. Uma
  cifra que este guia carregou ("52 estados do Gowalla, 14 cidades do Massive-STEPS intocados")
  não tem fonte que a sustente e não deve ser citada. O fato de carga sobrevive a qualquer
  contagem: a faixa pequena/média é reabastecível (NY 715 k, WA 608 k, IL 540 k, …), **a faixa
  grande não é**. E uma reserva dessas é **consumível e nomeada em pré-registro**, não permanente —
  ver [`POR_QUE_O_TESTE_ESPERA.md`](POR_QUE_O_TESTE_ESPERA.md).
- **A pergunta que isso transforma:** não é mais "como evito gastar o teste?" — é "**quantos ciclos
  de congelamento eu quero, e quais conjuntos pagam por cada um?**".

### ⚠ Conflito declarado com o protocolo congelado — emenda registrada como §12.3

O [`plans/EVALUATION_PROTOCOL.md`](plans/EVALUATION_PROTOCOL.md) — congelado; **não editar** —
diz em §9 (item 4) que *"Istanbul/CA/TX carry the confirmatory weight"*, e em §4b marca como
estados de desenvolvimento FL e AL (com AZ na justificativa). As duas atribuições precedem dois
fatos: (1) a leitura de Istambul em 2026-08-18, e (2) o reconhecimento de que CA/TX carregam busca
de batch do modelo dedicado (e TX também de LR) e números legados publicados. A posição corrigida
deste guia, e a decisão de papéis do autor para o v21 (abaixo), **contradizem o protocolo nesses
pontos**. O §12 do protocolo exige que qualquer mudança entre como **emenda datada e registrada**.

**Correção, 2026-08-24:** uma versão anterior deste bloco dizia que a emenda "ainda não foi escrita
e é devida". Ela **existe**: é o **§12.3** do protocolo, datado de 2026-08-21, que declara falsa a
premissa "CA/TX nunca foram estados de tuning", enumera o que sobrevive da atribuição de peso
confirmatório e o que não, e registra a leitura de Istambul. O que este bloco ainda governa é a
metade que não é matéria de protocolo: a decisão de papéis do v21 (abaixo) é deste guia, e a
proibição prática permanece — nenhuma alegação cita o §9.4 como se CA/TX fossem confirmatórios
limpos; cita-se o §12.3, que é o registro correto.

### Os papéis para o ciclo v21 — decisão do autor, 2026-08-21

| papel | conjuntos | por quê |
|---|---|---|
| **desenvolvimento** | Alabama · Istambul · Flórida · Califórnia | cobre 114 k a 3,2 M check-ins (28×), com pequeno, médio não-US, grande e muito grande |
| **fechados para o ciclo** | Arizona · Texas · **Jakarta** | cada um testa um eixo de transferência **diferente** |

O que cada conjunto fechado testa, e com que força:

| conjunto | check-ins | POIs | eixo | força |
|---|---:|---:|---|---|
| **Jakarta** | 412 100 | 76 116 | **fonte e época** — não-Gowalla, não-US, moderno | **a mais forte** |
| Texas | 4 089 892 | 160 938 | **escala** — 1,29× acima do maior de desenvolvimento | forte |
| Arizona | 236 450 | 20 666 | geografia em escala pequena | **a mais fraca** |

Jakarta tem 412 k check-ins mas **76 116 POIs — quase igual à Flórida (76 544)**. Como a tarefa de
região é dominada por cardinalidade e não por volume de check-ins, ela vale mais do que o número de
check-ins sugere.

O Arizona é o mais fraco por dois motivos que se somam: é 2× o Alabama na mesma plataforma e no
mesmo país (pouca transferência a testar), e **teve o teste externo lido em 2026-08-18** — alguém
já viu o número. O Texas não: o que ele tem é contaminação de **decisão** (batch; LR em folds
únicos), não de **leitura**.

### ⚠ O que estes conjuntos sustentam, e o que NÃO sustentam

Nenhum dos três fechados é intocado (Jakarta é a única limpa de verdade — nunca lida, nenhuma
decisão tomada nela). Todos os outros informaram decisões nos ciclos anteriores. Portanto:

> **A frase que NÃO se pode escrever:** "a v21 atinge X no Texas, um conjunto reservado."
>
> **A frase que se pode:** "a mudança da v20 para a v21 foi desenvolvida sem olhar o Texas, e o ganho
> se reproduz lá."

A segunda exige a peça do §7.6, cenário 2: **rodar o sistema ANTIGO também nesses conjuntos**, sob o
mesmo contrato. Sem isso compara-se um método tunado por meses contra um número de outro protocolo.

E se Arizona e Texas forem apresentados como sustentando a alegação do incremento, **o texto do
artigo tem de dizer que o batch size foi buscado neles** (e o LR no Texas, em folds únicos) — e que
o Arizona teve o teste externo lido em 2026-08-18. Omitir recria exatamente a contradição
"reserva intocada" que esta seção existe para desfazer: o leitor conclui "não olhado" onde o
registro do próprio programa diz o contrário.

### O compromisso que faz isso valer

O argumento do autor é que a v21 muda o suficiente para que o tuning da v20 não se transfira, o que
quebra a contaminação herdada. **Isso é válido na medida em que a v21 de fato re-derive as decisões**
— e portanto é compromisso, não previsão:

> Durante todo o ciclo v21, nenhum sweep, ablação ou hipótese roda em Arizona, Texas ou Jakarta. A
> v21 re-tuna nos conjuntos de desenvolvimento.

Se a v21 reaproveitar os hiperparâmetros da v20, o argumento evapora e os três voltam a ser
desenvolvimento.

E a alegação **degrada a cada ciclo**: vale para a v21 se a v21 foi cega a eles; a v22 precisa ter
sido cega de novo, e a essa altura a herança acumulada fica difícil de defender (§7.8 diz o que se
acumula e o que se pode afirmar sobre isso).

### A restrição que nenhuma política conserta

**A faixa grande não é reabastecível.** Os três maiores estados do Gowalla são TX, CA e FL — todos
usados. O maior livre é Nova York com 715 k, seis vezes menor que o Texas. Nenhuma cidade do
Massive-STEPS passa de 545 k.

Consequência: quando o Texas sair, **não há substituto para o eixo de escala**. A resposta honesta
será mudar a alegação, não procurar outro conjunto.

### 7.6 · Os quatro cenários de comparação, e o que cada um exige

Esta pesquisa faz quatro comparações diferentes, e elas têm exigências **diferentes**. Tratar todas
como "preciso de um conjunto reservado" é o que tornava a discussão confusa: três das quatro não
precisam.

| # | a comparação | precisa de conjunto reservado? |
|---|---|---|
| 1 | contra modelos da literatura | **não** |
| 2 | contra as nossas próprias abordagens anteriores | **sim** |
| 3 | dedicado contra joint | parcialmente |
| 4 | hipótese contra hipótese, durante o desenvolvimento | **não** |

#### Cenário 1 — contra a literatura

Você **tem** de usar os datasets dos artigos originais; é o que torna a comparação uma comparação.
Reservar não ajuda e não se aplica.

Reproduza primeiro os números publicados do artigo original antes de comparar. Isso valida o harness,
e quando falha você descobre antes de construir um argumento em cima.

⚠ **O risco deste cenário não é reuso, é assimetria de ajuste.** Se o baseline roda perto dos
hiperparâmetros default enquanto o nosso método carrega meses de adaptação, a comparação favorece o
nosso lado por construção. **É por aqui que uma revisão ataca primeiro**, muito antes de perguntar
sobre conjunto reservado.

⚠ **A ressalva do autor, e ela é legítima:** na prática pegamos a receita que os autores publicaram
para os melhores datasets *deles* e comparamos com a nossa melhor receita. Isso é melhor-contra-melhor,
não default-contra-tunado, e é defensável — mas é um ponto de crítica previsível, e a resposta tem de
estar escrita antes de ser perguntada. A formulação honesta: *"cada método roda na configuração que
seus autores publicaram como a melhor para aquele dataset"*, com a cobertura de busca declarada por
método.

#### Cenário 2 — contra as nossas abordagens anteriores

**O mais sensível dos quatro, e o único que exige conjunto reservado.**

O motivo: uma melhoria nossa envolve meses de ajuste, enquanto o número do antecessor está congelado
como foi publicado. O ganho do ajuste entra **inteiro** dentro do delta. O protocolo garante simetria
de seleção *dentro* de um artigo; **entre artigos ela é violada por construção**.

**A peça que resolve, e que não é óbvia: rode o sistema ANTIGO também no conjunto reservado.** Não
basta separar o conjunto — os dois sistemas têm de rodar lá, sob o mesmo contrato. Aí pareamento e
frescor **compõem**: a comparação é simultaneamente pareada e não-tunada, que é a célula mais forte
que este desenho consegue produzir. Custa um braço a mais.

Isto desfaz a dicotomia aparente entre "mesmo dado para comparar" e "dado novo para validar": a
comparação exige o **método** antigo, não o **dado** antigo, e o método antigo é código nosso, que
roda de novo.

#### Cenário 3 — dedicado contra joint

**Mais seguro que o 2, não igual.** Os dois braços são nossos e rodam sob protocolo idêntico no mesmo
artigo — essa simetria é alcançável, ao contrário do cenário 2.

O resíduo: a receita foi escolhida, em parte, porque fazia o joint parecer não-inferior. Por isso a
alegação de **não-inferioridade** é a mais frágil a reuso de todas — ela afirma uma diferença
*limitada*, e o viés residual em estado pequeno tem o tamanho da margem (ver §7.7).

#### Cenário 4 — durante o desenvolvimento

**Validação interna, à vontade, sem gastar nada.** É para isso que ela existe.

#### Três cenários que faltavam nesta lista

**Ablações publicadas.** Diferentes do cenário 4 porque **saem no artigo**. Oito linhas de ablação são
oito comparações e a família precisa de correção de multiplicidade. Decida antes: ablação se mede em
validação interna (e é rotulada como leitura de desenvolvimento) ou no teste (e conta como leitura).

**Os números absolutos das tabelas.** Mesmo com todas as comparações sólidas, **o valor absoluto é a
quantidade mais frágil**: ele não viaja entre conjuntos — o desvio de distribuição o move aos pontos
percentuais quando se troca de conjunto de teste (§7.7) — e é o alvo natural da suspeita de reuso.
As comparações pareadas sobrevivem melhor que os absolutos.

**A reprodução do baseline falhar.** Já aconteceu aqui: as células do POI-RGNN impressas na tabela não
saem dos JSONs correspondentes. Precisa de regra **antes** de acontecer: reporta-se o publicado, o
nosso, ou os dois com a discrepância nomeada?

### 7.7 · O viés de reuso é um problema de estado PEQUENO

Contra-intuitivo e decisivo para o desenho. O viés de escolher a melhor de K variantes é
aproximadamente `erro-padrão pareado × √(2·ln K)`, e o erro-padrão pareado encolhe com o tamanho do
conjunto:

| tamanho | erro-padrão pareado | viés ao escolher a melhor de 20 |
|---|---:|---:|
| Texas (4,1 M check-ins) | 0,01–0,04 pp | **0,03–0,10 pp** |
| Alabama (114 k) | 0,13–0,15 pp | **0,32–0,37 pp** |

A margem de equivalência é 0,4 pp. **Gastar Alabama custa uma margem inteira; gastar o Texas custa
quase nada.**

Consequência prática: ter usado CA e TX ao longo dos artigos custou muito menos do que soa, e o
conjunto que mais precisaria de proteção — Alabama — é o que foi mais usado. Isso inverte a
intuição de que os "grandes" são os preciosos.

**O que a literatura empírica de reuso realmente mostra** — e ela deve ser citada pelo que diz,
não pelo que conviria. Recht, Roelofs, Schmidt & Shankar, "Do ImageNet Classifiers Generalize to
ImageNet?" (ICML 2019 — conferido via busca web em 21-08), construíram conjuntos de teste **novos**
para CIFAR-10 e ImageNet seguindo o processo de coleta original e reavaliaram dezenas de modelos:
as acurácias absolutas caíram ~3–15 pp **nos conjuntos novos**, e o achado central é que a queda
**não é atribuída a sobreajuste adaptativo por reuso do teste antigo, e sim ao desvio de
distribuição** entre o conjunto original e o recém-coletado — os ganhos no teste original traduzem-se
em ganhos iguais ou maiores no novo, o padrão **oposto** ao que o sobreajuste adaptativo produziria.
Roelofs et al., "A Meta-Analysis of Overfitting in Machine Learning" (NeurIPS 2019 — conferido via
busca web em 21-08), mediram mais de cem competições do Kaggle — leaderboard público consultado
milhares de vezes contra teste final usado uma vez — e acharam **pouca evidência de sobreajuste
adaptativo substancial**.

O que esses dois artigos sustentam aqui é, portanto, duas coisas — e **não** a frase "o reuso
destrói o número absoluto":

1. a **ordem** entre métodos é notavelmente estável mesmo sob troca de conjunto de teste — o que
   respalda apoiar as conclusões em comparações pareadas, como este desenho faz;
2. o dano do reuso adaptativo, medido em larga escala, foi **menor do que o pior caso teórico** — o
   que calibra o medo, mas não licencia reusar à vontade: os regimes medidos (testes i.i.d. com
   dezenas de milhares de exemplos) não são o nosso estado pequeno com usuários agrupados, onde a
   aritmética da tabela acima continua valendo.

O número absoluto continua sendo a quantidade mais frágil — mas o mecanismo demonstrado nesses
estudos é o desvio de distribuição ao trocar de conjunto, não uma corrosão por reuso.

### 7.8 · O que acumula entre ciclos — e o que este protocolo NÃO corrige

A regra "uma leitura por braço por ciclo" tem um custo que as seções anteriores não nomeiam: **os
ciclos se acumulam sobre o mesmo conjunto.** Um braço genuinamente novo no ciclo v22 é, de fato, um
par (receita, conjunto) nunca lido (§7.10) — mas o estado já foi lido em ciclos anteriores, e quem
decidiu o que entra no v22 viu aqueles números. A correção de multiplicidade do protocolo (Holm na
família manchete, dentro do ciclo; §5 do protocolo) **não cobre isso**: não existe correção formal
entre ciclos, e fingir que Holm a fornece seria falso.

O que existe, e o que se pode dizer:

1. **O viés acumulado tem a magnitude do §7.7**, com K = o número TOTAL de braços já lidos naquele
   conjunto, somado sobre todos os ciclos — não o K do ciclo corrente. A expressão
   ≈ erro-padrão·√(2·ln K) cresce devagar (dobrar K move pouco), mas cresce; num estado pequeno
   cada ciclo consome uma fração visível da margem de 0,4 pp.
2. **O livro de leituras (§7.10) torna K público e contável.** Qualquer alegação sobre um conjunto
   deve poder citar quantas leituras aquele conjunto já sofreu — o número sai do ledger e do git,
   não da memória de quem rodou.
3. **A degradação é declarada, não escondida** (§7.5): "fechado para o ciclo v21" vale para o v21;
   a cada ciclo o rótulo enfraquece, até o ponto em que a resposta honesta é mudar a alegação — ou
   pagar uma primeira leitura num conjunto do pool intocado (§7.5), que é o único reset real.

A frase defensável na banca: *"entre ciclos não há correção estatística — há um registro público de
quantas vezes cada conjunto foi lido, um limite de viés da ordem de SE·√(2·ln K) sobre esse total, e
a política declarada de aposentar o rótulo confirmatório de um conjunto conforme K cresce."*

### 7.9 · Receita de bolso

```
1. Rode N variações        → só validação interna, Tier B    [teste: intacto]
2. Ordene, escolha 3-5     → só validação interna            [teste: intacto]
3. CONGELE a lista curta   → nada muda daqui em diante
4. mtlcheck compare        → UMA leitura, todos os braços     [gasta 1 ciclo]
5. Precisa mexer de novo?  → volte ao passo 1; o próximo ciclo
                             paga com outro conjunto (§7.5)
```

E a regra que protege tudo isto no código, não na disciplina: o **Estágio 1 nunca calcula um número
de teste externo**, nem para monitorar. A wave grava linhas e nenhuma métrica externa, então não
existe o que olhar cedo. Quem quer o número chama o Estágio 2 — um ato deliberado, datado, que fica
no log.

### 7.10 · `--confirmatory` — como obter o número final, e quando ele é recusado

#### O problema que ele resolve

Rodar um modelo imprime a **validação interna** — o número que escolhe a época e que o §8 diz para
nunca citar. Quem chega ao sistema recebe, por padrão, algo com cara de resultado que não é.

A saída não foi abrir a leitura do teste para todo mundo. Foi notar que **duas situações diferentes**
estavam sendo tratadas como uma:

| | o que é | custa? |
|---|---|---|
| **primeira leitura** de um par (receita, conjunto) | o ato racionado | **sim** — gasta o conjunto para aquela receita |
| **reprodução** de um par já lido e publicado | re-derivar um fato público | **não** |

#### Como usar

```bash
# desenvolvimento — o default. Sai a validação interna, não gasta nada.
mtlcheck train --recipe recipes/v19/joint.toml --state alabama --seed 0 --split-seed 0

# o número final, quando o par já foi lido
mtlcheck train --recipe recipes/v19/joint.toml --state alabama --seed 0 --split-seed 0 --confirmatory
```

Se o par **nunca** foi lido, a segunda forma **recusa** — e recusa **antes de treinar**, porque
recusar depois de horas de GPU é a mesma informação pelo pior preço. A mensagem diz o que fazer.

#### Como um par entra no livro

O caminho normal, e único daqui em diante: **um `mtlcheck compare` confirmatório que de fato
aconteceu.** O `compare` registra a leitura em `studies/READ_LEDGER.json` no momento em que ela
ocorre. Pré-registrar pares como lidos para poupar trabalho declararia gasto o que não foi, e
liberaria a leitura de conjuntos que ninguém leu — por isso o livro não aceita entradas
especulativas.

#### O backfill — a leitura que aconteceu antes de o livro existir

O livro nasceu em 2026-08-21; a primeira leitura selada aconteceu em **2026-08-18** (AL/AZ/IST,
[`SEALED_BRIDGE_READ.md`](../studies/porting_validation/SEALED_BRIDGE_READ.md)). Sem tratamento,
as regras acima recusariam uma reprodução `--confirmatory` desses pares como "nunca lidos" — o que
é falso, e transformaria o livro num registro que contradiz o fato que ele existe para registrar.

A regra de backfill, e ela é estreita: um par só pode ser semeado no livro quando a leitura tem
**registro datado e commitado independente do livro** — para AL/AZ/IST, o registro é
`SEALED_BRIDGE_READ.md` + `evidence/sealed_bridge_tier_a.json`, no commit de 18-08. A entrada
backfilled aponta para esse registro em vez de para um `compare`. Nada além disso entra por
backfill: um par sem registro datado é, por definição, nunca-lido, e semeá-lo "para poupar
trabalho" é exatamente o vazamento que o livro impede.

#### O par é (RECEITA, conjunto) — não só o conjunto

A trava é por versão, e é a peça que impede o vazamento óbvio:

> Uma receita **v21** apontada para um estado lido na **v19** é **primeira leitura**, não reprodução.
> O número daquele par nunca existiu.

A identidade é o `science_fingerprint` da receita, então telemetria não cria par novo (ligar a sonda
de gradiente não é uma receita diferente), mas trocar substrato, cabeça, taxa de aprendizado ou
família **cria** — que é exatamente o comportamento desejado.

#### O que ele NÃO entrega

**Um número, não um veredito.** O que sai é o escore OOF agrupado do braço no fold externo. O Δ com
intervalo de confiança, o NI/TOST e o gatekeeping continuam saindo do `compare`, porque a unidade
confirmatória é a **família inteira de um ciclo**, com correção de multiplicidade — não um braço
isolado.

#### O limite honesto

`studies/READ_LEDGER.json` é editável, e o `git` é a única loja à prova de adulteração deste projeto.
Por isso ele é versionado: **uma leitura aparece como um commit datado.** A garantia é
auditabilidade, não impossibilidade.

### 7.11 · O que ler depois

- [`plans/EVALUATION_PROTOCOL.md`](plans/EVALUATION_PROTOCOL.md) §5 (triagem/confirmação) e §9
  (limites; o item 4 sobre pesos confirmatórios foi emendado pelo §12.3 — ver §7.5) — a fonte
  formal.
- [`NOMENCLATURE.md`](NOMENCLATURE.md) — repetição vs. réplica, e por que `seed` virou dois botões.
- [`DIVERGENCE_REGISTER.md`](DIVERGENCE_REGISTER.md) — as três categorias de divergência e a
  hierarquia das cifras de otimismo (§0.1).
- [`QUAL_CONJUNTO_USAR.md`](QUAL_CONJUNTO_USAR.md) — o quadro de bolso de qual conjunto usar.
- §3 deste guia — Tier A vs. Tier B, que é o "qual instrumento em qual etapa".

---

## 8 · Números deste protocolo NÃO se comparam com números do v18

O erro mais fácil de cometer com esta base, e o mais caro, porque produz uma conclusão plausível e
inteiramente falsa.

### As duas perguntas usam protocolos diferentes de propósito

| | **paridade de porte** | **ciência** |
|---|---|---|
| pergunta | o código calcula a mesma coisa? | qual é a resposta? |
| protocolo | o do v18 — 5-fold plano | o novo — aninhado e selado |
| treino | 80 % | 70 % |
| validação | os 20 % de fora | os 10 % internos |
| escolhe a época em | **o mesmo conjunto que reporta** (regra legada) | o conjunto interno |
| onde | `waves/ref_parity_al.toml` | `waves/sealed_bridge.toml` |

A wave de paridade reproduz a regra legada **incluindo o otimismo dela**. Isso é deliberado: paridade
de porte exige reproduzir o que a referência faz, não o que ela deveria fazer. Nenhum número dessa
wave entra em estimando algum.

### Três números, não dois — e só um é resultado

Alabama, região, dedicado. Mesmo código, mesmo substrato, mesma semente de partição:

| leitura | protocolo | Acc@10 | é resultado? |
|---|---|---:|---|
| plano, seleciona e reporta no mesmo conjunto | v18 | 70,05 | é o que o v18 reportava |
| aninhado, **validação interna** | novo | 73,72 | **não** — serve para escolher a época |
| aninhado, **teste externo lido uma vez** | novo | **69,01** | **sim** |

A linha do meio é a que mais engana, porque tem a cara de um resultado e é a que sai no
`result.json` de uma célula `inner_validation`. Ela é otimista por construção: é o máximo sobre 50
épocas num conjunto de ~110 usuários (10 % dos 1.101 de Alabama sob o v18 — §4), metade do externo.
Nunca a cite.

O protocolo aninhado é o correto — é ele que separa quem escolhe a época de quem reporta o número
(§2). O que ele custa em Alabama é visível: 69,01 contra os 70,05 que a regra legada reportava, ou
seja, **a regra legada era otimista em ~1 pp** — e essa é a cifra do meio da hierarquia do §0.1.

⚠ **Esse ~1 pp não é uma medida limpa de otimismo de seleção.** Os dois lados diferem em duas
coisas ao mesmo tempo: o protocolo *e* a convenção de agregação — 70,05 é média-de-fold com uma
semente, 69,01 é OOF agrupado sobre quatro réplicas, e o §1 deste guia mostra que essas duas
convenções já não coincidem entre si. Trate ~1 pp como ordem de grandeza.

⚠ **E a cifra de cima da hierarquia — os ≈3,7 pp entre a linha do meio e a de cima — também não é
"só o protocolo muda".** Na precisão da tabela, 73,72 − 70,05 = **3,67** (o `DIVERGENCE_REGISTER.md`
cita 3,66, dos valores não arredondados). É a mais limpa das três cifras — mesmo código, mesmo
substrato, mesma partição — mas entre as duas linhas mudam **também** a população de avaliação (a
val interna de 10 % contra o fold legado de 20 %), a fração de treino (70 % contra 80 %) e o número
de réplicas (quatro contra uma). É a mais limpa, não limpa. A separação verdadeiramente limpa é a
do §8a do protocolo (`src/mtlcheck/eval/optimism.py`): estimadores co-registrados na MESMA
trajetória, que cancelam fold e semente exatamente — e esse instrumento **nunca rodou** (exige
`retain_checkpoints != "none"`; primeiro item de `studies/improvements/PLAN.md`). Até lá, nenhuma
das cifras desta seção pode ser citada como "o otimismo de seleção medido" — e de qualquer forma
qualquer uma delas é ≥ 2× a margem δ = 0,4 pp: ler uma tabela contra a outra não produz erro de
arredondamento, produz conclusão invertida.

### A regra prática

> Um Δ só é interpretável entre duas células que compartilham `eval_stream`. O campo está no
> `result.json` de toda célula: `outer_fold` é o protocolo plano, `inner_val` é o aninhado. Se os
> dois lados não baterem, não subtraia.

---

## 9 · Partição × semente de modelo — os dois sorteios, e o eixo que se mede

> Escrito 2026-08-24, junto com a emenda §12.6 do protocolo, que registra formalmente a medição.
> Esta é a versão didática: o que cada botão sorteia, por que um deles é congelado, como o eixo de
> partição se mede e se lê, e o que um ciclo novo (v20) tem de refazer. A medição em si está em
> [`../studies/v19_defence/S10_4_PARTITION_AXIS.md`](../studies/v19_defence/S10_4_PARTITION_AXIS.md).

### 9.1 · O que cada botão sorteia — e por que a partição é congelada

Todo treino recebe dois inteiros, e eles movem coisas diferentes:

| botão | o que sorteia | trocá-lo muda… |
|---|---|---|
| `--split-seed` (a **partição**) | a divisão dos usuários nos 5 folds — quem treina junto, quem escolhe a época de quem | **quem treinou o modelo** que pontua cada usuário |
| `--seed` (a **semente de modelo**) | inicialização dos pesos e ordem dos batches | o ponto de partida da otimização, nos mesmos dados |

("Partição" é o termo congelado em [`NOMENCLATURE.md`](NOMENCLATURE.md) §2, e é o que a prosa e as
tabelas usam daqui em diante. O campo de configuração, a coluna do parquet e o `cell_id` continuam
`split_seed` **de propósito**: renomeá-los rotacionaria o `science_fingerprint` das receitas, o que
transformaria as 54 células seladas em par nunca-lido e forçaria retreinar a suíte — uma segunda
leitura de um teste selado, comprada por uma palavra. Emenda §12.6e.)

**Por que a partição é congelada.** Sob o desenho user-disjoint com OOF agrupado (§0, §1), **todo
usuário do estado é avaliado exatamente uma vez, sob qualquer partição** — cada um é outer-test em
exatamente um fold, seja qual for o sorteio. Re-sortear a partição não muda *quem é avaliado*; muda
**quem treinou junto** — qual modelo pontua cada usuário held-out. A partição, portanto, não é um
eixo de amostragem do teste (esse eixo é o bootstrap de usuário do §3, que funciona sob qualquer
partição congelada); é ruído do lado do **treino**, da mesma família da dispersão entre réplicas e
do piso de reinstanciação de 0,18 pp (§5).

**E por que isso NÃO zera o efeito.** "Todo usuário é avaliado uma vez" garante que a população de
avaliação é a mesma; não garante que o número seja o mesmo. O escore de cada usuário depende do
modelo que o pontuou, e o modelo depende de quem caiu no treino dele. Duas partições produzem
modelos diferentes pontuando os mesmos usuários — e a diferença sistemática disso, no delta pareado
joint − dedicado, é o **eixo de partição**. Medido em região no Alabama: +0,37 pp. Não é zero, e
nada no desenho obrigava que fosse.

### 9.2 · Como o eixo se mede — e como se lê

**Um manifesto de wave declara o eixo direto:**

```toml
[[cell]]
recipe = "recipes/v19/joint.toml"
states = ["alabama"]
seeds = [0, 7]
partitions = [0, 7]      # produto cartesiano com `seeds`: quatro células, o 2×2 do §10.4
```

As outras duas formas são `split_seed = 0` (RÉPLICAS sobre partição fixa) e `split_seed = "per-seed"`
(REPETIÇÕES). **Exatamente uma tem de estar presente** — omitir era o desenho confundido por omissão.
O campo continua grafado `split_seed` pelo motivo do §12.6e do protocolo: o nome entra no
`science_fingerprint`, e renomeá-lo invalidaria as 54 células seladas.

**A regra, que é o que este guia deve carregar:**

1. o eixo é ruído do lado do **treino** — ele vai **ao lado** do intervalo, nunca dentro dele
   (§9.1, §10.2 do protocolo), e a frase de condicionalidade nomeia a partição congelada;
2. o limiar de 0,15 pp é **conferência de segurança**, não reivindicação: disparar no
   não-resolvido é o lado conservador;
3. cada ciclo **remede** o eixo na sua própria arquitetura — herdar a medição da v19 é o defeito
   que o §0.2 cataloga (ver §9.3).

**A medição da v19 — os quatro conjuntos, os dois eixos, os erros-padrão e a conta de "e se o eixo
entrasse no intervalo" — vive em
[`../studies/v19_defence/S10_4_PARTITION_AXIS.md`](../studies/v19_defence/S10_4_PARTITION_AXIS.md).**
Ela é datada e pertence ao estudo. Não a copie para cá: uma faixa que circulou entre cópias já não
reproduziu uma vez, e só não virou texto porque um revisor pegou (commit `d78a5c36`).

### 9.3 · O que um ciclo novo refaz — e o que ele NÃO herda

A **regra** é permanente; a **medição** é datada e pertence à v19 (§12.6a do protocolo). Os números
da tabela acima são propriedade do aprendiz que os produziu: estabilidade de validação cruzada
condiciona na estabilidade do aprendiz, e o aprendiz é exatamente o que um ciclo novo troca. Um v20
com outra arquitetura ou outro substrato pode ter outra estabilidade e mover — em qualquer direção
— o ponto onde o efeito some.

O ciclo novo, portanto:

1. **refaz o fatorial 2×2** no(s) conjunto(s) pequeno(s), antes da leitura confirmatória dele —
   custo medido na v19: 6 células novas, 30 fits, **~20 min de GPU** num conjunto pequeno;
2. **certifica o congelamento por conjunto × tarefa** contra o limiar, com o ep ao lado do eixo;
3. **reporta o eixo ao lado dos intervalos** onde a certificação falhar ou não existir — e rotula
   como extrapolação os conjuntos que não mediu.

**Herdar a medição da v19 é erro.** Não é atalho conservador nem "aproximação razoável": é citar a
estabilidade de um aprendiz que não é o que rodou — a mesma forma do defeito que o §0.2 cataloga
(todos os números coerentes, vindos de uma configuração que não é a que rodou). Se os ~20 min não
couberem no ciclo, a frase honesta é "eixo não medido nesta arquitetura", nunca o número da v19.

---

### 9.4 · Quantas réplicas, e quem decide isso — o *internal pilot*

Uma célula é treinada mais de uma vez, mudando só a moeda interna. **Quantas vezes?** A resposta
honesta é que a literatura **não tem um número** — e saber disso evita duas armadilhas.

**Não existe constante publicada para réplicas sobre partição fixa.** Colas, Sigaud & Oudeyer (2018)
respondem literalmente a pergunta "quantas sementes?" e a resposta é *faça análise de poder*: N sai
de (desvio medido, efeito de interesse, α, β), nunca de convenção. O `10×10` de Bouckaert & Frank
(2004) é sobre **repetições** — partições novas —, então citá-lo para justificar réplicas seria citar
fora do alvo. E Agarwal et al. (2021) medem que um intervalo por tarefa individual pede **20–30**
execuções: quatro compram um diagnóstico grosseiro, não um auditor.

**O que 2 → 4 compra são duas coisas diferentes, e confundi-las é a armadilha:**

| | 2 → 4 ganha | importa? |
|---|---|---|
| precisão da **média** (o Δ) | erro-padrão encolhe √2, ≈29 % | pouco — ambos ficam muito abaixo de δ |
| **estimar a dispersão** | 1 g.l. → 3 g.l. · multiplicador t de **12,7 → 3,2** | é o argumento real |

Com uma réplica a mais que o mínimo você não sabe nem a **ordem de grandeza** da banda. É por isso
que `stats.py` recusa imprimir sua faixa de 2·SE abaixo de três réplicas.

**Quem decide, então.** Não um número fixo: uma **regra**, e a regra tem forma válida na literatura.
Desenhos adaptativos separam duas adaptações, e a separação é a que este projeto precisa:

* adaptar sobre o **efeito observado** exige maquinário sequencial completo (fronteiras
  pré-especificadas, gasto de α). Rodar duas réplicas, olhar o delta e escalar se discordarem cai
  aqui — a regra de parada vira parte do estimador;
* adaptar sobre a **variância** — um parâmetro de perturbação — é o ***internal pilot***
  (Kieser & Friede 2000), e o FDA (2019) registra que ele tem inflação de tipo I negligenciável e
  **não exige gasto de α**.

**A restrição deste projeto resolve a favor do segundo:** olhar o teste externo o **gasta**; olhar a
dispersão na **validação interna** não gasta nada. Então a escalada por dispersão interna,
pré-registrada, é válida — e é a recomendação para o próximo ciclo
([`../docs/future_works/banda_da_ponte_transfere.md`](future_works/banda_da_ponte_transfere.md)).

⚠ **O v19 não usa isso**, e não pode passar a usar: a regra dele é a ponte, o gate reprovou em
24-08, e trocar a regra depois de ver a reprovação é o pós-hoc que o protocolo §12.7 cataloga. O que
está registrado para esta campanha é o diagnóstico do §12.9, que reporta sem decidir.

---

## 10 · "Vale em seis conjuntos" — o que essa frase pode dizer, e o que ela custa

Esta é a frase que o título da dissertação faz, e é a única do protocolo inteiro que fala de mais de
um conjunto ao mesmo tempo. Ela tem uma seção própria porque é a mais fácil de dizer errado, e o erro
é atraente: seis leituras verdes parecem seis confirmações independentes, e não são.

### 10.0 · Por que isto não é "contar na mão"

A objeção natural: o `compare` já dá o veredito de cada conjunto — por que existe uma camada para
contar quantos passaram?

**Porque contar engana.** Se o efeito for zero em toda parte, cada conjunto ainda tem 5 % de chance
de sair "positivo" por azar; com seis, a chance de **pelo menos um** sair é `1 − 0,95⁶ ≈ 26 %`.
Anunciar "funcionou em um dos seis" é uma frase que o acaso produz um quarto das vezes com um método
inútil. A conjunção parcial faz a conta que desconta isso: **`u*` é um teste, não uma contagem**, e
o `compare`, que enxerga um conjunto por vez, estruturalmente não pode fazê-la.

Daí o par de números lado a lado — `marginal` é a contagem na mão, `u*` é o que sobra depois do
desconto. **Quando batem, a intuição estava certa; quando `u*` é menor, a diferença era sorte.**

### 10.1 · Ela não é a média, e não é "todos passaram"

Três frases diferentes, com preços diferentes:

| a frase | o que ela pede | quando ela quebra |
|---|---|---|
| "em média, o efeito existe" | *pooling* entre conjuntos | um conjunto destoante contamina a média e ninguém vê |
| "vale nos seis" | interseção-união: os seis vereditos individuais | um conjunto ruim zera a afirmação inteira |
| **"vale em pelo menos u dos seis"** | **conjunção parcial (§4a)** | não quebra — ela devolve o `u` que o dado sustenta |

A terceira é a que o protocolo registra, e a razão é concreta: **já aconteceu** neste projeto de um
braço ganhar na Flórida e desabar no Alabama. Com a segunda frase, aquele resultado teria sido "não
replicou" — apagando cinco conjuntos por causa de um. Com a terceira, ele é "replicou em cinco", que
é o que o dado diz.

O `u*` é o maior `u` que o teste sustenta. Ele sai ao lado de uma coluna **marginal**: quantos
conjuntos sustentam o veredito olhando um a um. A folga entre as duas é o preço de afirmar as coisas
juntas — nunca o contrário, porque `u*` não compra conjunto nenhum de graça.

### 10.2 · Por que Bonferroni, e por que isso não foi escolha nossa

A conjunção parcial combina os p dos conjuntos, e há duas maneiras. **Simes** é a apertada, e exige
que os conjuntos sejam independentes (ou PRDS). **Bonferroni** vale sob dependência arbitrária e
custa poder — sustenta um `u*` menor com o mesmo dado.

O §4a do protocolo pré-registrou qual usar como uma **precondição verificável**, não como
preferência: intersectar os IDs de usuário entre os corpora, e trocar para Bonferroni se a
sobreposição for não-trivial. A precondição nunca tinha rodado. Rodou em 2026-08-23, e **falhou por
muito**:

- entre 37 % e 80 % dos usuários de cada estado americano aparecem em pelo menos um outro;
- dos 80 875 indivíduos distintos nos cinco estados, **24,5 % aparecem em mais de um**;
- e contar usuários **subestima** a dependência: viajantes são mais ativos que a média — no Texas são
  37 % dos usuários e **51 % dos check-ins**.

Testado contra a hipótese de artefato de ETL, e a hipótese foi descartada: as fatias não compartilham
lugar nenhum (o corte é por geografia do lugar), há exatamente 5 check-ins `(usuário, instante)`
duplicados em ~9 milhões de linhas, e o caso examinado de perto — 182 check-ins na Flórida numa
semana, depois um único no Alabama no último dia dela — é inequivocamente uma pessoa viajando para
casa. Usuários do Gowalla viajam, como a própria frase do §4a previa.

**Istanbul é limpa por construção, e a auditoria confirmou a construção e não a contagem ingênua.**
Uma interseção crua acusa 1 952 usuários "compartilhados" entre Istanbul e Califórnia. É **colisão de
inteiros** entre dois espaços de identificador independentes (Massive-STEPS contra SNAP Gowalla), não
gente. Uma auditoria que "acha" sobreposição em Istanbul está medindo colisão de id.

### 10.3 · A consequência que vai no texto, e não só no código

Bonferroni entra — é o ramo barato que o próprio §4a pré-registrou, custa zero GPU e se paga em
poder. Mas a consequência maior é de redação:

> **"Replicado em seis conjuntos" não é seis observações independentes.** Os cinco estados americanos
> são fatias geográficas de **uma** população do Gowalla, e nos dois conjuntos pequenos — que são
> justamente os estados-ponte — mais de 70 % dos usuários também aparecem nos grandes. **Istanbul é o
> único conjunto genuinamente independente.**

Isso não invalida leitura nenhuma por conjunto: cada uma é condicional aos usuários daquele conjunto,
e o bootstrap do §3 reamostra dentro dele. Mas limita o que a frase cross-state pode dizer, e o texto
tem de dizer isso antes que um membro da banca pergunte.

### 10.4 · Como se roda

A camada é pós-processamento sobre as leituras que já aconteceram — ela **não abre parquet nenhum**:

```bash
mtlcheck conjunction al.json az.json ist.json fl.json ca.json tx.json \
    --analysis recipes/analysis/v19_headline.toml
```

Os arquivos são as saídas de `mtlcheck compare --json`, um por conjunto. Como nada de teste selado é
tocado, **ela pode rodar de novo quantas vezes o texto precisar** — reescrever uma frase não custa
leitura.

Ela recusa três coisas, e as três são maneiras de a frase deixar de significar o que parece:

- **conjuntos lidos por receitas diferentes** — cada p foi computado contra a margem e os níveis da
  *sua* receita, então combiná-los daria um `u*` sem um "u de quê";
- **o mesmo conjunto duas vezes** — cada conjunto é UMA observação, e repetir um infla `u*`;
- **um conjunto lido em modo exploratório** — a frase é confirmatória e não se monta sobre ele.

O p que entra é o **bruto**, não o corrigido por Holm: o §5 põe Holm *dentro* do conjunto, sobre a
família de duas tarefas daquele conjunto. Combinar o ajustado corrigiria duas vezes pelo mesmo
motivo.

### 10.5 · Uma armadilha aritmética que quase entrou

A combinação, como escrita nos artigos, **não é monótona em `u`**. O multiplicador `n − u + 1`
encolhe enquanto a estatística de ordem `p_(u)` cresce, e o produto pode cair. Com
`p = [0,001 0,002 0,003 0,004 0,60 0,70]` a versão crua dá **1,20 em u=5 e 0,70 em u=6** — o que
licenciaria "vale em pelo menos 6" com "vale em pelo menos 5" rejeitado. Não é uma afirmação que
alguém possa fazer.

O conserto é o máximo corrente, que só aumenta `p` e portanto continua válido. Está no código e tem
teste. Fica registrado aqui porque quem reimplementar a partir do artigo vai reencontrar o mesmo
buraco.

---

## Ledger de fontes — o que foi conferido, quando, e como

Regra deste ledger: uma linha só diz "conferido" quando uma checagem mecânica aconteceu numa sessão
datada, e a linha diz **qual** checagem. Uma verificação declarada sem método é o mesmo defeito do
§0.2 — alegação acima da evidência — e este ledger já o cometeu; a regra existe por isso.

Duas sessões de verificação: **Crossref** (consultas a `api.crossref.org/works`, 2026-08-20) e
**busca web** (páginas de editora/arXiv/JMLR/dblp, 2026-08-21).

| Referência | Identificador | Verificação | O que sustenta neste guia |
|---|---|---|---|
| Forman & Scholz, "Apples-to-apples in cross-validation studies", *SIGKDD Explorations*, 2010 | DOI 10.1145/1882471.1882479 | Crossref 20-08 — título/autor/DOI confirmados | §1 — agregar antes de dividir |
| Tsamardinos, Greasidou & Borboudakis, "Bootstrapping the out-of-sample predictions…", *Machine Learning*, 2018 | DOI 10.1007/s10994-018-5714-4 | Crossref 20-08 — confirmado | §1, §3 — princípio de pooling OOF |
| Field & Welsh, "Bootstrapping Clustered Data", *JRSS-B*, 2007 | DOI 10.1111/j.1467-9868.2007.00593.x | Crossref 20-08 — confirmado | §3 — bootstrap em cluster de usuário |
| Chung & Romano, "Exact and asymptotically robust permutation tests", *Annals of Statistics*, 2013 | DOI 10.1214/13-aos1090 | Crossref 20-08 — confirmado | §3, §6 — permutação estudentizada |
| Schuirmann, "A comparison of the Two One-Sided Tests Procedure…", *J Pharmacokinet Biopharm*, 1987 | DOI 10.1007/bf01068419 | Crossref 20-08 — confirmado | §6 — origem do TOST |
| Opitz & Burst, "Macro F1 and Macro F1", 2019 | arXiv:1911.03347 | busca web 21-08 — página do arXiv confirma título/autores; conteúdo citado (duas definições não-equivalentes; diferença até 0,5) confere | §1 — dualidade de definições de macro-F1 |
| Cawley & Talbot, "On Over-fitting in Model Selection and Subsequent Selection Bias…", *JMLR*, 2010 | JMLR 11(70):2079–2107 | busca web 21-08 — jmlr.org/papers/v11/cawley10a.html confirma volume/páginas | §2 — viés de seleção não contabilizado |
| Efron, "Better Bootstrap Confidence Intervals", *JASA*, 1987 | 82(397):171–185; DOI 10.1080/01621459.1987.10478410 | busca web 21-08 — tandfonline confirma volume/número/páginas/DOI | §3 — intervalo BCa |
| Bouthillier et al., "Accounting for Variance in Machine Learning Benchmarks", MLSys, 2021 | arXiv:2103.03098; dblp conf/mlsys/BouthillierDBTN21 | busca web 21-08 — dblp + proceedings.mlsys.org confirmam | §4, §5 — medir variância antes de decidir orçamento |
| Benavoli, Corani, Demšar & Zaffalon, "Time for a Change…", *JMLR*, 2017 | JMLR 18(77):1–36; arXiv:1606.04316 | busca web 21-08 — confirmado | §5 — exemplo de ROPE ~1 pp |
| Lakens, "Equivalence Tests: A Practical Primer…", *SPPS*, 2017 | 8(4):355–362; DOI 10.1177/1948550617697177 | busca web 21-08 — journals.sagepub.com confirma o DOI da versão publicada | §6 — TOST moderno + pré-registro da margem |
| Recht, Roelofs, Schmidt & Shankar, "Do ImageNet Classifiers Generalize to ImageNet?", ICML, 2019 | PMLR 97:5389–5400 | busca web 21-08 — dblp/ICML confirmam; conteúdo conferido: queda de ~3–15 pp em conjuntos NOVOS, atribuída a desvio de distribuição, não a sobreajuste adaptativo; ordem preservada | §7.7 — o que o reuso faz e não faz |
| Roelofs et al., "A Meta-Analysis of Overfitting in Machine Learning", NeurIPS, 2019 | papers.nips.cc paper 9117 | busca web 21-08 — proceedings confirmam; >100 competições Kaggle, pouca evidência de sobreajuste adaptativo | §7.7 |
| Wellek, *Testing Statistical Hypotheses of Equivalence and Noninferiority*, 2ª ed., 2010 | Chapman & Hall/CRC | busca web 21-08 — **existência confirmada; conteúdo NÃO consultado** — citado de segunda mão | §6 |
| EMA, CPMP/EWP/482/99 ("Points to Consider on Switching between Superiority and Non-inferiority"), 2000 | — | **não conferido mecanicamente** em nenhuma sessão; citado a partir do protocolo | §6 — troca NI → superioridade sem correção |
| Holm, "A simple sequentially rejective multiple test procedure", *Scand J Statist*, 1979 | citado como 6(2):65–70 | **não conferido mecanicamente** (a consulta Crossref de 20-08 retornou registros errados); citado a partir do protocolo | §7.3 — correção da família manchete |

**Não conferidas por nenhum método, em nenhuma sessão** (todas citadas apenas no protocolo
completo, nenhuma desenvolvida neste guia): Nadeau & Bengio (2003), Dietterich (1998), Benjamini &
Heller (2008), Dror et al. (2017), Riley et al. (2010), Veroniki et al. (2016), Röver, Knapp &
Friede (2015), Higgins, Thompson & Spiegelhalter (2009), IntHout et al. (2016), Demšar (2006),
Friede et al. (2017), Kruschke (2018), Higgins & Thompson (2004), Benjamini & Hochberg (1995),
Bengio & Grandvalet (2004), Bates, Hastie & Tibshirani (2023), Corani & Benavoli (2015), Romano &
Wolf (2005), Card et al. (2020), Varma & Simon (2006). Consultas Crossref de 20-08 para várias
delas retornaram registros que **não** correspondem à obra citada — nenhuma deve ser tratada como
verificada até checagem individual.

**Fatos internos citados neste guia (não são citações de literatura — são medições deste
projeto):** o viés de −0,24 pp de média-de-fold em Alabama; os pisos de ruído (1,2 pp entre folds;
0,05–0,15 pp entre repetições; 0,02–0,05 pp entre execuções idênticas; 0,18 pp numa reinstanciação
ponta-a-ponta, medida uma vez; 0,034 pp entre quatro sorteios de substrato); o efeito de
+0,354 ± 0,095 pp de duração de schedule em Alabama; as contagens de usuários (AL 1.101 sob o
substrato v18 — a cifra 3.858 é da janelagem v17 e está superada; TX 38.644 é contagem v17, ainda
não re-medida sob o v18); e as meia-larguras realizadas do bootstrap (0,101–0,222 pp na leitura
selada). Vêm de `docs/plans/EVALUATION_PROTOCOL.md`, `docs/NOMENCLATURE.md`,
`studies/porting_validation/GATES_2026-08-17.md`, `studies/porting_validation/SEALED_BRIDGE_READ.md`
e `studies/porting_validation/SUBSTRATE_FROM_SCRATCH.md`, e devem ser tratados como tal: números
específicos deste repositório, não constantes da literatura.

---

## Nota sobre a pergunta de arquitetura (dois scripts)

A separação proposta — um estágio de execução (treino → predições linha-a-linha
persistidas) e um segundo estágio, independente, de comparação (pooling, Tier A, Tier B, NI/TOST,
correções de multiplicidade) — é exatamente a estrutura que o próprio protocolo assume desde a
abertura, ao declarar que tudo nele é pós-processamento de artefatos que o design já exige (a
frase é do próprio `docs/plans/EVALUATION_PROTOCOL.md`, não de uma fonte externa). Dado o
"persistence contract" do §2 do protocolo (predições por (braço, seed, fold) com user ID, fold ID,
seed, época selecionada, rank por linha, e o conjunto de rótulos de treino por fold), faz sentido
que o Estágio 1 tenha como única responsabilidade científica gravar esse contrato — sem calcular
médias, deltas ou vereditos — e que o Estágio 2 seja o único lugar onde bootstrap de usuário,
permutação, TOST e correções de multiplicidade acontecem, lendo apenas os arquivos persistidos do
Estágio 1.

Isso tem uma consequência direta para `train/stats.py`: o módulo atual opera sobre **métricas já
agregadas por célula** (`Cell(seed, fold, value)`), o que é suficiente para o Tier B, mas não para
o Tier A — o bootstrap de usuário exige as predições linha-a-linha, não o valor de métrica já
resumido por fold. **Decidido em 2026-08-18** (registro em
[`plans/EVALUATION_IMPLEMENTATION.md`](plans/EVALUATION_IMPLEMENTATION.md)): módulo novo (`eval/`) ao
lado, com `train/stats.py` intacto como motor do Tier B. Tier A e Tier B são estimandos com `n`
diferentes, e uma função que aceitasse linha-a-linha *ou* célula reabriria justamente a confusão de
unidade inferencial que o `NOMENCLATURE.md` existe para fechar. O acoplamento obrigatório é uma
definição única de métrica (`eval/estimands.py`), usada por quem quer que calcule um número.

A mesma decisão acrescentou uma emenda à separação em dois estágios: **o Estágio 1 não calcula
métrica de outer-test, nem para monitorar.** Um número impresso durante a wave é um número que o
operador vê, e o critério 7 da auditoria converte em exploratória qualquer execução alterada depois
de olhar o outer-test. Gravando linhas e nenhum número, o selo deixa de depender de disciplina e vira
propriedade do fluxo de dados.
