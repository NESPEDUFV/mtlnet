# Arquivado em 2026-08-25 — a campanha que demonstrava a ponte

Este estudo rodou a leitura confirmatória sob o protocolo que usava a **ponte de calibração**:
medir a dispersão entre execuções em três conjuntos pequenos e transferi-la para licenciar menos
execuções nos grandes.

**A ponte foi aposentada** (protocolo §2a). Ela media o regime errado, dava ao menor conjunto veto
sobre o maior, agregava por um máximo sem propriedades conhecidas, e não tem precedente publicado em
ML. O substituto é a escada de escalada, em que cada conjunto mede a si mesmo na validação interna.

**Por isso este estudo saiu de cena.** O `v19_defence` existe para ser a *vitrine* do protocolo de
avaliação novo; uma vitrine que demonstra um mecanismo descartado não demonstra coisa nenhuma. O
estudo vivo é [`../../v19_defence/`](../../v19_defence/), que roda a escada.

## O que ficou aqui, e por que importa

**A leitura confirmatória de Alabama, Arizona e Istambul aconteceu.** 36 pares
(identidade, conjunto) constam de `studies/READ_LEDGER.json` como GASTOS, e isso **não se desfaz**
por o estudo ter sido arquivado. Os payloads estão em `leitura/`.

| conjunto | usuários | cat | reg | co-primária |
|---|---:|---|---|---|
| alabama | 1 101 | −0,060 · não-inferior | −0,795 · **inferior** | não vale |
| arizona | 2 136 | −0,128 · não-inferior | −0,547 · inconclusivo | não vale |
| istanbul | 14 530 | **+0,178 · superior** | −0,139 · não-inferior | **vale** |

⚠ **A consequência que a campanha nova herda:** esses três conjuntos **já foram olhados**. Uma
leitura nova sorteia partições novas e o `compare` a permite — mas são os mesmos usuários, e quem
lê já sabe o que procurar. A vitrine nova tem de declarar isso onde reporta AL/AZ/IST. FL, CA e TX
nunca foram lidos e seguem limpos.

## O que este estudo produziu e continua valendo

- **O eixo de partição, medido** em quatro conjuntos ([`S10_4_PARTITION_AXIS.md`](S10_4_PARTITION_AXIS.md)) —
  é o dado que mostrou que a banda de um conjunto pequeno não transfere para um grande, e que levou
  à escada;
- **A precondição de sobreposição de usuários do §4a, executada e reprovada**
  ([`S4A_USER_OVERLAP.md`](S4A_USER_OVERLAP.md)) — 24,5 % dos usuários aparecem em mais de um estado
  americano, e Istambul é o único conjunto genuinamente independente. Isso vale para qualquer
  campanha sobre estes corpora, inclusive a nova;
- **As bandas de réplica medidas**, que são a única evidência empírica de que a ponte não transferia:
  Istambul, o maior dos três, tem a **menor** banda — 11× menor que a do Arizona, que detinha o veto.

## O protocolo que governou isto

Preservado sem edição em [`../../../docs/v19_RECORD.md`](../../../docs/v19_RECORD.md).
