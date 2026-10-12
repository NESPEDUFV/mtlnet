# Incidente — dois agentes, uma árvore, commits cruzados nos dois sentidos

**2026-08-21.** Sem perda científica. O **código está correto e a suíte verde**; o que ficou errado é
o **registro**: duas mensagens de commit descrevem conteúdo que não está nelas.

## O que aconteceu

`mtlcheck` e `mtlcheck-2` trabalharam na **mesma árvore de trabalho**, em paralelo, e ambos usaram
`git add -A`. Cada um varreu as mudanças não-commitadas do outro.

| commit | o que a mensagem diz | o que o diff contém |
|---|---|---|
| `84fc6c73` | `substrate/identity: digest() recusa dicionário sem chaves de identidade` — e a mensagem afirma explicitamente *"test_logger_bindings.py fica fora do commit"* | a mudança de `identity.py` **mais** o conserto de `cli.py:168` (do outro agente) **mais** o `test_logger_bindings.py` que a mensagem diz estar fora |
| `222877dc` | `cli: liga o logger em _run_check2hgi — NameError no caminho sem --shapefile` | **nenhuma linha de `cli.py`** — só o `.gitignore` e a remoção do teste, ambos meus |

O conserto de `cli.py` está no commit que diz falar de `identity.py`. A mensagem que anuncia o
conserto do `cli.py` não o contém.

## Por que não reescrevi a história

Rebase/amend numa árvore que outro agente está usando ativamente é como se cria perda de verdade.
O código está certo; o custo do erro é um leitor futuro procurar o conserto do `cli.py` no commit
errado. Este arquivo é o ponteiro que resolve isso, e é mais barato que o risco.

## A parte que dói

**É a segunda vez nesta sessão.** A primeira foi `a85a42f4`, em que um `git add -A` capturou seis
mutações de auditoria numa janela de nove minutos. E o `BEST_PRACTICES_NESPEDGPU.md` §9 — escrito
**nesta mesma manhã**, por mim — diz literalmente: *"se houver qualquer agente ou sessão ativa na
mesma árvore, `git add -A` captura trabalho alheio em voo… commite por caminho explícito, e leia o
`git diff --stat` antes."*

Escrever o aviso não impediu o erro. Isso agora tem três instâncias no mesmo dia — o aviso do
`save_predictions` escrito duas horas antes da omissão, o teste de sanidade que não podia falhar no
caso que importava, e este. **O padrão não é falta de conhecimento; é que conhecimento não age. Só a
verificação age.**

## A regra, para valer de agora em diante

Numa árvore compartilhada por mais de um agente:

1. **Nunca `git add -A`.** Sempre `git add -- <caminho> [<caminho>…]`.
2. **`git diff --cached --stat` antes de todo commit**, e a pergunta é: *isto é exatamente o que eu
   pretendia commitar, e nada mais?*
3. Se o `--stat` mostrar arquivo que tu não tocaste, **para** — é trabalho de outro agente em voo.

Ver também: [`INCIDENT_2026-08-19_commit.md`](INCIDENT_2026-08-19_commit.md), o primeiro caso.
