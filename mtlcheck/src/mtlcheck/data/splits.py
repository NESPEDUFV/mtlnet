"""Cross-validation folds — one split, shared by all three task families.

`StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)` over `(y=next_category,
groups=userid)`. The held-out unit is the **user**: a user's windows are entirely in train or
entirely in validation, never split. Stratification balances the seven category labels across folds.

Three things this module is careful about, each of which silently redraws the split if got wrong:

* **The same split for every family.** The dedicated-category runner, the dedicated-region script and
  the joint trainer all build it this way, and in the joint both tasks share the identical indices.
  That is what makes a paired MTL-vs-ceiling comparison legitimate.
* **The label used for stratification is the CATEGORY**, including for the region task. Region
  labels never enter the split.
* **Label encoding order.** The reference stratifies on integer codes from a fixed map that happens
  to be alphabetical (Community=0 … Travel=6), which is also what sorting the strings gives. Encode
  differently and `StratifiedGroupKFold`'s greedy assignment can land elsewhere.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

from .. import ids

logger = logging.getLogger(__name__)

# The reference's fixed category map. Alphabetical, which matters — see the module docstring.
CATEGORY_ORDER = ("Community", "Entertainment", "Food", "Nightlife", "Outdoors", "Shopping", "Travel")


@dataclass(frozen=True)
class Fold:
    index: int                 # 0-based
    train: np.ndarray
    val: np.ndarray
    #: Users held out INSIDE the development block, for checkpoint selection only. None under the
    #: legacy protocol, where `val` does both jobs and the reported score is therefore selected on
    #: the observations that report it. When this is set, `train` already excludes it.
    inner_val: np.ndarray | None = None

    @property
    def sealed(self) -> bool:
        """True when selection and reporting use disjoint users."""
        return self.inner_val is not None

    @property
    def n_train(self) -> int:
        return len(self.train)

    @property
    def n_val(self) -> int:
        return len(self.val)


def encode_categories(labels) -> np.ndarray:
    """String category labels -> the reference's integer codes."""
    lookup = {name: i for i, name in enumerate(CATEGORY_ORDER)}
    codes = np.asarray([lookup.get(v, -1) for v in np.asarray(labels)], dtype=np.int64)
    if (codes < 0).any():
        unknown = sorted(set(np.asarray(labels)[codes < 0]))
        raise ValueError(f"labels outside the category map: {unknown}")
    return codes


def as_group_ids(userids) -> np.ndarray:
    """Coerce user ids to int64 — a scientifically load-bearing cast, not tidiness.

    The same logical column is stored with different dtypes across artifacts of the same engine:
    `next.parquet` holds `userid` as a STRING while `sequences_next.parquet` holds it as int64, with
    identical values. `StratifiedGroupKFold` sorts its group keys, and string keys sort
    lexicographically — '10' before '2'. Grouping on the string form therefore visits users in a
    different order and the greedy fold assignment lands somewhere else entirely, producing a
    perfectly valid split that is not THE split, with nothing to indicate it.

    Verified: with strings, all four reporting seeds disagree with the reference at fold 1.
    """
    return ids.as_int64(userids, name="userid")


def build_inner(folds: list[Fold], categories, userids, *, inner_split_seed: int,
                inner_splits: int = 8) -> list[Fold]:
    """Carve a user-disjoint inner validation set out of each fold's development block.

    Protocol §2: 70 % train / 10 % inner validation / 20 % outer test. The 10 % comes from an
    8-way `StratifiedGroupKFold` over the 80 % development block — 12.5 % × 80 % = 10 % of all users
    — and one of its folds is taken as the inner set.

    The seed is SEPARATE from the outer split's on purpose. Deriving it from the same integer is the
    confound that made repetition and replicate inseparable (NOMENCLATURE §1), and repeating that one
    level down would make the inner split move whenever the outer one did.

    Users, not rows: the inner set must be disjoint from the training set at the USER level, or a
    user's other windows leak the checkpoint decision back into training.
    """
    categories = np.asarray(categories)
    userids = np.asarray(userids)
    out: list[Fold] = []

    for fold in folds:
        block = np.asarray(fold.train)
        inner = StratifiedGroupKFold(n_splits=inner_splits, shuffle=True,
                                     random_state=inner_split_seed)
        train_rel, inner_rel = next(iter(inner.split(np.zeros(len(block)),
                                                     categories[block], groups=userids[block])))
        train_idx, inner_idx = block[train_rel], block[inner_rel]

        overlap = np.intersect1d(np.unique(userids[train_idx]), np.unique(userids[inner_idx]))
        if len(overlap):
            raise ValueError(f"fold {fold.index}: {len(overlap)} users span train and inner "
                             f"validation; the inner split must be user-disjoint")
        out.append(Fold(index=fold.index, train=train_idx, val=fold.val, inner_val=inner_idx))

    shares = [len(f.inner_val) / (len(f.train) + len(f.inner_val) + len(f.val)) for f in out]
    logger.info("inner validation: %.1f%%-%.1f%% of rows per fold (target ~10%%)",
                100 * min(shares), 100 * max(shares))
    return out


def build(categories, userids, *, split_seed: int, n_splits: int = 5) -> list[Fold]:
    """The canonical user-disjoint, category-stratified 5-split.

    `split_seed`, não `seed`: este parâmetro determina a PARTIÇÃO e nada mais. O
    `NOMENCLATURE.md` §1 cita esta chamada como o sítio do achado que originou o documento —
    o mesmo inteiro semeava o sorteio dos folds E a inicialização, um botão movendo dois
    fatores experimentais.
    """
    y = np.asarray(categories)
    if y.dtype.kind in "US" or y.dtype == object:
        y = encode_categories(y)
    groups = as_group_ids(userids)

    if len(y) != len(groups):
        raise ValueError(f"labels ({len(y)}) and groups ({len(groups)}) differ in length")

    # X is unused by StratifiedGroupKFold beyond its length; the reference passes the real feature
    # matrix in one call site and `np.zeros(len(y))` in another, which is why the two agree.
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True,
                               random_state=split_seed)
    folds = [
        Fold(index=i, train=train, val=val)
        for i, (train, val) in enumerate(sgkf.split(np.zeros(len(y)), y, groups=groups))
    ]

    for f in folds:
        logger.debug("fold %d: train=%d val=%d (users train=%d val=%d)",
                     f.index + 1, f.n_train, f.n_val,
                     len(np.unique(groups[f.train])), len(np.unique(groups[f.val])))
    return folds


def assert_user_disjoint(folds: list[Fold], userids) -> None:
    """No user may appear on both sides of a fold. The leak guard the whole protocol rests on."""
    groups = as_group_ids(userids)
    for f in folds:
        overlap = np.intersect1d(groups[f.train], groups[f.val])
        if overlap.size:
            raise AssertionError(
                f"fold {f.index + 1} shares {overlap.size} users between train and validation "
                f"(e.g. {overlap[:5].tolist()}) — the split is not user-disjoint"
            )


def train_label_set(labels, fold: Fold) -> set[int]:
    """The labels seen in this fold's TRAINING split.

    Used by the region metric to separate in-distribution validation rows from out-of-distribution
    ones. Train-only by construction: reading the validation split here is the leak.
    """
    return set(np.unique(np.asarray(labels)[fold.train]).tolist())


__all__ = ["Fold", "build", "encode_categories", "assert_user_disjoint", "train_label_set",
           "CATEGORY_ORDER"]
