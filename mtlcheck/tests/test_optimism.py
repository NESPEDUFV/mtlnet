"""§8a — os três estimadores, a quarentena, e a agregação que não pode ser afrouxada."""

from __future__ import annotations

from pathlib import Path

import pytest

from mtlcheck.eval import optimism as opt


def _curve():
    return {1: 0.90, 5: 0.30, 12: 0.34, 20: 0.31, 30: 0.33}


def test_a1_is_never_below_b1() -> None:
    """a1 é um máximo sobre a MESMA curva de onde b1 sai, então a1 >= b1 por construção.

    Se este teste falhar, o otimismo de seleção saiu negativo — o que só é possível se a1 e b1
    vierem de trajetórias diferentes, que é exatamente o que o §8a existe para impedir.
    """
    for inner in (5, 12, 20, 30):
        e = opt.estimators_from_curve(_curve(), inner_epoch=inner, joint_epoch=30, state="al",
                                      task="cat", fold=0, seed=0, stream="inner_val")
        assert e.a1 >= e.b1
        assert e.selection_optimism >= 0


def test_epochs_below_the_cut_cannot_win_a1() -> None:
    """A época 1 vale 0,90 e é a maior da curva; o corte do §8a a torna inelegível.

    Sem o corte, o máximo cairia na rampa do OneCycle — um ponto que nenhuma regra de seleção real
    escolheria — e o otimismo medido seria enorme por um motivo que não é seleção.
    """
    e = opt.estimators_from_curve(_curve(), inner_epoch=20, joint_epoch=30, state="al", task="cat",
                                  fold=0, seed=0, stream="inner_val")
    assert e.a1_epoch == 12 and e.a1 == 0.34, "a época 1 (0,90) não pode vencer"


def test_b2_uses_the_joint_selector_epoch_not_the_task_epoch() -> None:
    """A diferença entre b1 e b2 É a pergunta. Se b2 usasse a época da tarefa, b1 − b2 seria zero
    por construção e o custo de checkpoint único ficaria invisível."""
    e = opt.estimators_from_curve(_curve(), inner_epoch=12, joint_epoch=20, state="al", task="cat",
                                  fold=0, seed=0, stream="inner_val")
    assert e.b1 == 0.34 and e.b2 == 0.31
    assert e.single_checkpoint_cost == pytest.approx(0.03)


def test_a_missing_retained_epoch_is_refused_not_approximated() -> None:
    """Se a época escolhida não foi retida, a1 e b1 sairiam de trajetórias diferentes.

    Aproximar pela época retida mais próxima seria silencioso e destruiria o cancelamento de
    variância que é a razão de os três serem co-registrados.
    """
    with pytest.raises(ValueError, match="não foi retida|não foi retido|retida"):
        opt.estimators_from_curve(_curve(), inner_epoch=17, joint_epoch=30, state="al", task="cat",
                                  fold=0, seed=0, stream="inner_val")


def test_the_sink_may_not_live_inside_the_rundir(tmp_path) -> None:
    run = tmp_path / "runs" / "estudo"
    run.mkdir(parents=True)
    with pytest.raises(opt.QuarantineViolated, match="dentro do rundir"):
        opt.assert_quarantine([], expected_seeds=0, expected_folds=0,
                              sink=run / "otimismo.jsonl", rundir_root=run)


def test_a_partial_state_is_refused(tmp_path) -> None:
    """A recusa que impede a utilidade mais errada: rodar no meio de um estudo para dar uma olhada."""
    run = tmp_path / "runs"; run.mkdir()
    cells = [Path(f"c{i}") for i in range(7)]
    with pytest.raises(opt.QuarantineViolated, match="antes do estado estar completo"):
        opt.assert_quarantine(cells, expected_seeds=4, expected_folds=5,
                              sink=tmp_path / "sink.jsonl", rundir_root=run)


def test_a_complete_state_passes(tmp_path) -> None:
    """O contrapeso: sem ele, uma implementação que recusa sempre passaria nos dois testes acima."""
    run = tmp_path / "runs"; run.mkdir()
    cells = [Path(f"c{i}") for i in range(20)]
    opt.assert_quarantine(cells, expected_seeds=4, expected_folds=5,
                          sink=tmp_path / "sink.jsonl", rundir_root=run)


def test_seeds_are_averaged_within_fold_before_the_stderr() -> None:
    """n = 5 folds, NÃO 20 células.

    Tratar semente e fold como réplicas independentes divide o erro-padrão por ~2 e produz uma
    decisão confiante sobre uma diferença que os dados não sustentam. O §8a especifica a ordem.
    """
    rows = [
        opt.Estimators(state="al", task="cat", fold=f, seed=s, a1=0.5 + 0.01 * s, b1=0.5,
                       b2=0.49, a1_epoch=10, b1_epoch=20, b2_epoch=30, stream="inner_val")
        for f in range(5) for s in range(4)
    ]
    summary = opt.summarise(rows)["cat"]
    assert summary["n_folds"] == 5, "o n tem de ser folds, não células"
    # Todos os folds têm a mesma média entre sementes, então o desvio entre folds é zero.
    assert summary["selection_optimism"]["stderr"] == pytest.approx(0.0, abs=1e-12)


def test_the_two_differences_are_reported_separately() -> None:
    rows = [opt.Estimators(state="al", task="cat", fold=f, seed=0, a1=0.55, b1=0.50, b2=0.48,
                           a1_epoch=10, b1_epoch=20, b2_epoch=30, stream="inner_val")
            for f in range(5)]
    summary = opt.summarise(rows)["cat"]
    assert summary["selection_optimism"]["mean"] == pytest.approx(0.05)
    assert summary["single_checkpoint_cost"]["mean"] == pytest.approx(0.02)
    assert "total" not in summary and "combined" not in summary, "as duas NÃO se somam"


def test_the_sink_is_append_only(tmp_path) -> None:
    sink = tmp_path / "otimismo.jsonl"
    opt.append_to_sink(sink, {"passagem": 1})
    opt.append_to_sink(sink, {"passagem": 2})
    assert len(sink.read_text().strip().splitlines()) == 2, "a segunda passagem sobrescreveu a primeira"
