# Log de desfechos entre estudos

Append-only. Uma linha por desfecho: o que foi perguntado, o que foi medido, o que ficou decidido.
Não é diário de trabalho — o diário de cada estudo é o `log.md` dele.

| Data | Estudo | Desfecho |
|---|---|---|
| 2026-08-12 | _(fundação)_ | Projeto `mtlcheck` aberto como reescrita do v18. Mapa do sistema, arquitetura e ledger de revisão em `docs/`. |
| 2026-08-13 | `porting_validation` | Camada determinística validada contra a referência (grafo, pesos de aresta, janelas, folds, loss, métricas, seleção de época, capacidades). Uma célula treinada — Alabama categoria, seed 0 — reproduz dentro do ruído de execução (Δ 0,006 pp contra ruído de ±0,08). Região e conjunta ainda não rodadas. |
| 2026-08-13 | `porting_validation` | Achado que sai do escopo da reescrita: a auditoria de capacidade da referência conta a cabeça de categoria e os braços de capacidade equiparada **fora do caminho de execução**. Registrado como R14 em `docs/REFERENCE_DEFECTS.md`; toca uma citação da dissertação e do MobiWac. Decisão de errata é do autor. |

## 2026-08-19 — `porting_validation` fecha em paridade; `improvements` abre

**Desfecho.** O porte reproduz a referência em duas famílias sob protocolo pareado: região +0,054 pp
(partição idêntica por hash) e categoria +0,03 (AL) / +0,06 (AZ), média e dispersão dentro do ruído.
O mtlcheck é standalone — do corpus bruto a modelos treinados, sem nada do repo antigo.

**O que custou.** A validação achou um déficit de −0,9 pp em região, rastreado até ser do construtor
e não do sorteio, e daí até três divergências do POI2Vec. Corrigidas e atribuídas uma a uma
(+0,563 / +0,282 / +0,012). ⚠ **Foram correções de migração — bugs nossos — e o resultado é paridade,
não superioridade.**

**O que a auditoria de proveniência revelou.** A campanha de medição inteira rodou de scripts de
shell fora do repo: 46 estudos bancados contra 9 manifestos. Consertado com guardas em tempo de
CONSUMO em vez de criação, que é o princípio que este projeto já tinha descoberto para o lacre e não
aplicava ao resto.

**Roteamento.** As melhorias identificadas ao longo do porte, mais as herdadas do `future_works` do
repo antigo, vão para o estudo [`improvements`](improvements/STUDY.md) — deliberadamente **não**
executadas, porque cada uma sozinha exige receita nova e uma cadeia v20/v21/v22 destruiria a
consistência da v19.

## 2026-08-25 — a ponte é aposentada; `v19_defence` é refeito sob a escada

**Desfecho.** A ponte de calibração — medir dispersão entre execuções em três conjuntos pequenos e
transferi-la para licenciar menos execuções nos grandes — **saiu do protocolo**. Ela media o regime
errado, dava ao menor conjunto veto sobre o maior, agregava por um máximo sem propriedades
conhecidas, e não tem precedente publicado em ML; o análogo mais próximo é o *external pilot*
clínico, criticado por Browne (1995) exatamente por isto.

**O substituto** é a escada do §2a: cada conjunto mede a própria dispersão na **validação interna**
— que não gasta leitura — e escala sozinho, de 2 a 6 execuções, parando quando
`t₀.₉₇₅,P−₁ · UCL₈₀(σ̂)/√P < δ`. Cada execução sorteia `split_seed` e `model_seed` **juntos**, o que
torna o estimando marginal sobre o sorteio de partição em vez de condicional a uma.

**O que isso custou ao `v19_defence`.** Ele existe para ser a *vitrine* do protocolo novo, e rodava
o mecanismo descartado. Refeito do zero por decisão do autor, sem reaproveitar célula: as antigas
são todas de `split_seed = 0` e só a execução `(0,0)` seria reutilizável. A campanha da ponte foi
para [`archive/v19_defence_bridge`](archive/v19_defence_bridge/ARQUIVADO.md).

**O que sobrevive dela e vale para qualquer campanha sobre estes corpora:** o eixo de partição
medido em quatro conjuntos, a precondição de sobreposição de usuários do §4a (24,5 % dos usuários
aparecem em mais de um estado americano; Istambul é o único genuinamente independente), e as bandas
de réplica — que são a evidência de que a ponte não transferia: Istambul, o maior dos três, tem a
**menor** banda, 11× menor que a do Arizona, que detinha o veto.

⚠ **A ressalva que a vitrine nova herda.** Alabama, Arizona e Istambul **já foram lidos**. Uma
leitura nova sorteia partições novas e o `compare` a permite, mas são os mesmos usuários e quem lê
já sabe o que procurar. Numa demonstração de método a afirmação é *"veja como o protocolo se
comporta"*, não *"este é o efeito verdadeiro no Alabama"* — o que torna a segunda olhada aceitável
**declarada**, e só declarada. Florida, California e Texas nunca foram lidos.
