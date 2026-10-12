"""Nenhuma função usa `log` sem que ele esteja ligado no escopo dela.

Por que este arquivo existe: `cli.py` liga o logger **por função** (`log = logging.getLogger(...)`
dentro de `_run_data`, `_run_train`, `_train_cell`) em vez de uma vez no módulo. O padrão funciona
até alguém escrever uma chamada nova numa função que não tem a linha — e aí é `NameError` em tempo
de execução, num ramo que talvez ninguém exercite.

Foi o que aconteceu em `cli.py:168`: a resolução automática de `--shapefile` logava o resultado e
`_run_check2hgi` não tinha logger próprio. O ramo só dispara quando `--shapefile` é omitido, então
passou por toda a suíte e pelos builds de Alabama e Arizona, e estourou na primeira vez que alguém
construiu um substrato sem passar o flag (Istambul, 2026-08-21).

Escopo, dito com honestidade: isto verifica **um nome**, `log`, não nomes indefinidos em geral. Um
`pyflakes`/`ruff` faria o caso geral, e nenhum dos dois está no ambiente — que é pinado de propósito.
Preferi cobrir a classe concreta que custou tempo a acrescentar dependência por conta própria.
"""
from __future__ import annotations

import ast
import pathlib

SRC = pathlib.Path(__file__).resolve().parents[1] / "src"


def _bound_inside(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """Nomes que a função liga: parâmetros, atribuições, imports, `except … as`."""
    names = {a.arg for a in fn.args.args + fn.args.kwonlyargs + fn.args.posonlyargs}
    if fn.args.vararg:
        names.add(fn.args.vararg.arg)
    if fn.args.kwarg:
        names.add(fn.args.kwarg.arg)
    for node in ast.walk(fn):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update((a.asname or a.name).split(".")[0] for a in node.names)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names.add(node.name)
    return names


def _module_level(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update((a.asname or a.name).split(".")[0] for a in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def unbound_log_uses(root: pathlib.Path = SRC) -> list[str]:
    """Cada `log.…` que roda num escopo onde `log` não existe. Público: o teste de mutação usa."""
    offences = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        at_module = _module_level(tree)
        for fn in [n for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            local = _bound_inside(fn)
            for node in ast.walk(fn):
                if (isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
                        and node.id == "log" and "log" not in local and "log" not in at_module):
                    offences.append(f"{path.relative_to(root.parent)}:{node.lineno} em {fn.name}()")
    return list(dict.fromkeys(offences))


def test_nenhuma_funcao_usa_log_sem_ligacao_no_escopo() -> None:
    offences = unbound_log_uses()
    assert not offences, (
        "`log` usado onde não está ligado — NameError em tempo de execução, num ramo que a suíte "
        f"pode não exercitar:\n  " + "\n  ".join(offences))


def test_a_varredura_realmente_olha_o_pacote() -> None:
    """Sem isto, um `root` errado deixaria o teste acima passar sem verificar nada."""
    assert len(list(SRC.rglob("*.py"))) > 40


def test_a_varredura_pega_o_caso_conhecido(tmp_path) -> None:
    """O `cli.py:168` real, reduzido: logger por função, e uma função sem a linha."""
    pkg = tmp_path / "p"
    pkg.mkdir()
    (pkg / "m.py").write_text(
        "import logging\n"
        "def com():\n"
        "    log = logging.getLogger('x')\n"
        "    log.info('ok')\n"
        "def sem():\n"
        "    log.info('estoura')\n", encoding="utf-8")
    found = unbound_log_uses(pkg)
    assert len(found) == 1 and "sem()" in found[0], found
