# improvements — o que melhorar agora que o porte está em paridade

## A pergunta

O porte terminou e reproduz a referência. **O que, das melhorias identificadas ao longo do caminho e
herdadas do sistema antigo, vale executar — em que ordem, e por quê?**

## Por que é um estudo separado do `porting_validation`

Porque a barra é outra, e misturar as duas foi o que produziu a confusão que o
[`DIVERGENCE_REGISTER.md`](../../docs/DIVERGENCE_REGISTER.md) existe para desfazer.

| | `porting_validation` | **`improvements`** (este) |
|---|---|---|
| pergunta | o mtlcheck reproduz o v18? | o que fazer melhor que o v18? |
| critério de sucesso | Δ dentro do ruído | Δ **fora** do ruído, na direção certa |
| o que um Δ positivo significa | fechamos um buraco nosso | mudamos a ciência, e isso tem de ser declarado |
| comparabilidade com a dissertação | preservada | **quebrada de propósito** — cada item tem de dizer o que quebra |

Um número que sai daqui **não é comparável** com a dissertação sem nomear a mudança. Um número que
sai do `porting_validation` é.

## As três fontes que este estudo reconcilia

Ninguém tinha reconciliado as três entre si, e elas foram escritas por agentes diferentes em momentos
diferentes do projeto:

1. **Achados do próprio porte** — [`../porting_validation/IMPROVEMENTS_BACKLOG.md`](../porting_validation/IMPROVEMENTS_BACKLOG.md),
   medidos e deliberadamente não executados para entrarem juntos.
2. **`docs/OPTIMIZATIONS.md`** e **`docs/REFERENCE_DEFECTS.md`** (R1–R16) do mtlcheck — o que foi
   medido como custoso e o que foi reproduzido em vez de corrigido.
3. **`docs/future_works/`** do repositório antigo — 16 memos, 1 608 linhas, a agenda de pesquisa que
   ficou pendente lá.

⚠ **A terceira fonte precisa de triagem, não de importação.** Vários memos foram escritos para um
sistema que o porte mudou: o `evaluation_protocol_cleanup.md` pede exatamente o protocolo aninhado
que o mtlcheck já implementou, e os memos de substrato duplo descrevem uma arquitetura que a v19
eliminou. Copiar a lista sem julgar produziria trabalho para reconstruir o que já existe.

## A distinção que a triagem tem de fazer

Os memos herdados misturam duas coisas, e elas não pertencem ao mesmo estudo:

- **melhoria de implementação** — a máquina faz X e deveria fazer Y. Pertence aqui.
- **agenda de pesquisa** — arquiteturas MTL, balanceadores de loss, sweeps de cabeça. São perguntas
  científicas abertas sobre o *modelo*, não sobre o porte. Pertencem a estudos próprios, e este
  estudo só as **registra e roteia**.

## Estado

Ver [`STATE.md`](STATE.md). O plano priorizado está em [`PLAN.md`](PLAN.md).


---

## ⚠ Um documento de defesa depende dos números deste estudo

**2026-08-20.** Existe, no repositório `ingred`, um documento de preparação para a banca:

    /Users/vitor/Desktop/mestrado/ingred/articles/dissertacao/wrapup/NEW_VERSION.md   (573 linhas)

Ele cita números **deste** repositório e foi escrito contra o estado de 20-08. Quem executar este
estudo **vai** invalidar parte dele, porque toda melhoria da fila reconstrói o substrato.

### O que muda o documento, e quando

| o que executar | o que isso invalida lá |
|---|---|
| **`mae_poi_target_dim` 8→7** | a paridade contra a dissertação (hoje Δ médio −0,001 pp em 8 células). Medido em +0,116 cat / −0,053 reg, uma réplica |
| **Delaunay unidades × POI2Vec simetrização** (fatorial 2×2) | idem, e em magnitude **não medida** — é a mudança de maior alcance da lista |
| **congelar a v20** | a linha de base inteira. Todo número da v20 é coluna 3 do `DIVERGENCE_REGISTER` — comparabilidade quebrada por declaração |
| **rodar o §8a** (`eval/optimism.py`, exige `retain_checkpoints != "none"`) | a cifra de otimismo de seleção. Hoje o documento diz **"sugerido por um fold, nunca medido"**, com o ponteiro para este instrumento. Rodá-lo troca uma sugestão por duas medições — `a1 − b1` e `b1 − b2`, que o protocolo proíbe somar |

### O que fazer

Avise a sessão que mantém o `NEW_VERSION.md` quando qualquer um dos quatro rodar. As três seções
que a banca puxa primeiro, segundo quem o escreveu, são a **3**, a **4** e a **8** — paridade,
errata e o que está aberto.

O item do §8a é o mais interessante para eles: hoje a resposta oral registrada é *"temos uma
sugestão de um fold e o instrumento pronto para medir direito"*. Depois de rodar, vira um número —
e a decomposição importa mais que o número, porque **só o `b1 − b2` é propriedade do modelo
conjunto**; o `a1 − b1` é propriedade do protocolo e seria pago por qualquer braço lido sob a regra
antiga.
