## question

Which Qualis (CAPES, Área Computação) classification applies to the three coletânea articles'
venues (CBIC, CoUrb, MobiWac), for the Art. 21 §1 "qualidade mínima" proof? Deep-research workflow
(100 sub-agents, adversarial 3-vote verification), run 2026-07-20.

## findings

(1) CONFIRMED (3-0) — **CBIC = B4**. Primary source: CAPES "RELATÓRIO DA COMISSÃO DE QUALIS
EVENTOS", quadriênio 2017-2020, Área de Avaliação Computação (coord. Paulo Roberto Freire Cunha):
https://www.gov.br/capes/pt-br/centrais-de-conteudo/documentos/avaliacao/09012022_RELATORIOQUALISEVENTOS20172020COMPUTACAO.PDF
— exact row: "CBIC   Congresso Brasileiro de Inteligência Computacional   B4". Classified by
CAPES's own Computação (Ciência da Computação) area coordination, NOT by an Engineering/Automação
committee, despite CBIC being organized by ABRICOM/SBIC/SBA rather than SBC. CBIC does not appear
in SBC's own SOL digital library (consistent with non-SBC organizer) and the official CBIC 2025
proceedings page (sbia.org.br) makes no Qualis/CAPES mention — the classification is only
findable in the CAPES document itself, not on the event's own site.

(2) CONFIRMED (3-0) — **CoUrb = B4**. Same CAPES document, listed under "COURB / Workshop of
Urban Computing", positioned alphabetically between COSN (B4) and CP (A3) in a genuine tabular
index (not an isolated/spurious match).

(3) CONFIRMED (3-0 / 3-0) — **MobiWac = B2** (the best of the three). Same CAPES document: "MOBIWAC
ACM International Symposium on Mobility Management and Wireless Access   B2", neighboring
MobiSys=A1, MobiHoc=A2, MobileHCI=A2, MoCo=B1. MobiWac does not appear anywhere in SBC's SOL
ecosystem (expected — it's an international ACM workshop outside the SBC ecosystem), but that
doesn't block its own CAPES-Computação classification, which is what matters for Art. 21.

(4) MEDIUM CONFIDENCE — this 2017-2020 list is the most recent **nominal, complete** listing
findable for these three specific venues, but its declared scope is "artigos publicados nos anos
2017 e 2018" — a historical snapshot, not an auto-current 2025/2026 list. Since ~2019 CAPES
formally replaced the fixed "Lista Qualis" model (for Computação) with a "Qualis Referência"
computed from bibliometric percentiles (H5-index via Google Scholar Metrics, adjusted by SBC
Comissões Especiais: Top10-endorsed venues get +2 strata, Top20 get +1). There is evidence of a
newer "Qualis Eventos 2025" cycle live on the (legacy) Sucupira platform
(https://sucupira-legado.capes.gov.br/sucupira/public/consultas/coleta/qualisEventos/listaQualisEventos.xhtml),
but that page is a dynamic year/area dropdown search UI, not a static indexable list — this
research did **not** run the live per-venue query against it, so it is unconfirmed whether
CBIC/CoUrb/MobiWac appear identically in the 2025 cycle. Flagged as an open question, not
resolved.

(5) CONFIRMED (3-0) — **PPGCC Regimento Art. 21 §1 does not itself state a minimum Qualis
stratum.** Verbatim: "publicação ou aceite de, pelo menos, um artigo originado da sua pesquisa, em
um evento científico ou comprovação de submissão a periódico da área de Ciência da Computação, com
qualidade mínima definida em **resolução interna**, pela comissão coordenadora do programa, de
acordo com normas gerais da área de Computação estabelecidas pela CAPES." The referenced
"resolução interna" was NOT located in this research (same gap already flagged in
`norms_verification_2026-07-18.md` — the June/2024 defense checklist still says "Qualis A4 ou
superior", which may be stale relative to the July/2026 regimento). **So B4/B4/B2 cannot yet be
confirmed to satisfy Art. 21 mechanically — that depends on a document not found online; ask the
secretariat.**

(6) CONFIRMED (3-0) — CAPES's own 2019 methodology document states its event/journal
classification criteria are designed to evaluate **programs** in aggregate and are "em princípio,
inadequados para a avaliação individual de pesquisadores" — a usable argument if a committee
questions strict Qualis-as-individual-proof.

(7) CONFIRMED (3-0 / 3-0) — methodology confirms events without an H5-index AND without an SBC
Comissão Especial endorsement are simply left unclassified. Since all three venues DO appear
classified in the 2017-2020 report, that is itself evidence they cleared the H5/CE-SBC bar (not a
gap in the data).

## refuted (do not use)

- "CBIC is organized by SBIA, not ABRICOM" (0-3, from sbia.org.br — the site hosts CBIC 2025 but
  doesn't establish SBIA as organizer over ABRICOM/SBIC).
- "CoUrb doesn't appear separately in SOL's top-level conference index, presumably nested under
  the SBRC week" (0-3, from sol.sbc.org.br).
- "The fixed Lista Qualis concept no longer exists at all for Computação, full stop" (0-3 / 1-2,
  from pgcomp.ufba.br and ic.unicamp.br — contradicted by the same source noting CAPES itself
  released a Qualis Periódicos 2021-2024 AND a Qualis Eventos 2025).
- "MobiWac = Qualis B3" per aggregator myhuiban.com (1-2 refuted — unofficial, no CAPES/Sucupira
  link, no cited edition year; the official CAPES B2 above is authoritative over this).

## open questions

1. Does a PPGCC internal resolution (separate from the Regimento) exist that sets the actual
   minimum stratum for Art. 21, and do B4 (CBIC, CoUrb) / B2 (MobiWac) clear it? Not found online
   — **needs a direct question to ppgcc@ufv.br** (already flagged as the remaining Art. 21 action
   in `UFV_COMPLIANCE.md` §3/§7).
2. Do CBIC/CoUrb/MobiWac keep B4/B4/B2 (or change) in the live "Qualis Eventos 2025" Sucupira
   cycle? Would require running the dropdown query per venue, not just reading the static page.
3. Any documented PPGCC precedent for an interdisciplinary AI venue like CBIC (SBIC/ABRICOM/SBA,
   not SBC) counting toward an Art. 21 requirement phrased as "área de Ciência da Computação"?

## sources

Primary: CAPES Qualis Eventos 2017-2020 report (Computação) —
https://www.gov.br/capes/pt-br/centrais-de-conteudo/documentos/avaliacao/09012022_RELATORIOQUALISEVENTOS20172020COMPUTACAO.PDF
; CAPES 2019 methodology doc —
https://www.gov.br/capes/pt-br/centrais-de-conteudo/documentos/avaliacao/qualis_periodico_eventos_cientifico_Ciencia_Computacao.pdf
; Sucupira legado Qualis Eventos search —
https://sucupira-legado.capes.gov.br/sucupira/public/consultas/coleta/qualisEventos/listaQualisEventos.xhtml
; PPGCC Regimento interno — https://ppgcc.ufv.br/regimento-interno/ ; SBC SOL conference index —
https://sol.sbc.org.br/index.php/anais/confs ; CBIC 2025 official page —
https://sbia.org.br/eventos/cbic_2025/ . Secondary (lower weight): pgcomp.ufba.br, ic.unicamp.br,
nemo.inf.ufes.br (methodology corroboration only).
