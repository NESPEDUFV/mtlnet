# Estado — v19_defence

> Contrato com quem retoma: humano ou agente. Quem encerra uma sessão atualiza este arquivo.
> Se estiver desatualizado, ele é pior que inexistente.

**Última atualização:** 2026-08-25, com a escalada quase fechada

> ⚠ Este arquivo não existia até 24-08. O estudo gastou a leitura irreversível de três conjuntos
> sem ter um. Foi uma auditoria que apontou a falta, não a suíte — `tests/test_studies_contract.py`
> só verifica proibições, e `studies/README.md` §Ciclo de vida enuncia a obrigação em prosa.

## Onde estamos

**A etapa 3 foi executada em 3 dos 6 conjuntos.** Alabama, Arizona e Istambul foram lidos em
2026-08-24; 36 pares (identidade, conjunto) constam de `studies/READ_LEDGER.json` como GASTOS e não
podem ser relidos. Os três grandes estão bloqueados por uma escalada que o próprio protocolo mandou
fazer.

**A escalada, em 25-08 12:30 UTC:** Flórida e Califórnia **completas** — 12 de 12 células, todas
com `result.json` e `predictions.parquet`, conferidas em disco. Texas **em voo** (~12,7 h). O reboot
que se esperava para a manhã de 25-08 **não aconteceu** (uptime de 13 dias), então a wave de FL/CA
correu sem interrupção e não precisou de resume.

Quando o Texas fechar, as 18 células da escalada existem e os três grandes ficam legíveis.

## O resultado da ponte

Receita `recipes/analysis/v19_headline.toml`, fingerprint `a3e2854771f0868d`. Δ em pontos
percentuais, joint menos o dedicado.

| conjunto | usuários | cat | reg | co-primária |
|---|---:|---|---|---|
| alabama | 1 101 | −0,060 · não-inferior | −0,795 · **inferior** | não vale |
| arizona | 2 136 | −0,128 · não-inferior | −0,547 · inconclusivo | não vale |
| istanbul | 14 530 | **+0,178 · superior** | −0,139 · não-inferior | **vale** |

Categoria se sustenta nos três. Região tem gradiente com o tamanho do conjunto — −0,795 → −0,547 →
−0,139 — e o p de permutação é 0,0001 nos dois pequenos, então o efeito negativo é real, não ruído.

O δ-crítico diz quanto falta: Alabama região seria não-inferior a partir de δ = 0,96 pp, Arizona a
partir de 0,72. A margem deste protocolo (0,4 pp) é estrita de propósito; com a margem usual de
1 pp a mesma tabela lê "não-inferior nos três", e a linha de sensibilidade confirma.

**A frase cross-state (§4a), sobre os três lidos** — `mtlcheck conjunction`, combinador Bonferroni:

```
cat  não-inferioridade  u* = 3/3      cat  superioridade  u* = 1/3
reg  não-inferioridade  u* = 1/3      reg  superioridade  u* = 0/3
```

⚠ Istambul é o **único conjunto genuinamente independente** (§12.6c: 24,5 % dos usuários aparecem
em mais de um estado americano). É também o que mais sustenta a tese. Isso é bom para a conclusão e
limita o que "replicado em seis conjuntos" pode dizer.

## Feito

- [x] etapas 0 a 2 — substratos e as 54 células, fechadas em 2026-08-23
- [x] as 54 identidades pinadas contra o que cada célula bancou · `ec002200`
- [x] o eixo de partição do §10.4, medido em quatro conjuntos · `f9a3c894`, `c44482f5`
- [x] a precondição de sobreposição de usuários do §4a, executada e reprovada · `c44482f5`
- [x] guardas: janela, vocabulário, canário estrito, célula selada sem identidade · `f60f7fee`
- [x] δ-crítico e a camada cross-state do §4a · `f8881913`
- [x] **a leitura da ponte — AL, AZ, IST** · `8eefa2d0`
- [x] os manifestos da escalada S=4 · `17a85b20`
- [x] as duas recusas que tornavam os grandes ilegíveis · `57316489` (§12.7)
- [x] o `p` da superioridade do §4a era BILATERAL — região saía `u* = 3/3` sobre conjuntos em que o
      joint é inferior · `58f33044`
- [x] as sete guardas de leitura saem do CLI para `eval/gates.py` · `ba7c2826`
- [x] §12 em ordem 12.1→12.9, com índice de "onde mora a regra vigente" · `75b97d34`
- [x] o envelope dos gates é 13× a banda que audita — diagnóstico `own_band` registrado ANTES da
      leitura dos grandes · `c1d16405` (§12.9)
- [x] a escalada: **Flórida e Califórnia completas** (12/12), Texas em voo desde 25-08
- [x] a ponte foi **aposentada** para ciclos futuros e substituída pela escada do §2a — o protocolo
      caiu de 1084 para 489 linhas e o que governou esta campanha está em
      [`../../docs/v19_RECORD.md`](../../docs/v19_RECORD.md) · `d67716c4`, `e3021167`, `52bb551a`

## Próximo

1. ~~Lançar o Texas~~ — **feito** em 25-08 12:30 UTC. Em voo.

2. Quando as 18 células da escalada fecharem, a leitura dos grandes — **e ela usa outra receita**:

   ```bash
   mtlcheck compare <runs>/v19_defence --analysis recipes/analysis/v19_headline_s4.toml \
       --state florida --dry-run \
       --bridge-reading studies/v19_defence/leitura/alabama.json \
       --bridge-reading studies/v19_defence/leitura/arizona.json \
       --bridge-reading studies/v19_defence/leitura/istanbul.json
   ```

   `v19_headline_s4.toml` difere da antecessora em três linhas: o nome, `accepts_bridge_from` e a
   tabela de compra dos três grandes. Tudo que decide o significado de um p é idêntico, e a suíte
   afirma isso. **Não use `v19_headline.toml` para os grandes** — ela pré-registra duas réplicas, e
   o guarda de réplicas recusa.

3. O `conjunction` final, sobre os seis payloads, com a receita `_s4`.

   ⚠ **Ao ler os grandes, olhe o `own_band` ao lado do desfecho dos gates** (§12.9). O envelope que
   os audita vem da ponte e é **13× a banda própria de Istambul** em região; o passo do gate (iii) a
   S=4 é 0,3802 contra uma margem de 0,4, então um carimbo `seed-limited` é o desfecho esperado e
   não diz que a célula é instável. O diagnóstico existe para separar as duas coisas.

## Bloqueios

- O Texas, ~12,7 h, em voo desde 25-08 12:30 UTC. É o último bloqueio antes da leitura dos grandes.

## O que já foi tentado e não funcionou

- **Ler os grandes com 2 réplicas.** O gate de calibração do §2 reprova em região
  (`sd/√2 = 0,2688 > δ/3 = 0,1333`, banda vinda do Arizona) e o §2 manda S=4 desde o início.
- **Editar `[replicates]` em `v19_headline.toml`.** Vetado para sempre: os três payloads da ponte
  carregam o fingerprint dela e a ponte não pode ser relida. Escalar é arquivo NOVO (§12.7).
- **Descartar a réplica destoante do Arizona** (semente 0 do joint, −1,016 contra ≈−0,39). Ela não
  tem defeito atribuível — varredura limpa em avisos, OOD, épocas e telemetria de gradiente — e o
  limite inferior unilateral de 95 % para σ (0,196) fica acima do limiar (0,189), então a reprovação
  não é azar de estimação. O déficit vem de ~20 usuários muito ativos.
- **Alimentar a superioridade do §4a com o p de permutação cru.** Ele é bilateral: região saía
  `u* = 3/3` com o veredito marginal em `0/3`, sobre conjuntos em que o joint é inferior. Corrigido
  pela conversão direcional (`58f33044`) — e o defeito só apareceu quando alguém RODOU o comando
  sobre dado real, meio dia depois de ele ser escrito. A suíte passava.
- **Abolir a ponte, ou trocar a agregação, para poupar as 27 h.** Avaliado por um advisor de
  metodologia em 24-08 e **rejeitado para o v19**: a ponte não enviesa estimativa nenhuma (a banda
  não entra em estimador), e não causou as horas — S=4 em tudo sem ponte custa as MESMAS, e S=2 em
  tudo não tem resposta para "por que dois bastam". Mexer na agregação depois de ver o gate reprovar
  é o pós-hoc que o §12.7 cataloga. O que fica para o v20 está em
  [`../../docs/future_works/banda_da_ponte_transfere.md`](../../docs/future_works/banda_da_ponte_transfere.md)
  e no §12.9.
