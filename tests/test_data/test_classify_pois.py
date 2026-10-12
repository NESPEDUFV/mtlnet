"""`_classify_pois` — the legacy-MTL user-isolation POI partition (leak guard).

A POI visited by both a train user and a val user is ambiguous (→ category-train);
a POI visited only by val users is val-exclusive (→ category-val) and must NEVER
appear in train. This pins that partition + its order (extraction is verbatim, so
the fold membership / fold_set_digest is unchanged).
"""

from data.folds import _classify_pois


def _inline_reference(poi_users, train_users, val_users):
    """The pre-extraction inline logic, kept here as the equivalence oracle."""
    train_exclusive, val_exclusive, ambiguous = [], [], []
    for poi, visitors in poi_users.items():
        in_train = bool(visitors & train_users)
        in_val = bool(visitors & val_users)
        if in_train and in_val:
            ambiguous.append(poi)
        elif in_train:
            train_exclusive.append(poi)
        elif in_val:
            val_exclusive.append(poi)
    return train_exclusive, val_exclusive, ambiguous


def test_classify_and_leak_guard():
    poi_users = {
        "p_train": {1, 2},
        "p_val": {3, 4},
        "p_ambig": {2, 3},   # a train user AND a val user
        "p_train2": {1},
        "p_val2": {4},
        "p_other": {99},     # visited only by a user in neither split
    }
    train_users, val_users = {1, 2}, {3, 4}
    tr, va, amb = _classify_pois(poi_users, train_users, val_users)
    assert tr == ["p_train", "p_train2"]      # order = poi_users iteration order
    assert va == ["p_val", "p_val2"]
    assert amb == ["p_ambig"]
    assert set(va).isdisjoint(tr)             # leak guard: no val POI in train
    assert "p_other" not in tr + va + amb     # neither-split POI is dropped


def test_matches_inline_reference():
    poi_users = {f"poi{i}": {i % 5, (i * 7) % 11} for i in range(200)}
    train_users = set(range(0, 6))
    val_users = set(range(6, 11))
    assert _classify_pois(poi_users, train_users, val_users) == _inline_reference(
        poi_users, train_users, val_users
    )
