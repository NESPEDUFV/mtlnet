"""The POI2Vec table — HGI's categorical code book, rebuilt here.

The second artifact both substrates consumed and neither could produce. `spatial.load_poi2vec` reads
it and the CLI took it as an argument.

## What it actually is, which is not what the name says

**It is not the AAAI-17 POI2Vec.** No users, no check-in sequences, no latent-region binary tree.
The reference's own docstring says so and it is worth repeating, because the name will otherwise be
cited as a baseline it is not.

What it does: node2vec walks over the Delaunay *place* graph, then each walk is projected from place
ids onto OSM `fclass` codes, then a skip-gram with negative sampling is trained over the ~284-symbol
fclass vocabulary. The per-place table is then a **pure lookup**:

    poi_emb[i] = fclass_emb[fclass[i]]

So the banked Alabama table has 11 848 rows and **284 distinct vectors** (verified). It is a
categorical code book, not a spatial prior — which is worth knowing, because `place_anchor` in the
substrate is anchoring the learnable place table to *category identity*, at `anchor_lambda = 0.1`.

## Why there is no bit-exact target, and what replaces it

**Nothing in the reference's call path is seeded** — no `torch.manual_seed`, no `random.seed`, no
`np.random.seed`. So a rebuild cannot match the banked CSV, and *the reference cannot match itself*.
This is worse than R16: R16 was a nondeterministic kernel under a fixed seed, here there is no seed
at all, so two reference runs are as far apart as two different seeds.

This implementation **is** seeded. That is a fixed defect, not a faithfulness break: seeding does
not change the distribution the walks are drawn from, it makes one draw reproducible. Verification is
therefore structural — the properties that must hold for any draw — and lives in `tests/test_poi2vec.py`.

## Reproduced deliberately

* **The graph is fed to node2vec DIRECTED.** `edges.csv` stores each undirected pair once, and the
  reference does not symmetrise before walking, so a walk can only ever move from a lower row index
  to a higher one. That shapes every walk and therefore the whole co-occurrence distribution.
  `symmetrise=True` is available and off by default.
* **Only walk position 0 is ever a centre**, so the effective context is one-sided.
* **`le_lambda = 1e-8` is not inert.** Under Adam the update is `lr·m̂/(√v̂+ε)`, scale-free in the
  gradient, so a term nine orders of magnitude below the main loss still moves parameters.

## ⚠ KNOWN DIVERGENCES — this module is NOT yet a faithful port

Three parts of the reference are not implemented here, each changing the learned code book. They are
listed rather than hidden because an earlier version of this docstring claimed all three were
"reproduced deliberately" and none of them were — the module asserted behaviour it did not have,
which is the one thing this project treats as worse than a missing feature.

0. **Edge orientation.** `delaunay.build` keeps each undirected pair's first occurrence from a
   column-block concat; the reference's `seen`-set loop scans per simplex row. Same undirected set,
   different first-seen order — measured at Alabama, **816 of 35 519 directed edges (2.3 %) point
   the other way**. The substrate is immune (its loader symmetrises); this module is not, because it
   walks the graph directed. An input-level divergence, listed here because it reaches the code book.
Until those land, treat the table as *structurally* right — a code book keyed by fclass, the right
shape, reproducible — and not as numerically comparable to the banked artifact.

### Corrigidas

2. ~~**The hierarchy regulariser.**~~ **Corrigida 2026-08-19.** A referência aplica
   `½·λ·Σ‖in[cat] − in[fclass]‖²` sobre os pares únicos `(categoria, fclass)`, indexando a tabela de
   *fclass* com um código de *categoria* — defeito da referência, reproduzido, ver
   `_SkipGram.hierarchy_loss`. O que havia aqui era `λ·Σ emb²`, um puxão global para zero: outro
   termo com o mesmo λ.

1. ~~**Negative sampling.**~~ **Corrigida 2026-08-19.** A referência sorteia, por centro, da lista
   dos fclasses que NUNCA co-ocorrem com ele, sem reposição dentro da janela, com fallback para
   "todos menos o centro" quando a lista esvazia. Esta implementação sorteava **uniforme sobre o
   vocabulário inteiro**, incluindo o próprio centro e os contextos verdadeiros.

3. ~~**Objective weighting.**~~ **Corrigida 2026-08-19.** A referência agrupa WINDOWS (2 048 delas) e
   reduz por `sum` na linha, `mean` no lote, então os 20 negativos carregam cinco vezes o peso dos
   quatro positivos. Esta implementação agrupava PARES com `mean` separada em cada termo, 1:1 — um
   objetivo diferente com o mesmo k nominal.

## Fixed

* **Seeded, with our own walk kernel — and the kernel is the reason.** `torch_cluster.random_walk`,
  which PyG's `Node2Vec` calls, **does not respect `torch.manual_seed`**: two calls under the same
  seed produce different walks (verified directly). So seeding the reference would not have made it
  reproducible either, and an implementation that called `manual_seed` and claimed reproducibility
  would be asserting something the code does not do. `_walks` below is a second-order node2vec walk
  over a seeded `numpy.random.Generator`, which makes the claim true.
* `torch.cuda.is_availableable()` — a typo for a method that does not exist, reached only when the
  device is not passed. It would raise; here the device resolution is explicit.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 64
WALK_LENGTH = 10
CONTEXT_SIZE = 5
WALKS_PER_NODE = 5
P, Q = 0.5, 0.5
WALK_BATCH = 128
TRAIN_BATCH = 2048
EPOCHS = 100
LR = 0.05
NEGATIVES_PER_CONTEXT = 5
LE_LAMBDA = 1e-8


@dataclass(frozen=True)
class POI2VecTable:
    """The per-place table, plus what it took to get there."""

    frame: pd.DataFrame              # placeid + 64 columns named "0".."63"
    fclass_embeddings: np.ndarray    # [vocab, 64] — the actual learned object
    vocab_size: int
    best_epoch: int
    best_loss: float
    losses: list[float]
    seed: int

    @property
    def distinct_vectors(self) -> int:
        """Should equal the number of fclasses PRESENT, never the number of places."""
        return len(np.unique(self.frame.iloc[:, 1:].to_numpy(), axis=0))

    def write(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.frame.to_csv(path, index=False)
        logger.info("poi2vec: %d places, %d distinct vectors -> %s",
                    len(self.frame), self.distinct_vectors, path)


def _csr(edge_index: np.ndarray, num_nodes: int) -> tuple[np.ndarray, np.ndarray]:
    """Adjacency in compressed form, for O(1) neighbour lookup during the walk."""
    order = np.argsort(edge_index[0], kind="stable")
    source, target = edge_index[0][order], edge_index[1][order]
    indptr = np.zeros(num_nodes + 1, dtype=np.int64)
    np.add.at(indptr, source + 1, 1)
    return np.cumsum(indptr), target


def _walks(edge_index: np.ndarray, num_nodes: int, *, length: int, per_node: int,
           p: float, q: float, rng: np.random.Generator) -> np.ndarray:
    """Second-order node2vec walks, over a generator we control.

    Written rather than delegated because `torch_cluster.random_walk` ignores `torch.manual_seed`.
    The bias is the standard one: from `current`, having come from `previous`, a candidate `x` is
    weighted `1/p` if it returns to `previous`, `1` if it is also a neighbour of `previous`, and
    `1/q` otherwise. At the reference's `p = q = 0.5` only the middle case differs.

    A Python loop over steps with vectorised work inside each; the walks themselves are a per-walk
    loop because the neighbour lists are ragged. At Alabama that is 11 848 x 5 walks x 10 steps,
    seconds inside a build that takes minutes.
    """
    indptr, neighbours = _csr(edge_index, num_nodes)
    starts = np.repeat(np.arange(num_nodes, dtype=np.int64), per_node)
    walks = np.full((len(starts), length), -1, dtype=np.int64)
    walks[:, 0] = starts

    for step in range(1, length):
        current = walks[:, step - 1]
        previous = walks[:, step - 2] if step > 1 else None
        for i, node in enumerate(current):
            lo, hi = indptr[node], indptr[node + 1]
            if lo == hi:
                walks[i, step] = node                       # a sink absorbs; the reference too
                continue
            candidates = neighbours[lo:hi]
            if previous is None:
                choice = candidates[rng.integers(len(candidates))]
            else:
                back = previous[i]
                blo, bhi = indptr[back], indptr[back + 1]
                prior = neighbours[blo:bhi]
                weights = np.full(len(candidates), 1.0 / q)
                weights[candidates == back] = 1.0 / p
                weights[np.isin(candidates, prior)] = 1.0
                weights[candidates == back] = 1.0 / p       # return beats common-neighbour
                choice = candidates[rng.choice(len(candidates), p=weights / weights.sum())]
            walks[i, step] = choice
    return walks


def _hard_negative_candidates(windows: np.ndarray, vocab_size: int) -> list[list[int]]:
    """Por fclass central, os fclasses que NUNCA co-ocorrem com ele nas janelas.

    É o amostrador da referência (`POISet._neg_candidates`): co-ocorrência é definida sobre as
    janelas cujo PRIMEIRO elemento é o centro — não sobre o par simétrico — e o próprio centro sai
    da lista. Quando a lista fica vazia (todo fclass co-ocorre com ele), a referência cai para
    "todos menos o centro", e esse fallback é reproduzido porque muda o resultado nos centros
    densos.
    """
    co_occurrence: list[set[int]] = [set() for _ in range(vocab_size)]
    for centre, *context in windows:
        co_occurrence[int(centre)].update(int(c) for c in context)

    everything = set(range(vocab_size))
    candidates: list[np.ndarray] = []
    for centre in range(vocab_size):
        usable = everything - co_occurrence[centre] - {centre}
        if not usable:
            usable = everything - {centre}
        candidates.append(sorted(usable))
    return candidates


def _draw_negatives(candidates: list[list[int]], centres: np.ndarray, count: int,
                    rng: random.Random) -> np.ndarray:
    """`count` negativos por janela, SEM reposição dentro da janela.

    A referência usa `random.sample` (sem reposição) e só completa com `random.choice` — aí com
    reposição — quando a lista de candidatos é menor que `count`. Os dois ramos importam: nos
    centros densos a lista encolhe muito.

    `random.sample` sobre listas, e não `Generator.choice`, é deliberado nos dois sentidos: é a
    ferramenta da referência, e `choice(replace=False)` do numpy permuta o pool inteiro a cada
    chamada. São ~35 milhões de chamadas por build; a diferença é entre minutos e horas.
    """
    out = np.empty((len(centres), count), dtype=np.int64)
    for i, centre in enumerate(centres.tolist()):
        pool = candidates[centre]
        if count <= len(pool):
            out[i] = rng.sample(pool, count)
        else:
            drawn = list(pool)
            rng.shuffle(drawn)
            drawn += [rng.choice(pool) for _ in range(count - len(pool))]
            out[i] = drawn
    return out


class _SkipGram(nn.Module):
    """Skip-gram with negative sampling over the fclass vocabulary. Hand-written, as in the source."""

    def __init__(self, vocab_size: int, dim: int = EMBEDDING_DIM, *,
                 hierarchy_pairs: torch.Tensor | None = None) -> None:
        super().__init__()
        self.in_embed = nn.Embedding(vocab_size, dim)
        self.out_embed = nn.Embedding(vocab_size, dim)
        nn.init.xavier_uniform_(self.in_embed.weight)
        nn.init.xavier_uniform_(self.out_embed.weight)
        pairs = (torch.empty(0, 2, dtype=torch.long) if hierarchy_pairs is None
                 else hierarchy_pairs)
        self.register_buffer("hierarchy_pairs", pairs)

    def hierarchy_loss(self) -> torch.Tensor:
        """`½·λ·Σ‖in[cat] − in[fclass]‖²` sobre os pares únicos (categoria, fclass).

        ⚠ Indexa a tabela de **fclass** com um código de **categoria**. Isso é um defeito da
        referência e é reproduzido: com 7 categorias e 284 fclasses, `in_embed[3]` é o vetor do
        fclass 3, não o da categoria 3. O termo portanto amarra cada fclass ao vetor de um fclass
        arbitrário de índice baixo — não à sua categoria. Corrigir mudaria o objetivo, e o objetivo
        é o que produziu todos os artefatos bancados.
        """
        if self.hierarchy_pairs.numel() == 0:
            return self.in_embed.weight.new_zeros(())
        difference = (self.in_embed(self.hierarchy_pairs[:, 0])
                      - self.in_embed(self.hierarchy_pairs[:, 1]))
        return 0.5 * LE_LAMBDA * (difference * difference).sum()

    def forward(self, centre: torch.Tensor, context: torch.Tensor,
                negatives: torch.Tensor) -> torch.Tensor:
        """One WINDOW per row: `centre` [B], `context` [B, ctx], `negatives` [B, ctx*k].

        The reduction is `sum` over each row and `mean` over the batch, which is the reference's
        `-(log_pos.sum(1) + log_neg.sum(1)).mean()`. It is not cosmetic: a window carries 4
        positives against 20 negatives, so the negative term gets five times the positive term's
        weight in the gradient. An earlier version here batched PAIRS and took `mean` on each term
        separately, weighting them 1:1 — a different objective at the same nominal k.
        """
        c = self.in_embed(centre).unsqueeze(2)                     # [B, D, 1]
        positive = torch.bmm(self.out_embed(context), c).squeeze(2)          # [B, ctx]
        negative = torch.bmm(self.out_embed(negatives), -c).squeeze(2)       # [B, ctx*k]
        return -(nn.functional.logsigmoid(positive).sum(1)
                 + nn.functional.logsigmoid(negative).sum(1)).mean()


def build(places: pd.DataFrame, edges: pd.DataFrame, *, seed: int = 42,
          epochs: int = EPOCHS, device: torch.device | None = None,
          symmetrise: bool = False) -> POI2VecTable:
    """Train the fclass code book and project it onto places.

    `places` and `edges` are the Delaunay artifacts — `delaunay.build(...)` produces both, so a
    from-scratch build no longer needs the HGI engine at all.
    """
    device = device or torch.device("cpu")
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    sampler = random.Random(seed)      # o amostrador de negativos, na ferramenta da referência

    fclass = places["fclass"].to_numpy(dtype=np.int64)
    vocab_size = int(fclass.max()) + 1
    edge_index = np.stack([edges["source"].to_numpy(), edges["target"].to_numpy()])
    if symmetrise:
        edge_index = np.concatenate([edge_index, edge_index[::-1]], axis=1)
    else:
        # Reproduced: each undirected pair appears once and is NOT symmetrised, so a walk can only
        # move from a lower row index to a higher one. It shapes every walk.
        logger.info("poi2vec: walking a DIRECTED graph (reproduced); pass symmetrise=True to undo")

    raw = _walks(edge_index, len(places), length=WALK_LENGTH, per_node=WALKS_PER_NODE,
                 p=P, q=Q, rng=rng)
    # Project place ids onto fclass codes, then cut each walk into CONTEXT_SIZE windows. Only
    # position 0 is ever a centre — reproduced, and it makes the effective context one-sided.
    projected = fclass[raw]
    windows = np.stack([projected[:, i:i + CONTEXT_SIZE]
                        for i in range(WALK_LENGTH - CONTEXT_SIZE + 1)], axis=1)
    window_codes = windows.reshape(-1, CONTEXT_SIZE)          # numpy, para o amostrador
    windows = torch.tensor(window_codes, dtype=torch.long, device=device)
    # Pares (categoria, fclass) únicos, como a referência os extrai de pois.csv.
    pair_frame = places[["category", "fclass"]].drop_duplicates()
    hierarchy_pairs = torch.tensor(pair_frame.to_numpy(dtype=np.int64), dtype=torch.long)
    logger.info("poi2vec: regularizador de hierarquia sobre %d pares (categoria, fclass) únicos",
                len(hierarchy_pairs))
    if len(hierarchy_pairs) and int(hierarchy_pairs[:, 0].max()) >= vocab_size:
        # A referência estouraria com um IndexError opaco do nn.Embedding aqui. O erro é dela e é
        # reproduzido; o que muda é a legibilidade. Em corpus real não acontece — são 7 categorias
        # contra centenas de fclasses — então bater aqui significa vocabulário de fclass pequeno
        # demais, tipicamente uma fixture.
        raise ValueError(
            f"o regularizador de hierarquia indexa a tabela de FCLASS (tamanho {vocab_size}) com "
            f"um código de CATEGORIA (máximo {int(hierarchy_pairs[:, 0].max())}). Isso é o defeito "
            f"de índice da referência, reproduzido de propósito; ele só é inofensivo quando há mais "
            f"fclasses do que categorias.")
    model = _SkipGram(vocab_size, hierarchy_pairs=hierarchy_pairs).to(device)
    optimiser = torch.optim.Adam(model.parameters(), lr=LR)
    generator = torch.Generator(device="cpu").manual_seed(seed)

    n_context = CONTEXT_SIZE - 1
    n_negatives = n_context * NEGATIVES_PER_CONTEXT
    candidates = _hard_negative_candidates(window_codes, vocab_size)
    logger.info("poi2vec: negativos duros — lista de candidatos por centro, mediana %d de %d "
                "fclasses", int(np.median([len(c) for c in candidates])), vocab_size)

    best_loss, best_state, losses = float("inf"), None, []
    for _epoch in range(epochs):
        # A WINDOW is the training unit, as in the reference — not a (centre, context) pair.
        order = torch.randperm(len(windows), generator=generator).to(device)
        shuffled = windows[order]
        negatives_all = torch.from_numpy(
            _draw_negatives(candidates, window_codes[order.cpu().numpy(), 0],
                            n_negatives, sampler)).to(device)

        total, batches = 0.0, 0
        for start in range(0, len(shuffled), TRAIN_BATCH):
            stop = start + TRAIN_BATCH
            batch = shuffled[start:stop]
            loss = model(batch[:, 0], batch[:, 1:], negatives_all[start:stop])
            # Reproduzido: nove ordens de grandeza abaixo do termo principal, e NÃO inerte — a
            # atualização do Adam é livre de escala no gradiente, então ainda move parâmetros.
            loss = loss + model.hierarchy_loss()
            optimiser.zero_grad(set_to_none=True)
            loss.backward()
            optimiser.step()
            total += float(loss.detach())
            batches += 1

        mean = total / max(batches, 1)
        losses.append(mean)
        # Lowest epoch-mean TRAINING loss, as in the reference. There is no validation set.
        if mean < best_loss:
            best_loss, best_state = mean, {k: v.detach().cpu().clone()
                                           for k, v in model.state_dict().items()}

    model.load_state_dict(best_state)
    table = model.in_embed.weight.detach().cpu().numpy()

    frame = pd.DataFrame(table[fclass], columns=[str(i) for i in range(EMBEDDING_DIM)])
    frame.insert(0, "placeid", places["placeid"].to_numpy())
    return POI2VecTable(frame=frame, fclass_embeddings=table, vocab_size=vocab_size,
                        best_epoch=int(np.argmin(losses)) + 1, best_loss=best_loss,
                        losses=losses, seed=seed)


__all__ = ["POI2VecTable", "build", "EMBEDDING_DIM", "WALK_LENGTH", "CONTEXT_SIZE",
           "WALKS_PER_NODE", "EPOCHS", "LE_LAMBDA"]
