# Verificacao dos numeros das erratas

Medido em 2026-08-13 contra os artefatos, nao contra prosa. **A seccao da tabela abaixo e a
verificacao da errata Q14** (`errata_Q14_capacity_region.tex`), cujo cabecalho aponta para aqui; o
identificador nao aparecia em lado nenhum deste ficheiro ate 2026-09-02, o que fazia um `grep Q14`
concluir que a verificacao nao existia. Fonte de cada arm:
`docs/results/P1/region_head_{california,texas}_region_5f_50ep_v18_*_capmatched*_s0.json`;
comparador do modelo conjunto: `docs/results/closing_data/v18/joint_best_perfold.json`,
celulas `{state}_s0_joint`, campo `top10_full` por fold, mesma semente e mesma engine.

| afirmacao na errata | medido | confere |
|---|---|---|
| California: dedicado pareado acima do conjunto por $0.43$ Acc@10 | $+0.4277$ | sim |
| California: $p = 0.008$, unanime | $p = 0.0082$, unanime nos 5 folds | sim |
| Texas: diferenca de $0.21$ Acc@10 | $+0.2136$ | sim |
| Texas: $p = 0.12$, nao separado de zero | $p = 0.1162$, 4 de 5 folds | sim |
| braco estreito a $57$ por cento do orcamento | $5{,}014{,}942 / 8{,}809{,}533 = 56.9$ por cento | **NAO -- o denominador esta errado, ver abaixo** |
| passo de $352$ para $528$ nao separado de zero | $+0.021$, $p = 0.40$ | sim |
| categoria: $6.5\times$ os parametros baixa o macro-F1 | registro do controle de categoria, $-0.53$, $p = 0.0011$ | sim, mas o fator passa a $6.7\times$ com a recontagem de 2026-09-02 (9.634.471 / 1.433.863; Apendice G corrigido) |

## O denominador estava errado, e com ele a leitura de todos os arms (2026-09-02)

A linha do "braco estreito a 57 por cento" divide por **8.809.533**, que era a contagem do modelo
conjunto em California **reconstruida com valores assumidos**, nao lida de execucao. A correccao de
2026-08-27 (`wrapup/post_submission_studies/EXECUTION_WAVE.md`) ja tinha registado que essa coluna
nao era uma medicao, e deixou o assunto em aberto; ninguem a levou de volta a esta tabela.

O total medido, somado da particao do optimizador no log entregue
(`docs/results/closing_data/v18_2/modal_runs/california_s7_lane_*/logs/california_s7_joint.out`:
cat 1.731.079 + reg 1.835.982 + shared 1.584.128), e **5.151.189**. Contra ele:

| estado | `d_model` | parametros | % do conjunto MEDIDO |
|---|---|---|---|
| Alabama | 624 | 6.978.702 | 166,3 |
| California | 528 | 9.004.686 | 174,8 |
| **California** | **352** | **5.014.942** | **97,4** |
| Texas | 544 | 8.354.882 | 170,5 |

**Os tres arms rotulados "pareados" carregam 1,66 a 1,75 vezes o orcamento do conjunto.** O unico
que aterra na paridade e o de 352 -- o mesmo que o registo anterior dispensava como estando a "57
por cento". E o Texas nao tem arm nenhum perto da paridade.

Reproduzir: `PYTHONPATH=src python research/reproducibility/mobiwac_v18/param_counts.py`, seccao
CAPACITY ARMS. Antes de 2026-09-02 estes racios eram derivados a mao e nao saiam de comando nenhum,
o que e a falha que a AGENT_GUARDRAILS V1 nomeia: um numero carrega o comando que o produziu.

## O arm a paridade tem teste, medido em 2026-09-02

A tabela original testava o arm de 528 e nao o de 352, que era tratado como secundario. Sendo o de
352 o controlo pareado, foi testado agora, na mesma convencao **bilateral** dos numeros ja
publicados:

| arm | delta Acc@10 | folds a favor | p |
|---|---|---|---|
| **352 (97,4 %)** | **+0,4063** | **5/5** | **0,0102** |
| 528 (174,8 %) | +0,4277 | 5/5 | 0,0082 |
| passo 352 -> 528 | +0,0214 | — | 0,4002 |

**O instrumento reproduz os dois numeros que o P1 ja publicava antes de reportar o novo**: o
`p = 0,008` do arm de 528 e o `+0,021, p = 0,40` do passo entre arms. Foi assim que a convencao
bilateral se identificou -- o valor unilateral do 528 e 0,0041, metade do publicado.

Entradas: conjunto California semente 0, por fold, de `joint_best_perfold.json`, celula
`california_s0_joint`, campo `top10_full`: 64,407 / 64,019 / 64,491 / 64,505 / 65,095. Arm de 352,
`per_fold[].top10_acc` de
`docs/results/P1/region_head_california_region_5f_50ep_v18_california_reg_capmatched_s0.json`
(`config.overrides.d_model = 352`): 64,693 / 64,766 / 64,831 / 64,762 / 65,498.

Os tres ficheiros dos arms de capacidade nao existiam nesta maquina -- viviam so na `nespedgpu`.
Foram trazidos em 2026-09-02 para **`docs/results/P1/`, a partir da RAIZ DO REPOSITORIO**, nao do
`docs/` da dissertacao. Ha dois `docs/` nesta arvore, e um `find docs/results` corrido de dentro de
`articles/dissertacao/` procura no ficheiro errado e conclui que os artefatos nao existem -- foi o
que aconteceu ao verifica-los.

✅ **Rastreados desde 2026-09-06** (commit `0c226b98`, *"os tres JSON do controlo de capacidade entram
no git"*, com `git add -f`). O paragrafo que estava aqui dizia que o git nao os via e que
traze-los era decisao do autor. Isso ficou resolvido nesse commit e so foi corrigido aqui a
2026-10-02. A armadilha continua valida para o resto do directorio: o padrao `results` em
`.git/info/exclude` esconde `docs/results/` de `git status`, portanto um ficheiro novo ali nao
aparece nem como untracked.

## Convencao de metrica

A metrica de regiao e `top10_acc` por fold. Verificado antes de qualquer comparacao: o arquivo do
dedicado reportado reproduz $63{,}4456$ a partir dos seus proprios folds por esse campo, que e o
valor da coluna Dedicated da tabela do Cap. 5 em California. Isso fixa qual campo usar e descarta a
leitura errada, que teria usado o valor bruto sem desconto de cobertura.

## Ausencias medidas

Nas tres extracoes completas de PDF e no fonte vivo com comentarios removidos:
`capacity-matched`, `confounded with capacity`, `several times the size`, `on three grounds`,
`fourth ground`, `forward-edge` tem **zero** ocorrencias no volume principal. `linear probe` tem
uma, dentro da tabela de errata. `separate study` tem zero nos dois volumes.

## Desvio registrado nos tres arms

`MTL_STRICT` omitido: o certificado de empate aborta a celula inteira por uma linha ambigua em
$585{,}091$ (0,00017 por cento). Os logs registram o aviso em vez do abort.
