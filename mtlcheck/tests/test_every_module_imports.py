"""Todo módulo do pacote importa.

Trivial, e existe por um defeito real de 2026-08-19. Um campo com default foi inserido ANTES de um
campo sem default em `train/result.py`, o que quebra a dataclass no momento da definição. A
verificação feita na hora foi `import mtlcheck.cli`, que passou — porque o `cli` importa `result`
preguiçosamente, dentro da função. A suíte inteira também passou, o que revelou que nenhum teste
importava `result.py` no topo.

O erro só apareceu numa execução na GPU, depois de 8 minutos construindo um substrato.

Importar tudo custa menos de um segundo e fecha a classe inteira de erros de tempo de definição:
ordem de campos de dataclass, anotação inválida, ciclo de import, nome que não existe no escopo do
módulo.
"""

from __future__ import annotations

import importlib
import pkgutil

import pytest

import mtlcheck

MODULES = sorted(
    name for _, name, _ in pkgutil.walk_packages(mtlcheck.__path__, prefix="mtlcheck.")
)


def test_the_walk_found_the_package() -> None:
    """Sem isto, um `MODULES` vazio faria o teste abaixo passar sem importar nada."""
    assert len(MODULES) > 20, f"só {len(MODULES)} módulos encontrados — a varredura falhou"
    assert "mtlcheck.train.result" in MODULES


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name: str) -> None:
    importlib.import_module(name)
