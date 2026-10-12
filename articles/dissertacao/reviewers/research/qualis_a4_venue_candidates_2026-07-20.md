## question

Follow-up to `qualis_classification_2026-07-20.md`. User downloaded the official 2025 CAPES
"Computação — Classificação de Eventos" spreadsheet from Sucupira
(`~/Downloads/Computação_Classificação de Eventos 2025.xlsx`, 781 rows, cols Sigla/Nome/Estrato).
Goal: (1) re-check CBIC/CoUrb/MobiWac against the 2025 numbers; (2) find Qualis A4 venues
thematically close to the dissertation (mobility, neural networks, ML, POI, LBSN, big data, MTL,
computer networks) that are still active, for a post-defense (~Sep 2026+) submission target.

## 2025 vs 2017-2020 recheck (local spreadsheet, parsed via openpyxl)

| Evento | 2017-2020 | 2025 |
|---|---|---|
| CBIC | B4 | B4 (unchanged) |
| CoUrb (`COURB` / "Workshop of Urban Computing") | B4 | B4 (unchanged) |
| MobiWac | B2 | **B3 (dropped one stratum)** |

## A4 candidates extracted from the 2025 sheet (134 total A4 rows; keyword-filtered)

Mobility/wireless: `MOBIQUITOUS`, `MSWIM`, `NTMS`, `VNC`, `WD`. Neural nets/ML: `ESANN`, `IWANN`,
`ICMLC`. Computer networks (CoUrb's parent event): **`SBRC`** (the flagship symposium itself is
A4 — CoUrb is a satellite workshop classified separately at B4). Databases/big data: `SBBD`.
Complex networks/graphs: `COMPLEXNETWORKS`. General AI: `EPIA`.

## CFP / active-status verification (deep-research workflow, 95 agents + 1 targeted follow-up
agent for the mobility cluster, run 2026-07-20; "today" = 2026-07-20)

| Evento | Ativo / próxima edição | Status do CFP | Aderência temática |
|---|---|---|---|
| **MOBIQUITOUS** | Sim — 2026, 16-18 nov, Beppu (Japão) | **Fechado** — Round 1 (14/jun) e Round 2 (28/jun) já passaram | **Alta** — mobile/ubiquitous computing/networking, o mais próximo do tema |
| **MSWiM** | Sim — 28ª ed., 26-30 out 2026, Paris | **Fechado** — deadline (estendido) 23/jun/2026 já passou | **Alta** — modelagem/simulação de sistemas sem fio e móveis |
| **NTMS** | Inconclusivo — só a 12ª ed. (2025) é visível; cadência irregular (2019/2021/2025), nada de 2026/2027 achado | Desconhecido | Alta (mobilidade + segurança), mas série pode estar dormente |
| **VNC (IEEE Vehicular Networking)** | Ed. 2026 já ocorreu (8-10 jun, Montreal); página oficial IEEE ITSS diz "No upcoming conference" | **Fechado** — deadline era 16/jan/2026; 2027 não anunciada | Média-alta (redes veiculares = mobilidade), mas sem próxima janela visível |
| **WD (Wireless Days)** | Inconclusivo — última edição confirmada foi a 13ª (dez/2025, Niterói); site oficial fora do ar | Desconhecido | Alta, mas status da série não confirmável agora |
| **ESANN** | Sim — 34ª ed., 22-24 abr 2026, Bruges (já ocorreu) | **Fechado** — deadline foi 26/nov/2025 | Baixa — ANN/CI/ML genérico, sem trilha de mobilidade |
| **IWANN** | Sim — 19ª ed., 16-18 jun 2027, Tenerife | **Aberto/futuro** — 1st CFP anunciado 28/mai/2026, deadline ainda não publicado | Média — deep learning/bio-inspirado, sem trilha de mobilidade/POI |
| **ICMLC** | Sim — 19ª ed. (ICMLC 2027), 26/fev–1/mar 2027, Shenzhen | **Aberto** — deadline **25/set/2026** (~2 meses a partir de hoje) | Baixa-média — ML/computação genérico, sem trilha específica de mobilidade/POI visível |
| **SBRC** (trilha principal, não o CoUrb) | Sim — 44ª ed., 25-29 mai 2026, Praia do Forte/BA | **Fechado** — ciclo 2026 já em fase de camera-ready; 2027 não anunciado | Baixa no trilha principal (redes/sistemas distribuídos genérico) — o encaixe real do autor é o workshop satélite CoUrb (B4), não a trilha A4 |
| **SBBD** | Sim — 41ª ed., 8-11 set 2026, São Carlos/SP (ICMC-USP) | **Ambíguo** — página não mostra deadlines por trilha; claim de "inscrições abertas agora" foi refutada (0-3) | Média via a trilha DS4SG (Data Science for Social Good) — não confirmado se cobre mobilidade/POI |
| **Complex Networks** | Sim — ed. 2026 | **Aberto** — deadline **02/set/2026, 23:59 AoE** | Média (plausível — redes de mobilidade humana são tema clássico de network science) mas não confirmado contra os tópicos exatos do CFP |
| **EPIA** | Sim — 25ª ed., 2-4 set 2026, Madeira | **Fechado** — deadline (rígido, sem extensão) era 29/mai/2026; notificação 12/jul, camera-ready 25/jul (iminente) | Baixa-média — IA geral |

## Avaliação (síntese para decisão)

**Nenhum evento A4 com CFP genuinamente aberto tem alta aderência temática ao POI/mobilidade/LBSN
do autor.** Os dois eventos de maior aderência (MOBIQUITOUS, MSWiM) já fecharam o ciclo 2026; a
próxima janela real para eles (ciclo 2027) ainda não foi anunciada — plausivelmente abrirá entre
~dez/2026 e mar/2027, o que é compatível com o cronograma pós-defesa (~set/2026 em diante) se o
autor não tiver pressa.

Dos eventos com CFP **hoje** genuinamente aberto:
1. **Complex Networks 2026** (deadline 02/set/2026) — melhor aposta relativa: aderência plausível
   via network science / grafos de mobilidade, mas precisa checar a lista de tópicos do CFP antes
   de comprometer (não verificado nesta pesquisa).
2. **ICMLC 2027** (deadline 25/set/2026) — aberto, mas aderência temática fraca (ML genérico);
   só faz sentido se o artigo for reformulado como contribuição metodológica de ML/MTL pura, sem
   framing de mobilidade/POI.
3. **IWANN 2027** — tecnicamente aberto (1st CFP já saiu) mas sem deadline publicado ainda; dá
   para monitorar mas não para planejar em cima agora.
4. **SBBD 2026** — status de deadline não confirmado; precisa checar a trilha DS4SG diretamente
   antes de descartar ou perseguir.

## caveats / open questions

- NTMS e WD ficaram **inconclusivos** (não "confirmadamente inativos") — merece um novo lookup
  dedicado antes de descartar, especialmente NTMS (mobilidade + segurança, boa aderência) caso a
  série ainda esteja viva com cadência irregular.
- SBRC/CoUrb: a trilha principal do SBRC é A4, mas o encaixe temático real do autor está no
  workshop satélite CoUrb (B4) — subir de B4 para A4 aqui significaria migrar da trilha
  satélite temática para a trilha principal genérica, uma troca de aderência por estrato.
- Nenhuma aderência temática foi verificada contra o texto completo do CFP (apenas contra a
  página inicial/escopo do evento) — antes de submeter a qualquer um destes, ler o CFP completo.
- Orçamento de WebSearch da sessão de pesquisa esgotou parcialmente; a maior parte da checagem do
  cluster de mobilidade veio de WebFetch direto em URLs prováveis + DBLP como fonte secundária de
  histórico de edições (não WikiCFP, que ficou inacessível).

## sources

CAPES 2025 spreadsheet (local, user-provided): `~/Downloads/Computação_Classificação de Eventos
2025.xlsx`. Event primary sources: mobiquitous.eai-conferences.org/2026/ ; mswimconf.com ;
ntms-conf.org (→ntms.dnac.org) ; comsoc.org/conferences-events/ieee-vehicular-networking-
conference-2026 + ieee-itss.org/conf/vnc/ ; esann.org ; iwann.uma.es ; icmlc.org ;
sbrc.sbc.org.br/2026/ ; sbbd.org.br/2026/ ; complexnetworks.org ; epia2026.web.uma.pt . Secondary
(edition-history cross-check only): DBLP.
