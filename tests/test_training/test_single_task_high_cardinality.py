"""`train_single_task` must not materialise the full [N, C] logit at region cardinality.

The val loop used to `torch.cat` every batch's logits unconditionally, with no size guard of any
kind. At category cardinality (C=7) that is nothing. At REGION cardinality it is the ~20 GB tensor
that already forced the CPU offload in p1 and the chunked path in mtl_eval (texas C=6553,
california C=8501) — an STL region run routed here would simply OOM, and nothing in the code said
so. The runner now streams above the hand-rolled cutoff.

What these tests pin:
  * the streamed branch produces the SAME metrics as the full-logit branch (the cutoff is an
    implementation detail, not a change in what is reported);
  * the low-cardinality path is untouched, since every caller today is C=7 and its numbers are
    banked;
  * the streamed branch never builds the [N, C] buffer — asserted by watching `torch.cat`, not by
    reading the source, because "I removed the cat" is exactly the kind of claim that should be
    checked mechanically.
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from tracking.metrics import StreamingClsMetrics
from training.runners._single_task_train import train_single_task


class _Tiny(nn.Module):
    def __init__(self, n_in, n_out):
        super().__init__()
        self.fc = nn.Linear(n_in, n_out)

    def forward(self, x):
        return self.fc(x)


class _Hist:
    """Minimal FoldHistory stand-in: records what the runner logs, asserts nothing itself.

    Shapes match the real call sites in `_single_task_train` — `log_train(task_name, **metrics)`,
    `task(name).best.best_value`, `task(name).val.best('f1')`, `timer.timer()`.
    """

    class _Best:
        best_value = 0.0

    class _Val:
        def __init__(self, outer):
            self._outer = outer

        def best(self, key):
            vals = [e.get(key, 0.0) for e in self._outer.val]
            return (0, max(vals) if vals else 0.0)

    class _Timer:
        def timer(self):
            return 0.0

    def __init__(self):
        self.train, self.val = [], []
        self.timer = _Hist._Timer()

    def log_train(self, _task, **kw):
        self.train.append(kw)

    def log_val(self, _task, **kw):
        kw.pop("model_state", None)
        self.val.append(kw)

    def task(self, _name):
        outer = self
        return type("T", (), {"best": _Hist._Best(), "val": _Hist._Val(outer)})()

    def __getattr__(self, _):            # any other hook the runner may call
        return lambda *a, **k: None


def _run(n_classes, seed=0, epochs=2, n=256, d=8):
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed)
    xt, yt = torch.randn(n, d, generator=g), torch.randint(0, n_classes, (n,), generator=g)
    xv, yv = torch.randn(n, d, generator=g), torch.randint(0, n_classes, (n,), generator=g)
    torch.manual_seed(seed)                       # model init must not depend on the data draw
    model = _Tiny(d, n_classes)
    hist = _Hist()
    train_single_task(
        model=model,
        train_loader=DataLoader(TensorDataset(xt, yt), batch_size=64),
        val_loader=DataLoader(TensorDataset(xv, yv), batch_size=64),
        criterion=nn.CrossEntropyLoss(),
        optimizer=torch.optim.SGD(model.parameters(), lr=0.01),
        scheduler=None,
        device=torch.device("cpu"),
        history=hist,
        task_name="next",
        num_classes=n_classes,
        epochs=epochs,
        compute_train_f1=True,
    )
    return hist


def _metrics(entries):
    keep = ("f1", "accuracy", "top3_acc", "top5_acc", "mrr", "ndcg_3", "ndcg_5")
    return [{k: round(float(v), 12) for k, v in e.items() if k in keep and isinstance(v, (int, float))}
            for e in entries]


def test_streamed_and_full_agree_across_the_cutoff(monkeypatch):
    """Same data, same seed, both branches — the cutoff must not move the numbers.

    Forcing `should_stream` False reproduces the pre-change full-logit path exactly, so this is a
    genuine A/B of the branch rather than a re-run of one side.
    """
    real_gate = StreamingClsMetrics.should_stream   # captured before the patch below
    streamed = _run(300)
    monkeypatch.setattr(StreamingClsMetrics, "should_stream", staticmethod(lambda n: False))
    full = _run(300)
    assert _metrics(streamed.val) == _metrics(full.val)
    assert _metrics(streamed.train) == _metrics(full.train)
    assert real_gate(300) is True                  # the real gate really is on at this C


def test_low_cardinality_still_takes_the_full_path(monkeypatch):
    """C=7 is every caller today and its numbers are banked; it must not start streaming."""
    seen = []
    real = StreamingClsMetrics.should_stream

    def spy(n):
        seen.append(n)
        return real(n)

    monkeypatch.setattr(StreamingClsMetrics, "should_stream", staticmethod(spy))
    _run(7, epochs=1)
    assert seen and all(n == 7 for n in seen)
    assert real(7) is False


def test_streamed_branch_never_cats_the_full_logit(monkeypatch):
    """The point of the change is the absent [N, C] buffer, so assert on the absence.

    Any `torch.cat` whose operands are 2-D and as wide as the class count is the buffer this
    change exists to remove. Per-row accumulators are 1-D, so they cannot trip this.
    """
    n_classes = 300
    offenders = []
    real_cat = torch.cat

    def watched(tensors, *a, **kw):
        seq = list(tensors)
        if seq and getattr(seq[0], "ndim", 0) == 2 and seq[0].shape[-1] >= n_classes:
            offenders.append(tuple(seq[0].shape))
        return real_cat(seq, *a, **kw)

    monkeypatch.setattr(torch, "cat", watched)
    _run(n_classes, epochs=1)
    assert offenders == [], f"full [N, C] logit was still materialised: {offenders}"
