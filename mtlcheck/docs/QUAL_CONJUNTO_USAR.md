# Qual conjunto eu uso? — as duas perguntas e os dois instrumentos

> Documento curto e deliberadamente simples. Se você só quer a resposta, leia o quadro do §1 e pare.

---

## 1 · O quadro

Existem **duas** perguntas neste projeto, e elas têm instrumentos diferentes.

| | **Pergunta de desenvolvimento** | **Pergunta final** |
|---|---|---|
| o que você quer saber | "essa mudança que eu fiz melhorou, piorou ou não mexeu?" | "o modelo conjunto empata ou ganha do dedicado?" |
| quando | agora, o tempo todo, a cada iteração | uma vez, com tudo fechado |
| conjunto | **validação interna** (10 %) | **teste externo** (20 %) |
| quantas vezes pode olhar | **infinitas** | **uma**, por braço, por ciclo |
| custo | zero | gasta a reserva |
| comando | `mtlcheck score` | `mtlcheck compare` |
| escala típica | 1 estado, 1 semente, 5 folds | 6 estados × 3 famílias × 4 réplicas × 5 folds |

**A regra em uma frase:** enquanto você estiver mexendo na implementação, use a validação interna.
Quando parar de mexer, use o teste — uma vez.

---

## 2 · Por que a validação interna basta para a pergunta de desenvolvimento

Porque ela é o **mesmo tipo de dado** que o teste: usuários que o modelo nunca viu treinando.

```
┌────────────── 70 % ──────────────┬─── 10 % ───┬────── 20 % ──────┐
│            TREINO                │  VAL       │      TESTE       │
│                                  │  INTERNA   │                  │
│  o modelo aprende                │  ← olhe    │  ← olhe UMA vez  │
│                                  │  à vontade │                  │
└──────────────────────────────────┴────────────┴──────────────────┘
                    disjuntos por USUÁRIO — ninguém aparece em dois
```

Os dois medem "acerta em gente nova". A diferença **não é qualidade** — é orçamento de olhadas.

E é por isso que o teste **não dá uma resposta melhor** para "minha mudança ajudou?". Dá a **mesma
resposta**, consumindo o instrumento que só serve uma vez.

### A prova, deste projeto, de 2026-08-19

A campanha que corrigiu o POI2Vec respondeu "essa mudança ajudou?" **doze vezes**, com atribuição
por divergência, e **não tocou no teste nenhuma vez**:

| medição | resultado | instrumento |
|---|---|---|
| piso de ruído entre sorteios de substrato | 0,034 pp | val interna |
| divergência 3, ponderação do objetivo | +0,012 pp → é ruído | val interna |
| divergência 1, negativos duros | +0,563 pp | val interna |
| divergência 2, regularizador de hierarquia | +0,282 pp | val interna |
| o déficit era do construtor, não do sorteio | 4 sorteios, desvio 0,034 contra distância 0,78 | val interna |

Uma dessas conclusões separou um efeito de **0,012 pp** de ruído. Isso é resolução de sobra para
qualquer pergunta de desenvolvimento.

---

## 3 · O que se perde ao usar o teste para desenvolver

Nada de estatístico no número **daquela** execução — ele é uma estimativa honesta. O problema é o
que acontece **depois**.

Cada vez que você olha o teste e decide algo com base nele — qual variante seguir, quando parar de
iterar, qual estado destacar — a decisão passa a ser condicionada nele. No fim, o número que sobra é
o **máximo sobre todas as olhadas**, e ele parece melhor do que o modelo é.

O tamanho disso, medido **neste repositório**: o otimismo de seleção é **~0,66 pp**, e a margem de
equivalência da dissertação é **0,4 pp**. Ou seja, o viés é maior que o efeito que se quer testar.
Todo resultado-manchete deste estudo cabe dentro dessa faixa.

Há ainda um detalhe técnico: métrica de teste **por fold** é o estimando errado. O protocolo pede
OOF agrupado (as linhas de todos os folds concatenadas, pontuadas uma vez). A média-de-folds carrega
viés de **−0,24 pp**, mais da metade da margem. Então um número de teste por fold, além de caro,
já nasce não-citável.

---

## 4 · Na prática

### Enquanto você desenvolve

```bash
# rode a variante
mtlcheck wave run studies/<estudo>/waves/minha_ideia.toml

# compare contra a base — de graça, quantas vezes quiser
mtlcheck score runs/<estudo> --compare cat joint:cat --state alabama
```

**A única regra que faz a comparação valer:** os dois lados têm de compartilhar o `eval_stream`.
Está no `result.json` de toda célula. `inner_val` compara com `inner_val`; `outer_fold` com
`outer_fold`. Se não baterem, **não subtraia** — a diferença entre protocolos em Alabama/região é de
3,66 pp, nove vezes a margem. → [`EVALUATION_METHOD_GUIDE.md`](EVALUATION_METHOD_GUIDE.md) §8

### Quando tudo estiver fechado

```bash
mtlcheck compare runs/<estudo> --arm-a cat --arm-b joint --task cat --state california
```

Aqui entram as estatísticas de verdade — bootstrap por usuário, TOST contra a margem de 0,4 pp,
correção de multiplicidade. É esse comando que **gasta** a leitura, e é por isso que ele é um ato
deliberado e datado, não um efeito colateral de treinar.

---

## 5 · Duas coisas que já estão resolvidas e não precisam mais te preocupar

**Você não vai precisar retreinar para ler o teste.** Desde 2026-08-19, toda execução com a
partição explícita (`--split-seed`) guarda as **predições linha a linha** do fold externo,
automaticamente, logo que o fold termina. As linhas ficam em disco; só o escore é racionado. Quando chegar a hora, o `compare`
lê o que já está lá.

**Ler o teste não é "proibido".** É *uma vez por braço, por ciclo de congelamento*. Se a receita
mudar de verdade, isso abre um ciclo novo e uma leitura nova — declarada e datada, como a de
2026-08-18 foi.

---

## 6 · Estado atual dos estados, que é o que decide o quanto isso importa

| estado | situação |
|---|---|
| **AL, AZ** | desenvolvimento. Teste já lido em 18-08 |
| **Istambul** | ⚠ **não** é estado de desenvolvimento. Era reserva, lido uma vez em 18-08, e é onde a alegação co-primária se sustentou |
| **FL** | desenvolvimento |
| CA, TX | ⚠ **NÃO são reserva intocada** — a nota da tabela da dissertação diz que o batch size foi buscado *at every dataset*, e no protocolo antigo isso tocou o fold reportado. São desenvolvimento, com **menos** contaminação que AL/AZ/IST (a config do joint foi transferida, não buscada), mas não zero |

⚠ E uma ressalva honesta: a leitura de 18-08 descreve uma configuração **superada** — o substrato foi
unificado e o POI2Vec corrigido no dia seguinte. O primeiro ciclo de congelamento foi gasto numa
receita que durou um dia. Isso torna CA e TX o ativo que sustenta a conclusão final, e é a razão de
protegê-los deixar de ser formalidade.
