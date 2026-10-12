"""Onde vive o sistema antigo, contra o qual os testes de equivalência comparam.

Era um caminho absoluto fixo repetido em onze arquivos — `/Users/...`, que só existia na máquina
do autor. Fora dela os testes pulavam por "artefato ausente": o desfecho certo pelo motivo errado,
e um caminho pessoal em arquivo publicado.

A ordem de resolução:

1. **`$MTLCHECK_OLD_REPO`**, para apontar explicitamente;
2. **a raiz deste repositório**, detectada pela assinatura do sistema antigo (`src/configs/paths.py`).
   É onde ele fica no repositório do departamento, com `mtlcheck/` como subpasta;
3. **um caminho inexistente** — e aí os testes pulam, que é o comportamento correto quando o
   sistema antigo não está ao lado.
"""

from __future__ import annotations

import os
from pathlib import Path


def old_repo() -> Path:
    if env := os.environ.get("MTLCHECK_OLD_REPO"):
        return Path(env)
    for pai in Path(__file__).resolve().parents:
        if (pai / "src" / "configs" / "paths.py").exists():
            return pai
    # NÃO devolva um caminho de desenvolvimento: estes arquivos são publicados.
    return Path("/nonexistent/old-repo")


#: Resolvido uma vez, na importação do módulo.
OLD_REPO = old_repo()
