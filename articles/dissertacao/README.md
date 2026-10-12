# Dissertação de Mestrado — Vitor Hugo Oliveira

**Multitask Learning for Point-of-Interest Classification and Prediction Tasks:
The Role of the Check-in-Level Representation**
PPGCC/UFV · formato coletânea de artigos (CBIC → CoUrb → MobiWac)
**Defendida e aprovada em 28/08/2026.**

---

> ## ⚠ Antes de qualquer coisa: [`VEREDITOS.md`](VEREDITOS.md)
>
> Questões **já encerradas com prova** (o vazamento do Cap. 3, que fonte de números vale, o que
> não se apaga, que números estão invalidados). Responde por **pergunta**, não por documento.
> Se a sua dúvida está lá, não se reabre.
>
> **Ordem de leitura:** `VEREDITOS.md` → `CLAUDE.md` §0 → os documentos vivos →
> `src_utils/_history/` **só se pedirem**. Toda pasta com `_` à frente é **bastidor**: as rondas de
> revisão fechadas vivem em `src_utils/_history/`, e valem como proveniência, nunca como fonte de um facto.

---

## Onde está cada coisa

| quero… | está em |
|---|---|
| **o texto entregue** | `src/` — `content.tex` monta `src/chapters/` |
| **o PDF do depósito** | `src/build/main_academico.pdf` (`make academico`; não rastreado, é o corpo que se anexa no AcademicoPG) |
| **o build corrente do texto** | `src/dissertacao.pdf` — cópia de conveniência que o `make defense` produz; **não** é o que se deposita (corrigido 2026-10-02: esta linha dizia que era) |
| **o PDF que a banca recebeu** | `src/banca.pdf` — **congelado, nunca rebuildar** (ver abaixo) |
| **as figuras do volume** | `src/figures/` (`.png`, `.tex`, `courb/`, `mobiwac/`) |
| **as tabelas de resultados** | `src/tables/` |
| **a bibliografia** | `src/references.bib` |
| **o suplemento** (material extra) | `wrapup/material_extra/` → `main_extra.pdf` |
| **os slides da defesa** | `presentation/slides/` — o deck congelado é `slide_final.pdf` |
| **as chapas de arquitetura** (TikZ) | `presentation/figures/` — fontes em `src/`, PDFs em `plates/`, método no README de lá |
| **o roteiro da fala** | `presentation/SPEECH.pdf`, gerado de `presentation/SLIDES.md` |
| **os bastidores da defesa** | `presentation/_preparacao/` — o plano, as decisões do autor (AUT-1…36), os handoffs |
| **as notas de pesquisa e a proveniência dos números** | `science/` |
| **as ferramentas de conferência** | `src_utils/` — `check.sh` é a porta de entrada; `evidence/` guarda os relatórios de proveniência que o texto cita |
| **o que ficou por fazer** | `wrapup/open_points/LACUNAS.md` (o registo vivo); o inventário da reorganização pós-defesa em `wrapup/ACHADOS.md` |

Fora do caminho principal: `reviewers/` (19 perfis de revisão usados na redação),
`archive/` e `reviewers/research/` (as notas de pesquisa que fundamentam as personas). As dissertações de exemplo
usadas como referência de qualidade não estão no repositório.

---

## O que foi decidido — o resultado, em quatro linhas

A pergunta: **MTL ajuda predição de POI (próxima categoria + próxima região), e do que depende
a resposta?** A resposta entregue, medida com CV por usuário disjunto, n=20, correção de Holm:

- **next-category:** o modelo conjunto **supera o dedicado em Florida** (+0,19, Holm *p* 0,011).
  As outras cinco diferenças são **não resolvidas** — nunca "em todos os datasets";
- **next-region:** **não-inferior nos seis** (TOST, margem registrada de 2 pontos), com
  **Texas +1,21** e **California +1,06** superando;
- **a representação é o fator dominante:** trocar embedding place-level por check-in-level move
  mais que qualquer mudança de arquitetura — **+0,23 a +2,81** macro-F1 (o +6,29 de Istambul não era
  pareado; o par corrido a 2026-10-01 dá +2,81, `docs/results/closing_data/v18/istanbul_pair/`);
- o arco é uma **trilha de correção**, não três artigos grampeados: resultado negativo publicado
  (CBIC) → diagnóstico (CoUrb) → resolução (MobiWac).

> 🛑 **Circula pelo repositório uma escada de veredito SUPERADA** — *"category everywhere,
> region at four of six"* e *"+28…+40 macro-F1"*. **Não é o resultado entregue.** O `NORTH_STAR.md`
> abre com um banner que aponta essas frases **por conteúdo** e marca cada ocorrência com
> `[SUPERADO 2026-08-20]`. Não copiar nenhuma delas para prosa nova (ver `wrapup/ACHADOS.md §A4`).
> Fonte do número entregue: `src/tables/mobiwac/results.tex` e `wrapup/evidence/ladder_recompute.json`.

---

## Cinco coisas que quem chega precisa de saber antes de mexer

1. **`src/banca.pdf` não reproduz do `src/` — de propósito.** É o registo congelado do que a banca
   recebeu (md5 `5be69d1b…`). O build corrente é o `src/dissertacao.pdf`, e o corpo do depósito é o
   `src/build/main_academico.pdf`. Quem os comparar sem saber isto vai reportar um defeito que não
   existe. (Até 2026-10-02 esta linha dava ao `dissertacao.pdf` o md5 `d7e85bb7…`, que já não era o
   ficheiro, e chamava-lhe o PDF do depósito. O md5 saiu: sem `SOURCE_DATE_EPOCH` cada rebuild o muda,
   e o conteúdo compara-se por `pdftotext`.)

2. **Um `make` pelado sobrescreve o `dissertacao.pdf`.** Cinco alvos copiam para ele:
   `defense`, `all`, `all3`, `fast`/`fast-defense`, `fast3`. Para conferir sem buildar: `make check`.

3. **`src_utils/_history/_round6` … `_round14` parecem pastas de trabalho velhas e não são.**
   `check.sh` **executa** `_history/_round9/35_wave_a_render_check.py`, e `check_audit_claims.py` lê os
   `.md` do `_round9` **como dados** (uma tabela de regexes). Apagar um deles faz o gate falhar.

4. **Os `.tex` do volume estão cheios de comentários de proveniência** que citam os valores
   superados **verbatim**. Qualquer `grep` sem filtro sobre-reporta. Filtrar o ficheiro, não a
   saída: `grep -v '^[[:space:]]*%' ficheiro.tex | grep <padrão>`.

5. **`git check-ignore -v` mente em caminhos já rastreados** (consulta o índice). Para saber se
   uma regra apanha um caminho, use `git check-ignore --no-index -v <path>`; para ver o que existe
   no disco e o git não mostra, `git status --ignored`.

---

## Reconstruir

```bash
cd src && . ../src_utils/texenv.sh && ../src_utils/latexbuild.sh main main.tex   # builda build/ SEM tocar no dissertacao.pdf; o texenv.sh e obrigatorio (o Makefile carrega-o, a chamada directa nao)
cd src && make check                                 # a esteira dos 25 portões
cd presentation/figures && ./build.sh                # regenera as chapas TikZ
cd presentation/slides && make                       # regenera o main.pdf que as canárias leem
```

⚠ **Buildar primeiro, conferir depois.** As saídas de build foram apagadas na limpeza de 28/08 (são
derivadas). Sem `build/`, seis portões saltam — e dizem-no alto (`SKIP: src/build/main.pdf not
built`), mas um portão que não corre não é um portão que passa.

⚠ **`make check` sai com código ≠ 0 e imprime verde na mesma. Ler o exit code, não a saída.**
E **nunca um `make` pelado**: cinco alvos sobrescrevem o `dissertacao.pdf`. O
`latexbuild.sh` acima builda sem copiar.

O `presentation/Makefile.speech` **só compila o `SPEECH.tex` que já existe** — não chama os dois
extractores (`build_speech_1_extract.py`, `build_speech_2_emit.py`). Ele imprime `OK` na mesma.
Para regenerar o roteiro a partir do `SLIDES.md`, correr os extractores primeiro.
