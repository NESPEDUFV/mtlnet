# Ledger da revisão adversarial — fase 1

Revisor: agente Fable 5, read-only, verificando `SYSTEM_MAP.md` e `ARCHITECTURE.md` (revisão 1) contra
o código. Disposição de cada item. `A` = aceito e aplicado · `R` = registrado sem mudança de plano ·
`P` = pendente para o autor.

## Blockers

| # | Achado | Disp. | Onde entrou |
|---|---|---|---|
| B1 | Pareamento cruzado do joint é **aleatório no treino** e alinhado na validação; `--aligned-pairing` é opt-in default-off e o driver nunca o passa; a implementação "limpa" natural viraria alinhada, mudando a distribuição de treino do tronco cross-attn, num gate (G0.1) ainda aberto | A | `SYSTEM_MAP` S13; `ARCHITECTURE` §3.1, §4.5, §8 |
| B2 | O rebuild não reproduz o v18 como estava escopado: (i) `placeid_to_idx`/`poi_to_region` vêm do engine canônico, não dos substratos reconstruídos; (ii) o espaço de linhas é copiado verbatim do `check2hgi_dk_ovl`; (iii) os dois builders dependem de artefatos HGI/POI2Vec que o §6 mandava apagar | A | `ARCHITECTURE` §1.1; `SYSTEM_MAP` §6.1 |
| B3 | O relato do incidente de precisão e as âncoras numéricas misturavam a wave superseded com a final: o vazamento **já foi corrigido** no driver que produziu o §1.1, o Δcat de TX foi re-medido em +0,020, o `n` de TX/CA vale para categoria e não para região, e os p-valores são anti-conservadores por construção | A | `SYSTEM_MAP` §5 (correção), D2, D6, D7 |

## Highs

| # | Achado | Disp. | Onde entrou |
|---|---|---|---|
| H1 | E7 ("mesma seed → mesmos logits") é impossível num rewrite clean-room | A | `ARCHITECTURE` E7 → transplante de checkpoint |
| H2 | Passam por C1-C8 sem serem notados: clipping, contagem de passos do scheduler, camada de estatística, e C7 sem âncora | A | S14, S15, S16; `ARCHITECTURE` §3.7, E11, §4.5, C7 |
| H3 | D4 é real, unilateral (só infla a coluna dedicada), ~0,01-0,06 pp — mesma ordem dos vereditos pequenos | A | `SYSTEM_MAP` D4; coluna dupla obrigatória |
| H4 | Sete itens da lista de obsoletos são carga estrutural (registry de losses, `next_stan` como classe base, `CATEGORIES_MAP` como rótulo de estratificação, FUSION no `paths.py`, guard de versão do torch, deps HGI/POI2Vec) | A | `SYSTEM_MAP` §6.1 |
| H5 | A história do prior inerte estava desatualizada nos dois sentidos: a carga do `log_T` já é pulada por default, e o skip do gather já existe em `aab23985` | A | `SYSTEM_MAP` §2.3, D5; `ARCHITECTURE` §3.3 |
| H6 | Faltavam do inventário as env vars que decidem mais ciência (`MTL_SKIP_INERT_PRIOR`, `REGION_EMB_ENGINE`, ...) e um auto-switch que nem é env var (`_auto_fp32_for_large_c`) | A | `SYSTEM_MAP` §5; `ARCHITECTURE` §3.2 |
| H7 | O braço τ=0 do lever de logit-adjust **não é CE pura** — cai em CE balanceada por pesos | A | `ARCHITECTURE` C3 |

## Mediums e nits aplicados

- **M1** weight decay por família: cat 0,01 · reg 0,01 · joint 0,05 (eu tinha escrito 0,05 para o `src`).
- **M2** a família de categoria **não** usa early stopping no v18 (`patience=-1`).
- **M3** C1 ancorado por receita: 28,23 é o harness da auditoria, 30,77 é o board.
- **M4** `n_regions = max+1` sobre a tabela completa é contrato; E3 testa a regra.
- **M5** o nível 1 precisa dos parquets do A40 localmente; virou primeira tarefa da fase 8.
- **M6** o reseed por fold afeta init/shuffle e **não** o split (confirmado); colisão `seed+fold` entre seeds registrada.
- **M7** a quarta coluna de tempo é `gap == 0`, não `is_first_visit`; escopo real do forward-only (D8).
- **M8** o certificado de ambiguidade e a semântica `strict` são portados como unidade.
- **Nits** faixa v17 corrigida para +5,34…+9,40; direção da frase do vazamento; `MTL_CHUNK_VAL_METRIC` hoje inerte; invariante de padding estritamente posterior.

## Registrados, sem mudança de plano

- **M9** memos de future work ainda não lidos, listados no §7 do `ARCHITECTURE` como leitura obrigatória antes da fase 6.
- **Nit** duas cópias byte-idênticas de `score_joint_best.py` no repo antigo — some por construção.
- **Nit** meta de ~3 500 linhas é aspiração, não gate.

## Resolvidas pelo autor (2026-08-12)

| # | Questão | Decisão |
|---|---|---|
| P1 | **Georgia** — descartar ou manter? | **Descartada.** Os 6 datasets são AL, AZ, IST, FL, CA, TX. Registrado como perda deliberada de cobertura em relação à matriz pré-v18 |
| P2 | **C7 sem âncora** — a lane joint-best do v18 está vazia | **Popular a lane.** As execuções do gate calculam e gravam as duas convenções, e C7 passa a ter limiar de verdade. Custo é re-scoring em CPU |
