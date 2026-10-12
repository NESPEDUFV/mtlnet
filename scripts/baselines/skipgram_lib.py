"""B2b skip-gram (word2vec, SGNS) over check-in POI sequences — library.

Reference
---------
Mikolov, Sutskever, Chen, Corrado, Dean. "Distributed Representations of
Words and Phrases and their Compositionality." NeurIPS 2013 (Skip-Gram with
Negative Sampling, SGNS). https://arxiv.org/abs/1310.4546

For POI/check-in sequences the recipe is the standard treatment (cf. DeepCity,
arXiv:1610.03676; CAPE; SG-CWARP): treat each user's chronologically ordered
``placeid`` trajectory as a "sentence", run skip-gram with negative sampling to
learn a 64-d vector per POI, then look the vector up per check-in (same POI =>
same vector). This is the B2b baseline column for the matched-head MTL board.

This module is a PURE library — no side effects on import, no shared-state edits.
It is consumed by ``scripts/baselines/build_b2b_skipgram_substrate.py``.

LEAK-SAFETY (HARD requirement)
------------------------------
``train_skipgram`` only ever sees the POI sequences whose ``userid`` is in the
fold's TRAIN-user set. The caller derives that set from
``StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)`` over
``load_next_data(state, CHECK2HGI)`` (bit-identical to the champion fold split).
POIs unseen in the train portion fall back to a deterministic zero vector at
emit time (documented deviation — a cold-start placeholder, never trained on
val users).
"""
from __future__ import annotations

import random
from collections import Counter
from typing import Dict, List, Sequence

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------------------------------------------------------------------------
# Skip-gram with negative sampling (SGNS), Mikolov et al. NeurIPS 2013.
# ---------------------------------------------------------------------------
class SkipGramNS(nn.Module):
    """Center/context embedding tables + SGNS loss.

    The emit vector for a token is its CENTER ("input") embedding row, the
    standard word2vec convention.
    """

    def __init__(self, vocab_size: int, dim: int = 64):
        super().__init__()
        self.center = nn.Embedding(vocab_size, dim)
        self.context = nn.Embedding(vocab_size, dim)
        # word2vec init: center ~ U(-0.5/dim, 0.5/dim), context = 0
        nn.init.uniform_(self.center.weight, -0.5 / dim, 0.5 / dim)
        nn.init.zeros_(self.context.weight)

    def forward(self, center_ids, pos_ids, neg_ids):
        # center_ids: [B], pos_ids: [B], neg_ids: [B, K]
        c = self.center(center_ids)               # [B, D]
        p = self.context(pos_ids)                 # [B, D]
        n = self.context(neg_ids)                 # [B, K, D]
        pos = F.logsigmoid((c * p).sum(-1))                        # [B]
        neg = F.logsigmoid(-(n * c.unsqueeze(1)).sum(-1)).sum(-1)  # [B]
        return -(pos + neg).mean()


def build_vocab(sequences: Sequence[Sequence[int]]) -> Dict[int, int]:
    """Map every POI id that appears in ``sequences`` to a contiguous index.

    Index 0 is RESERVED for the <unk>/cold-start token (gets the zero vector at
    emit time). Real POIs start at 1.
    """
    counter: Counter = Counter()
    for seq in sequences:
        counter.update(seq)
    vocab = {poi: i + 1 for i, poi in enumerate(sorted(counter))}
    return vocab


def _negative_sampling_table(
    counter: Counter, vocab: Dict[int, int], power: float = 0.75, table_size: int = 1_000_000
) -> np.ndarray:
    """word2vec unigram^0.75 negative-sampling table over vocab INDICES (>=1)."""
    pois = sorted(counter)
    freqs = np.array([counter[p] for p in pois], dtype=np.float64) ** power
    probs = freqs / freqs.sum()
    idxs = np.array([vocab[p] for p in pois], dtype=np.int64)
    cum = np.cumsum(probs)
    # vectorized fill: for each table slot position, find which cum bucket it lands in
    positions = (np.arange(table_size) + 0.5) / table_size
    bucket = np.searchsorted(cum, positions, side="left")
    bucket = np.clip(bucket, 0, len(idxs) - 1)
    return idxs[bucket]


def generate_skipgram_pairs(
    sequences: Sequence[Sequence[int]], vocab: Dict[int, int], window: int, rng: random.Random
) -> np.ndarray:
    """Emit (center_idx, context_idx) pairs with dynamic window (word2vec style).

    Returns an int64 array of shape [n_pairs, 2] in vocab-index space.
    """
    pairs: List[tuple] = []
    for seq in sequences:
        idx_seq = [vocab[p] for p in seq if p in vocab]
        L = len(idx_seq)
        for i, center in enumerate(idx_seq):
            # dynamic window: sample b in [1, window] (down-weights far context)
            b = rng.randint(1, window)
            lo, hi = max(0, i - b), min(L, i + b + 1)
            for j in range(lo, hi):
                if j == i:
                    continue
                pairs.append((center, idx_seq[j]))
    if not pairs:
        return np.empty((0, 2), dtype=np.int64)
    return np.asarray(pairs, dtype=np.int64)


def train_skipgram(
    sequences: Sequence[Sequence[int]],
    *,
    dim: int = 64,
    window: int = 5,
    epochs: int = 5,
    neg_k: int = 5,
    batch_size: int = 4096,
    lr: float = 0.025,
    seed: int = 0,
    device: str = "cpu",
    verbose: bool = True,
) -> tuple:
    """Train SGNS on POI sequences. Returns (vocab, emb_matrix[V, dim]).

    ``vocab`` maps poi_id -> index; ``emb_matrix[0]`` is the <unk>/cold vector
    (zeros); ``emb_matrix[vocab[poi]]`` is the learned center vector.

    The caller MUST pass only TRAIN-portion sequences (leak-safety).
    """
    rng = random.Random(seed)
    torch.manual_seed(seed)
    np.random.seed(seed)

    vocab = build_vocab(sequences)
    if not vocab:
        raise ValueError("Empty vocab — no POI sequences to train skip-gram on.")
    counter: Counter = Counter()
    for seq in sequences:
        counter.update(seq)
    vocab_size = len(vocab) + 1  # +1 for <unk> at index 0

    pairs = generate_skipgram_pairs(sequences, vocab, window, rng)
    if verbose:
        print(f"    skip-gram: vocab={len(vocab)} POIs, pairs={len(pairs):,}, "
              f"dim={dim}, window={window}, epochs={epochs}, neg_k={neg_k}")
    if len(pairs) == 0:
        raise ValueError("No skip-gram pairs generated (sequences too short).")

    neg_table = _negative_sampling_table(counter, vocab)
    model = SkipGramNS(vocab_size, dim).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    pairs_t = torch.from_numpy(pairs)
    n = len(pairs_t)
    for ep in range(epochs):
        perm = torch.randperm(n)
        total = 0.0
        nb = 0
        for s in range(0, n, batch_size):
            bidx = perm[s:s + batch_size]
            batch = pairs_t[bidx]
            center_ids = batch[:, 0].to(device)
            pos_ids = batch[:, 1].to(device)
            neg_np = neg_table[np.random.randint(0, len(neg_table), size=(len(batch), neg_k))]
            neg_ids = torch.from_numpy(neg_np).to(device)
            opt.zero_grad()
            loss = model(center_ids, pos_ids, neg_ids)
            loss.backward()
            opt.step()
            total += float(loss.item())
            nb += 1
        if verbose:
            print(f"      epoch {ep + 1}/{epochs}  loss={total / max(nb,1):.4f}")

    emb = model.center.weight.detach().cpu().numpy().astype(np.float32)
    emb[0] = 0.0  # <unk>/cold-start = zero vector
    return vocab, emb
