# root_migration — promover o `mtlcheck/` a raiz do repositório

## A pergunta

O `mtlcheck/` vira a raiz. **O que fazer com os doze diretórios irmãos — migrar, arquivar ou
apagar — sem quebrar o que ainda depende deles?**

## Por que isto é um estudo e não uma faxina

Porque a dependência mais importante é **invisível**: a suíte de equivalência — a que prova que o
porte reproduz a referência — importa o repositório antigo por **caminho absoluto**. Apagá-lo não
deixa esses testes pulando; torna-os impossíveis de rodar para sempre.

## O layout de hoje

`/Users/vitor/Desktop/mestrado/mtlcheck` é um **worktree** do repositório antigo, na branch
`rewrite/mtlcheck`. Ele contém a árvore antiga inteira **mais** o pacote novo como subdiretório:

```
mestrado/
├── ingred/                    ← o repo antigo (PoiMtlNet), branch main
└── mtlcheck/                  ← worktree da MESMA branch-mãe, em rewrite/mtlcheck
    ├── articles/ data/ docs/ experiments/ notebooks/ output/
    ├── pipelines/ research/ results/ scripts/ src/ tests/     ← os doze irmãos
    └── mtlcheck/              ← o pacote novo, que vira a raiz
```

Tamanhos: `output/` 18 GB · `data/` 1,0 GB · `docs/` 207 MB · `articles/` 143 MB · `results/` 23 MB.

## O que depende de quê — verificado, não suposto

**1 · A suíte de equivalência importa o repo antigo por caminho absoluto.** Seis arquivos fixam
`/Users/vitor/Desktop/mestrado/ingred`:

```
tests/equivalence/test_assembly.py          test_e6_e8_model_loss.py
tests/equivalence/test_delaunay_equivalence.py   test_e9_metrics.py
tests/equivalence/test_e10_graph.py         test_joint_runner.py
```

Vinte e três testes já **pulam** no venv do projeto por falta de `cvxpy` e `pytorch_warmup`, que são
dependências da referência. **Decisão a tomar de propósito:** manter um checkout fixado da
referência em algum lugar, ou aceitar que a prova de equivalência vira histórica e congelar a
evidência dela.

**2 · A comparação com a dissertação precisa de `docs/studies/closing_data/v18/`.** O `status.json`,
o `PROVENANCE.md`, o `V18_RESULTS.md` e os drivers `run_*.sh` são o único registro do que o v18 de
fato rodou. A tarefa de avaliar contra a dissertação é justamente **atribuir diferenças** contra
aquilo — e a linha de base definitiva ainda não foi medida (ver `studies/improvements/`).

**3 · Já desacoplado, não re-acople.** Os dados primários (gowalla, massive steps, shapefiles,
check-ins) foram movidos em 19-08 para `/Users/vitor/Desktop/mestrado/data/` e os dois repositórios
os consomem por **symlink**. Antes, os 221 MB de shapefiles moravam dentro do repo antigo.

**4 · `output/` (18 GB) e `results/` são DERIVADOS** e gitignorados — são artefatos do engine antigo.
São o alvo mais tentador e o mais perigoso: contêm a única cópia de alguns substratos bancados que
a A40 não tem. **Confira antes de remover qualquer coisa.**

**5 · Os links `../../docs/...` do mtlcheck resolvem DENTRO do pacote** (são relativos a `studies/`),
não para a árvore antiga. Falso alarme, sem ação.

## Armadilhas

* **O worktree compartilha o `.git`** com o repo antigo. Apagar arquivos nesta branch não libera a
  linha principal, e vice-versa. Verifique o que uma promoção faz nos **dois** lados antes de mexer.
* **`artifacts/reference/` dentro do mtlcheck** guarda dados de comparação bancados. Não faz parte da
  árvore antiga e **tem de sobreviver**.
* **`git add -A` é perigoso aqui**, e o projeto já pagou por isso duas vezes em 19-08: um commit
  capturou seis mutações de auditoria em `src/`, e um `rsync --delete` malformado apagou a árvore de
  deploy na A40. Ver [`../porting_validation/INCIDENT_2026-08-19_commit.md`](../porting_validation/INCIDENT_2026-08-19_commit.md).

## Pré-requisito

⚠ **Não comece enquanto o estudo `improvements` estiver produzindo comparações.** Mexer na árvore que
a suíte de equivalência lê, no meio de uma campanha, é o incidente de 19-08 em escala maior.
