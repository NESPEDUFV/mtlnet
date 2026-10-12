"""T8 — the top-K distribution block, and the one thing that makes it lossless.

Four pre-registered consumers, written down before the field existed (docs/TELEMETRY_GUIDE.md §5.4): U5 error
distance, cross-arm error overlap, abstention curves, calibration. Anything else read off these
columns is reported as exploratory.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from mtlcheck.config import load_recipe
from mtlcheck.eval import predictions as P
from mtlcheck.train import metrics, runner
from conftest import extra_valido
from test_capture import _fold, _inputs, _spec


def test_the_logsumexp_makes_the_true_softmax_exactly_recoverable() -> None:
    """Storing K of C probabilities silently changes the denominator — unless the total is stored.

    `p_j = exp(logit_j - logsumexp)`. Without the logsumexp a reader renormalises over the retained
    entries and reports probabilities the model never produced; the error grows with how much mass
    lives outside the top K, which at 8,501 classes is exactly where it is least visible.
    """
    torch.manual_seed(0)
    logits = torch.randn(64, 1109) * 3
    targets = torch.randint(0, 1109, (64,))

    acc = metrics.StreamingMetrics(1109, top_k=(1, 5, 10), keep_top_k=20).update(logits, targets)
    block = acc.distribution()

    expected = torch.softmax(logits.float(), dim=-1)
    top = expected.gather(-1, block["top_ids"].long())
    # The reconstruction a consumer performs: exp of the stored LOG-probability.
    assert torch.allclose(block["top_log_probs"].float().exp(), top, rtol=2e-3, atol=0)
    assert torch.allclose(block["true_prob"], expected.gather(-1, targets[:, None]).squeeze(-1),
                          atol=1e-6)
    # The retained mass is a real fraction, not 1.0 — the point of storing the total.
    assert float(block["top_log_probs"].float().exp().sum(dim=-1).mean()) < 1.0


def test_log_probabilities_survive_the_tail_that_probabilities_do_not() -> None:
    """fp16 on a PROBABILITY destroys the tail; on a log-probability it does not.

    fp16 flushes anything below 2.98e-8 to exactly zero and quantises the whole subnormal band under
    6.1e-5 to 20-100% error. Storing the log instead costs the same two bytes and represents -17
    nats to ~0.008 absolute — under 1% on the probability — everywhere a model can reach.
    """
    tiny = torch.tensor([[0.0, -12.0, -18.0, -25.0, -34.0]])       # log-probs into the deep tail
    logits = tiny.clone()
    acc = metrics.StreamingMetrics(5, top_k=(1,), keep_top_k=5)
    acc.update(logits, torch.zeros(1, dtype=torch.long))
    stored = acc.distribution()["top_log_probs"].float()

    exact = torch.log_softmax(logits, dim=-1).gather(-1, acc.distribution()["top_ids"].long())
    assert torch.allclose(stored, exact, atol=0.02), "log-space keeps the tail"
    # The same values as fp16 PROBABILITIES: the last two entries would have been destroyed.
    as_prob = exact.exp().to(torch.float16).float()
    assert (as_prob[0, -1] == 0.0) and (exact.exp()[0, -1] > 0), "the defect this replaced"


def test_the_block_is_off_during_training_and_on_for_the_sealed_pass() -> None:
    """Retaining 20 probabilities per row per epoch would be 50x the cost for no consumer."""
    resolved = load_recipe("recipes/v18/cat.toml", state="alabama", seed=0, epochs=3,
                           batch_size=128)
    plain = runner.train_fold(resolved, _inputs(), _fold(sealed=True), _spec())
    assert plain.rows is None

    captured = runner.train_fold(resolved, _inputs(), _fold(sealed=True), _spec(),
                                 capture_predictions=True)
    assert set(P.DISTRIBUTION_COLUMNS) <= set(captured.rows)
    assert captured.rows["top_ids"].shape[1] == min(resolved.train.keep_top_k, 7)


def test_a_partial_block_is_refused_on_write_and_on_read(tmp_path) -> None:
    """The columns travel together or not at all — a reader that found top_ids without logsumexp
    would renormalise over the truncated set and never know."""
    n, k = 8, 4
    base = dict(state="alabama", arm="cat", task="cat", split_seed=0,
                partition_hash="abc123def456", model_seed=0, fold=0, selected_epoch=3,
                userid=np.arange(n), window_id=np.arange(n), y_true=np.zeros(n, dtype=np.int64),
                y_pred=np.zeros(n, dtype=np.int64), rank_of_true=np.ones(n, dtype=np.int64),
                train_labels=frozenset({0}), sealed=True)

    with pytest.raises(ValueError, match="distribution block is partial"):
        P.FoldPredictions(**base, top_ids=np.zeros((n, k), dtype=np.int32)).to_frame()

    whole = P.FoldPredictions(**base, top_ids=np.zeros((n, k), dtype=np.int32),
                              top_log_probs=np.full((n, k), -1.4, dtype=np.float16),
                              true_prob=np.full(n, 0.25, dtype=np.float32),
                              logsumexp=np.zeros(n, dtype=np.float32))
    P.write(tmp_path, [whole], extra=extra_valido(arm=whole.arm))
    loaded = P.read(tmp_path)
    assert loaded.meta["has_distribution"] is True and loaded.meta["top_k"] == {"cat": k}
    assert len(loaded.frame["top_ids"].iloc[0]) == k

    frame = loaded.frame.drop(columns=["logsumexp"])
    frame.to_parquet(tmp_path / "predictions.parquet", index=False)
    with pytest.raises(ValueError, match="partial distribution block"):
        P.read(tmp_path)


def test_rows_without_the_block_still_write(tmp_path) -> None:
    """The block is optional: cells banked before it exists must stay readable."""
    n = 4
    P.write(tmp_path, [P.FoldPredictions(
        state="alabama", arm="cat", task="cat", split_seed=0, partition_hash="abc123def456",
        model_seed=0, fold=0, selected_epoch=3, userid=np.arange(n), window_id=np.arange(n),
        y_true=np.zeros(n, dtype=np.int64), y_pred=np.zeros(n, dtype=np.int64),
        rank_of_true=np.ones(n, dtype=np.int64), train_labels=frozenset({0}), sealed=True)],
        extra=extra_valido())
    loaded = P.read(tmp_path)
    assert loaded.meta["has_distribution"] is False and loaded.meta["top_k"] == {}


def test_the_sidecar_reports_k_per_task_not_per_row_zero(tmp_path) -> None:
    """A joint cell holds both tasks; row 0 is always the 7-class head.

    Reading K from row 0 therefore advertised the category head's width for region rows carrying 20
    — and it described list position, not the file: reversing the list flipped the field. Two of the
    four pre-registered T8 consumers slice on this value, and an Acc@10 abstention curve is not even
    expressible at K=7.
    """
    def block(task: str, k: int, n: int = 6):
        return P.FoldPredictions(
            state="alabama", arm="joint", task=task, split_seed=0, partition_hash="abc123def456",
            model_seed=0, fold=0, selected_epoch=5, userid=np.arange(n), window_id=np.arange(n),
            y_true=np.zeros(n, dtype=np.int64), y_pred=np.zeros(n, dtype=np.int64),
            rank_of_true=np.ones(n, dtype=np.int64), train_labels=frozenset({0}), sealed=True,
            top_ids=np.zeros((n, k), dtype=np.int32),
            top_log_probs=np.full((n, k), -float(np.log(k)), dtype=np.float16),
            true_prob=np.full(n, 0.5, dtype=np.float32), logsumexp=np.zeros(n, dtype=np.float32))

    P.write(tmp_path, [block("cat", 7), block("reg", 20)], extra=extra_valido())
    assert P.read(tmp_path).meta["top_k"] == {"cat": 7, "reg": 20}
