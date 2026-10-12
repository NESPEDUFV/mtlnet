"""§1 — o canário de vazamento. Ele dispara? E ele estava desligado?"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mtlcheck.eval import leak_canary


def _rows(n=200, fold=0, *, ood_ranks=None):
    """Linhas de predição. `ood_ranks` põe rótulos FORA do treino nos ranks dados."""
    y = np.arange(n) % 50
    rank = np.full(n, 30)                       # ninguém acerta no top-10 por padrão
    if ood_ranks:
        for i, r in ood_ranks.items():
            rank[i] = r
    return pd.DataFrame({"fold": fold, "task": "reg", "userid": np.arange(n) % 20,
                         "y_true": y, "rank_of_true": rank})


def test_the_canary_fires_when_untrained_labels_rank_in_the_top_k() -> None:
    """O contrapeso que dá sentido a um resultado zero.

    Sem este teste, "ood_hit_rate = 0 em 60 folds" é indistinguível de um canário que nunca poderia
    disparar — que era exatamente o estado até 2026-08-19: `ood_diagnostics` tinha um chamador, o
    próprio teste, e o caminho do `compare` zerava os arrays de OOD na origem.
    """
    # rótulos 40..49 fora do treino; alguns deles acertam no top-10
    frame = _rows(ood_ranks={i: 3 for i in range(160, 200)})
    meta = {"arm": "reg", "state": "x", "train_labels": {"reg/0": list(range(40))}}
    canarios = leak_canary.per_fold(frame, meta)

    assert canarios, "nenhum canário avaliado"
    assert canarios[0].ood_fraction > 0, "a fixture não produziu linhas fora de distribuição"
    assert canarios[0].fired, "rótulos nunca treinados ranqueando no top-10 TÊM de disparar"
    with pytest.raises(leak_canary.LeakCanaryFired, match="§1"):
        leak_canary.assert_no_leak(canarios)


def test_the_canary_stays_quiet_when_untrained_labels_never_rank() -> None:
    frame = _rows()                                    # todos no rank 30, fora do top-10
    meta = {"arm": "reg", "state": "x", "train_labels": {"reg/0": list(range(40))}}
    canarios = leak_canary.per_fold(frame, meta)
    assert canarios[0].ood_fraction > 0 and not canarios[0].fired
    leak_canary.assert_no_leak(canarios)               # não levanta


def test_it_is_evaluated_PER_FOLD_not_pooled() -> None:
    """Agrupar os folds sob a UNIÃO dos rótulos de treino SUBESTIMA o OOD.

    Um rótulo ausente do fold 0 mas presente no fold 1 deixaria de contar como fora de distribuição
    no fold 0 — e é justamente por isso que os `train_labels` são bancados por (tarefa, fold).
    """
    f0 = _rows(fold=0, ood_ranks={i: 2 for i in range(160, 200)})
    f1 = _rows(fold=1)
    frame = pd.concat([f0, f1], ignore_index=True)
    meta = {"arm": "reg", "state": "x",
            "train_labels": {"reg/0": list(range(40)), "reg/1": list(range(50))}}

    canarios = leak_canary.per_fold(frame, meta)
    assert len(canarios) == 2
    assert canarios[0].fired and not canarios[1].fired, (
        "o fold 0 vaza e o 1 não; avaliar sob a união dos rótulos apagaria a diferença")


def test_a_fold_without_banked_labels_is_skipped_loudly(caplog) -> None:
    """Ausente avisa e não avalia — nunca assume 'sem OOD'."""
    import logging

    frame = _rows()
    with caplog.at_level(logging.WARNING):
        canarios = leak_canary.per_fold(frame, {"arm": "reg", "state": "x", "train_labels": {}})
    assert canarios == []
    assert "train_labels" in caplog.text


def test_exploratory_reading_degrades_to_a_warning() -> None:
    frame = _rows(ood_ranks={i: 1 for i in range(160, 200)})
    meta = {"arm": "reg", "state": "x", "train_labels": {"reg/0": list(range(40))}}
    canarios = leak_canary.per_fold(frame, meta)
    assert canarios[0].fired
    leak_canary.assert_no_leak(canarios, confirmatory=False)   # avisa, não levanta


def test_sem_rotulos_de_treino_o_canario_recusa_em_vez_de_pular() -> None:
    """§1 diz "fails the run", e um fold sem `train_labels` não é canário que passou — é canário
    que não foi ligado. Sob leitura confirmatória um aviso em log é indistinguível de um zero real.
    """
    with pytest.raises(leak_canary.LeakCanaryFired, match="NÃO PODE ser avaliado"):
        leak_canary.per_fold(_rows(), {"arm": "reg", "state": "alabama"}, strict=True)


def test_fora_do_estrito_ele_segue_avisando(caplog) -> None:
    with caplog.at_level("WARNING"):
        assert leak_canary.per_fold(_rows(), {"arm": "reg", "state": "alabama"}) == []
    assert "train_labels" in caplog.text
