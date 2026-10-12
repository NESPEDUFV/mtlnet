# Q15 -- o piso do encoder por treinar: resultado

**Medido em 2026-09-06/07**, em `nespedgpu`. Semente de treino 0, cinco dobras, receita identica a
das celulas dedicadas de categoria entregues. **Nao gerou errata**: o resultado nao contradiz o
texto depositado, quantifica uma afirmacao que ele ja faz por palavras.

## A pergunta

O Capitulo 5 diz, no texto entregue (`5_mobiwac/06_results.tex`):

> "Most of the category difference is therefore already available in the raw per-visit features;
> what the check-in-level representation adds beyond them on this axis is small, and **this control
> does not separate it**."

Aquela ultima clausula e uma confissao de limite: o controlo de concatenacao (Q13) mostra que as
features brutas carregam a maior parte, mas nao separa **quanto** o grafo treinado acrescenta por
cima delas. Este estudo mede o piso que fecha essa separacao.

## O desenho

Um unico braco, e a sua definicao e a parte que importa: **a arquitectura na inicializacao**, antes
de qualquer passo do optimizador. Nao e "o mesmo procedimento com zero epocas" -- para epocas > 0 o
codigo selecciona o checkpoint de **menor perda de treino**, e essa regra nao tem analogo com zero
passos. A distincao esta escrita no proprio patch para ninguem ler as duas coisas como uma serie.

Tudo o resto e identico ao build v18: `--repr-seed <s> --encoder resln --forward-only
--add-continuous-time`, readout `prefix_forward_only --self-test`. **So a contagem de epocas e o
nome do engine mudam.** Uma segunda diferenca tornaria a comparacao ilegivel.

**Quatro sementes de representacao (42, 0, 1, 7), nao uma.** O substrato entregue fixa a semente 42
porque o treino lava a inicializacao; num braco de piso a inicializacao **e** o tratamento, logo um
so sorteio e uma amostra de uma projeccao aleatoria e nao diz nada sobre dispersao.

## Os numeros

Categoria (macro-F1), modelo dedicado, semente de treino 0:

| | Alabama | Arizona |
|---|---|---|
| semente de repr. 0 | 30,5418 | 34,2916 |
| semente de repr. 1 | 30,5449 | 34,3389 |
| semente de repr. 7 | 30,6235 | 34,2318 |
| semente de repr. 42 ⚠ | 30,6846 | 34,3779 |
| **media / sd** | **30,5987** / 0,0594 | **34,3101** / 0,0545 |
| entregue (semente 0) | 30,7654 | 34,508 |
| entregue (agregado 4 sementes) | 30,77 ± 0,07 | 34,57 ± 0,04 |

## A decomposicao, que e o resultado

Contra `src/tables/mobiwac/representation.tex`, na mesma escala:

| | *place-level* | check-in **treinado** | check-in **por treinar** |
|---|---|---|---|
| Alabama | 29,15 | 30,77 (+1,62) | **30,60** |
| Arizona | 31,93 | 34,51 (+2,58) | **34,31** |

O encoder sem uma unica epoca ja recupera **+1,45 dos +1,62** em Alabama e **+2,38 dos +2,58** em
Arizona. A vantagem da representacao no eixo da categoria e portanto **cerca de nove partes de
granularidade da entrada para uma parte de grafo aprendido**. O que o treino acrescenta, 0,17 a
0,26 pontos, e **menor que a dispersao entre sementes do proprio braco treinado**.

## ⚠ Duas ressalvas que viajam com o numero, sempre

1. **Eixo da categoria e mais nada.** A regiao nao foi tocada, e e onde vivem as alegacoes mais
   fortes da tese (Texas +1,21, California +1,06, nao-inferioridade nos seis). "O encoder estava por
   treinar e nada mudou" **nao** e uma afirmacao sobre o substrato como um todo.
2. **Nao diz que a representacao nao vale nada.** Diz que o **componente aprendido** acrescenta pouco
   **neste eixo**. A estrutura ao nivel do check-in continua a fazer +1,45/+2,38 sobre o nivel do
   lugar, e essa alegacao fica intacta.

Um piso para a **regiao** nao e a experiencia simetrica: a via de regiao le os embeddings de regiao
do engine v14 (`--region-emb-source`), nao do encoder aqui aleatorizado, e o
`region_embeddings.parquet` do v18 e um **symlink** para esse directorio. Seria aleatorizar um
substrato diferente -- pergunta de desenho, nao a mesma flag. Nao foi feito.

## Integridade -- as tres verificacoes, com valores

1. `build.json` regista `epochs: 0` nas oito celulas, lido do ficheiro e nao inferido.
2. Nenhum checkpoint reaproveitado: cada directorio foi apagado imediatamente antes do seu build.
3. **Cosseno medio linha-a-linha contra os embeddings v18 treinados**, que e a verificacao que prova
   que o encoder esta mesmo por treinar em vez de o assumir:

   | semente | Alabama | Arizona |
   |---|---|---|
   | 42 ⚠ | 0,796069 | 0,848251 |
   | 0 | 0,045814 | 0,066566 |
   | 1 | −0,039271 | 0,083166 |
   | 7 | 0,071876 | −0,024299 |

   Nenhum perto de 1,0 -- confirmado por treinar em todas.

**⚠ A SEMENTE 42 E A DA INICIALIZACAO DO SUBSTRATO ENTREGUE**, e o cosseno mostra a consequencia: os
seus embeddings retem 0,80/0,85 de semelhanca com os treinados, contra ~0 das outras tres. A celula
42 **nao e independente** da corrida entregue, e parte da sua proximidade pode ser inicializacao
partilhada e nao "as features ja sao separaveis". **As sementes 0/1/7 sao o piso limpo**, e a
conclusao aguenta-se descontando a 42 por completo. Foi o `worker` que notou isto e o mediu; nao
estava no desenho que eu especifiquei.

## Nota de escala, para nao se comparar o que nao e comparavel

O piso varia a semente de **representacao** com a de treino fixa em 0; o ±0,07 / ±0,04 entregue
varia a semente de **treino**. Sao fontes de variacao diferentes. A comparacao emparelhada e
30,6846 contra 30,7654 (AL) e 34,3779 contra 34,508 (AZ), ambas a semente de treino 0.

## Duas correccoes do metodo, registadas porque custaram duas viagens a maquina

**O mecanismo que eu especifiquei nao funcionava.** `--epochs 0` da um laco vazio, mas vinte linhas
abaixo ha um `model.load_state_dict(best_state)` incondicional e o `best_state` nunca chega a ser
atribuido: rebenta, antes de escrever nada. Eu tinha lido o laco e nao a linha seguinte.

⚠ **O `best_epoch=0 loss=inf` imprime ANTES do crash.** Quem verificasse por grep no log leria
aquilo como uma corrida bem-sucedida. Mesma familia dos portoes que passam por nao chegarem a
comparacao.

**O portao de inercia que eu exigi nao era satisfazivel.** Pedi hashes identicos byte-a-byte antes e
depois do patch; deram diferentes. O `worker` correu um controlo que eu nao tinha pedido -- o
**mesmo** codigo corrigido duas vezes -- e os hashes voltaram a diferir. O pipeline **nao e
reprodutivel ao bit**: a diferenca entre patch e nao-patch (2,646e-05) e **menor** que a variacao
entre duas corridas iguais (2,772e-05), com identidade de linhas e metadados exacta e cosseno
0,999999999999. A inercia fica provada; o meu portao e que estava mal especificado.

> **Piso de ruido, medido e nao portavel.** `build_study_repr.py --state alabama --epochs 5
> --repr-seed 42 --encoder resln --forward-only --add-continuous-time`, duas vezes seguidas, em
> `nespedgpu` (RTX 6000 Ada, driver 580.173.02, CUDA 13.0, PyTorch 2.11.0+cu128): **max abs
> 2,772e-05** na tabela de embeddings. **"Reproduzir o substrato entregue" so pode significar
> reconstruir dentro do ruido, nunca igualar bytes.** Quem verificar um substrato por hash vai
> concluir que foi adulterado. Propriedade desta maquina e desta combinacao de driver/torch.
>
> Nao move digito nenhum: sementes 0/1/7/42 sao sorteios praticamente descorrelacionados (cosseno ~0
> entre si) e o macro-F1 delas so varia 0,14 pp (AL) / 0,15 pp (AZ). Uma perturbacao ordens de
> grandeza menor do que "embedding completamente diferente" nao toca uma casa decimal reportada.

## Comandos

Engine `check2hgi_v18_untrained_s${r}`, por estado x semente:

```
build:       python scripts/integrity_v2/build_study_repr.py --state $st --cell V18UT \
               --repr-seed $r --epochs 0 --device cuda --encoder resln \
               --study-root results/$ENG --forward-only --add-continuous-time
infer:       python scripts/integrity_v2/infer_checkins.py --state $st \
               --checkpoint results/$ENG/$st/V18UT/checkpoint.pt \
               --readout prefix_forward_only --out results/$ENG/$st/V18UT/win_matched.npz --self-test
materialize: python scripts/integrity_v2/materialize_engine.py --state $st \
               --arm-npz results/$ENG/$st/V18UT/win_matched.npz \
               --source-engine check2hgi_dk_ovl --dest-engine $ENG
train:       env MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1 python scripts/train.py \
               --task next --state $st --engine $ENG --model next_gru --embedding-dim 64 \
               --folds 5 --epochs 50 --seed 0 --batch-size 8192 \
               --max-lr <0.0025 AL | 0.0005 AZ> --logit-adjust-tau 0.5 --compile --tf32 --no-checkpoints
score:       python scripts/closing_data/score_stl_cat_ceiling.py <rundir> --tag floor_${st}_s${r}
```

`temp/sequences_next.parquet` copiado de `check2hgi_dk_ovl`; `region_embeddings.parquet`
**symlinked** de `check2hgi_design_k_resln_mae_l0_1` -- verificados symlinks reais nas oito, nunca
copias. Nada escrito em `output/check2hgi/`, `output/check2hgi_v18/` nem no directorio v14
(confirmado por `find -newer`, vazio).

## Duas alteracoes de codigo, aplicadas pelo autor

O classificador de seguranca desta instalacao recusou deixar o agente executor editar qualquer dos
dois ficheiros; os diffs foram entregues ao autor, que os aplicou.

> ✅ **CORRIGIDO 2026-09-08: os dois patches estao commitados.** `f11c8cc7`, "Os dois patches que
> produziram o Q15 saem do nespedgpu e passam a ter historia" -- verificado ao vivo em `nespedgpu`
> apos `git pull` (HEAD `e2ebec55`): `grep "FLOOR ARM"` e `grep "CHECK2HGI_V18_UNTRAINED"` devolvem
> as linhas do patch em ambos os ficheiros, no checkout normal, sem diferenca de `git status`. A
> nota anterior (2026-09-07) estava certa quando escrita; deixou de estar. Os oito valores, a
> decomposicao e o piso de ruido tambem ganharam sidecar estruturado em
> `docs/results/closing_data/v18_untrained_floor/` (nove ficheiros JSON, um por celula mais um
> `summary.json`), para nao dependerem so da prosa deste ficheiro.

1. `scripts/integrity_v2/build_study_repr.py` -- duas ramificacoes explicitas antes do
   `load_state_dict`: com `epochs == 0` usa o estado de inicializacao; com epocas > 0 e `best_state`
   ainda `None`, **recusa escrever** e diz que todas as perdas foram nao-finitas.

   ⚠ **Isto e deliberado e nao e o mesmo que semear o `best_state` antes do laco.** Como
   `lowest = math.inf` e a guarda e `l < lowest`, qualquer perda finita ganha na primeira epoca --
   por isso semear *parece* inerte. Mas com perdas **NaN** o `NaN < inf` e falso, o `best_state`
   ficaria com o valor semeado, e a corrida escreveria um artefacto completo com **pesos por treinar
   enquanto o `build.json` diz 500 epocas**. Hoje esse caso rebenta alto, e tem de continuar a
   rebentar.

2. `src/configs/paths.py` -- quatro membros novos no enum `EmbeddingEngine`, acrescentados no fim,
   mesmo padrao da familia `CHECK2HGI_IV2_*`. Pura adicao, sem reordenar nem tocar em membros
   existentes. O `--engine` do `train.py` e um enum fechado e rejeitava os nomes novos.
