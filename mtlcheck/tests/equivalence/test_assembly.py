"""The layer-2 assembly, exercised end to end on real data.

`dataset.load` is the only code that reads a substrate directory, and it is where the S9 alignment
guard, the label-space derivation and the two tensor builds meet. Until this file existed it had no
test at all — it was checked by importing it, which proves nothing.

The fixture is the first 2 000 rows of Alabama's real v18 tables (6.3 MB), truncated consistently
across all three files so the row alignment they must satisfy is preserved.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from mtlcheck.config import DataConfig, TaskFamily
from mtlcheck.data import dataset, splits

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "alabama_head2000"
from ._old_repo import OLD_REPO

REGION_EMB = OLD_REPO / "output" / "check2hgi_design_k_resln_mae_l0_1" / "alabama" / "region_embeddings.parquet"
GRAPH = OLD_REPO / "output" / "check2hgi" / "alabama" / "temp" / "checkin_graph.pt"

def _skip_unless_fixture() -> None:
    if not (FIXTURE / "input" / "next.parquet").exists():
        pytest.skip(f"fixture absent: {FIXTURE}")


def _n() -> int:
    """O tamanho da fixture, LIDO dela e só quando um teste precisa.

    Lido e não fixo porque a fixture foi regenerada em 2026-08-19 (de 2 000 linhas / 4 usuários
    para 2 400 / 13) e uma contagem fixa fez três testes falharem por um motivo que não tinha nada
    a ver com o que eles protegem.

    ⚠ E LAZY, não no nível do módulo. Como `N = len(read_parquet(...))` no topo, a ausência da
    fixture virava `FileNotFoundError` na IMPORTAÇÃO — o que o `pytest.skip` abaixo não alcança e
    que aborta a COLETA da suíte inteira ("Interrupted: 1 error during collection"), não só estes
    testes. Importa para a publicação: o repositório do departamento não redistribui check-ins
    (Apêndice C), então a fixture não vai com ele, e `pytest` imprimiria um erro em vez de um
    relatório.
    """
    import pandas as pd

    _skip_unless_fixture()
    return len(pd.read_parquet(FIXTURE / "input" / "next.parquet", columns=["userid"]))


@pytest.fixture(scope="module")
def inputs(tmp_path_factory):
    _skip_unless_fixture()
    if not (REGION_EMB.exists() and GRAPH.exists()):
        pytest.skip("region embeddings or graph maps absent")
    return dataset.load(
        "alabama", "check2hgi_v18", DataConfig(),
        need_region_tower=True,
        substrate_dir=FIXTURE,
        region_embeddings_path=REGION_EMB,
        graph_path=GRAPH,
        cache_dir=tmp_path_factory.mktemp("cache"),
    )


@pytest.mark.artifacts
def test_load_produces_aligned_tensors(inputs) -> None:
    assert len(inputs) == _n()
    assert inputs.checkin.shape == (_n(), 9, 64)
    assert inputs.region.shape == (_n(), 9, 64)
    assert inputs.checkin.dtype == np.float32
    assert inputs.y_category.shape == (_n(),)
    assert inputs.y_region.shape == (_n(),)
    assert inputs.last_region.shape == (_n(),)
    assert inputs.n_categories == 7


@pytest.mark.artifacts
def test_checkin_tensor_is_position_major(inputs) -> None:
    """Column j of the 576 belongs to position j//64, dimension j%64.

    The reference reshapes numerically-sorted digit columns with `view(-1, 9, 64)`, which is
    position-major in C order. Reading them dim-major instead would scramble every input while every
    shape stayed valid and every test about counts kept passing — so the layout is asserted against
    the raw columns rather than assumed.
    """
    raw = pd.read_parquet(FIXTURE / "input" / "next.parquet")
    columns = sorted((c for c in raw.columns if str(c).isdigit()), key=int)
    assert len(columns) == 576

    flat = raw[columns].to_numpy(dtype=np.float32)
    for position in (0, 4, 8):
        expected = flat[:, position * 64 : (position + 1) * 64]
        assert np.array_equal(inputs.checkin[:, position, :], expected), (
            f"position {position} does not come from columns {position * 64}..{position * 64 + 63}"
        )


@pytest.mark.artifacts
def test_label_space_comes_from_the_label_column(inputs) -> None:
    """`n_regions = max(region_idx) + 1` over the rows, not the count of distinct regions."""
    assert inputs.n_regions == int(inputs.y_region.max()) + 1
    assert inputs.n_regions > len(np.unique(inputs.y_region)), (
        "on this fixture the two derivations should differ, which is what makes the test meaningful"
    )


@pytest.mark.artifacts
def test_region_tower_agrees_with_the_aux_column(inputs) -> None:
    """Position 8 of the region tower is the embedding of the region `last_region_idx` names."""
    from mtlcheck.data import tensors

    table = pd.read_parquet(REGION_EMB)
    matrix = tensors._region_embedding_matrix(table)
    assert np.allclose(inputs.region[:, 8, :], matrix[inputs.last_region])


@pytest.mark.artifacts
def test_region_tower_cache_round_trips(tmp_path) -> None:
    """A second load reuses the cached tensor and produces an identical array."""
    _skip_unless_fixture()
    if not (REGION_EMB.exists() and GRAPH.exists()):
        pytest.skip("region artifacts absent")

    kwargs = dict(need_region_tower=True, substrate_dir=FIXTURE,
                  region_embeddings_path=REGION_EMB, graph_path=GRAPH, cache_dir=tmp_path)
    first = dataset.load("alabama", "check2hgi_v18", DataConfig(), **kwargs)
    cached_files = list(tmp_path.glob("region_tower_*.npy"))
    assert len(cached_files) == 1, "the region tower was not cached"

    second = dataset.load("alabama", "check2hgi_v18", DataConfig(), **kwargs)
    assert np.array_equal(first.region, second.region)


# ---------------------------------------------------------------- S9 at runtime

@pytest.mark.artifacts
def test_misaligned_userids_are_refused(tmp_path) -> None:
    """The guard fires on a table with the right row count and the wrong per-row user.

    This is the failure it exists for: row-count parity holds, every shape stays valid, and every
    (window, region-label) pair is mis-paired.
    """
    _skip_unless_fixture()
    broken = tmp_path / "broken"
    (broken / "input").mkdir(parents=True)

    next_table = pd.read_parquet(FIXTURE / "input" / "next.parquet")
    region_table = pd.read_parquet(FIXTURE / "input" / "next_region.parquet")
    shuffled = region_table.copy()
    shuffled["userid"] = shuffled["userid"].to_numpy()[::-1]

    next_table.to_parquet(broken / "input" / "next.parquet", index=False)
    shuffled.to_parquet(broken / "input" / "next_region.parquet", index=False)

    with pytest.raises(ValueError, match="per-row userids"):
        dataset.load("alabama", "check2hgi_v18", DataConfig(),
                     need_region_tower=False, substrate_dir=broken)


@pytest.mark.artifacts
def test_row_count_mismatch_is_refused(tmp_path) -> None:
    _skip_unless_fixture()
    broken = tmp_path / "short"
    (broken / "input").mkdir(parents=True)
    pd.read_parquet(FIXTURE / "input" / "next.parquet").to_parquet(
        broken / "input" / "next.parquet", index=False)
    pd.read_parquet(FIXTURE / "input" / "next_region.parquet").head(_n() - 1).to_parquet(
        broken / "input" / "next_region.parquet", index=False)

    with pytest.raises(ValueError, match="rows"):
        dataset.load("alabama", "check2hgi_v18", DataConfig(),
                     need_region_tower=False, substrate_dir=broken)


# ---------------------------------------------------------------- streams

@pytest.mark.artifacts
def test_fold_streams_partition_the_rows(inputs) -> None:
    folds = splits.build(inputs.y_category, inputs.userid, split_seed=0)
    device = torch.device("cpu")

    train, val = dataset.fold_streams(inputs, folds[0], TaskFamily.CAT, device)
    assert len(train) + len(val) == _n()
    assert train.aux is None, "the category family has no auxiliary input"

    reg_train, reg_val = dataset.fold_streams(inputs, folds[0], TaskFamily.REG, device)
    assert reg_train.aux is not None, "the region family needs last_region_idx"
    assert len(reg_train) == len(train), "both families must use the same split"


@pytest.mark.artifacts
def test_joint_streams_index_the_same_rows(inputs) -> None:
    """The joint's two tasks index identical rows — what makes the paired comparison legitimate."""
    folds = splits.build(inputs.y_category, inputs.userid, split_seed=0)
    cat_tr, cat_va, reg_tr, reg_va = dataset.joint_streams(inputs, folds[0], torch.device("cpu"))

    assert len(cat_tr) == len(reg_tr)
    assert len(cat_va) == len(reg_va)
    # Same rows, so the region target of validation row i belongs to the same window as its
    # category target.
    expected_cat = torch.from_numpy(inputs.y_category[folds[0].val])
    expected_reg = torch.from_numpy(inputs.y_region[folds[0].val])
    assert torch.equal(cat_va.y, expected_cat)
    assert torch.equal(reg_va.y, expected_reg)


@pytest.mark.artifacts
def test_region_family_without_the_tower_is_refused(tmp_path) -> None:
    _skip_unless_fixture()
    inputs = dataset.load("alabama", "check2hgi_v18", DataConfig(),
                          need_region_tower=False, substrate_dir=FIXTURE)
    folds = splits.build(inputs.y_category, inputs.userid, split_seed=0)
    with pytest.raises(ValueError, match="region tower"):
        dataset.fold_streams(inputs, folds[0], TaskFamily.REG, torch.device("cpu"))


@pytest.mark.artifacts
def test_streamed_and_frame_paths_agree() -> None:
    """Reading position-by-position from the parquet gives the same tensor as loading it whole.

    The streamed path exists to cut peak memory (measured: 1.00 GB -> 0.32 GB at Alabama, for a
    0.21 GB tensor), and a memory optimisation that changes a value is worse than the memory it
    saved. Verified against the frame path AND against the raw columns, so agreement cannot come
    from both paths sharing a bug.
    """
    from mtlcheck.data import tensors

    path = FIXTURE / "input" / "next.parquet"
    if not path.exists():
        pytest.skip("fixture absent")

    streamed = tensors.checkin_tensor(path)
    frame = pd.read_parquet(path)
    via_frame = tensors.checkin_tensor(frame)

    assert streamed.shape == via_frame.shape
    assert np.array_equal(streamed, via_frame)

    columns = sorted((c for c in frame.columns if str(c).isdigit()), key=int)
    raw = frame[columns].to_numpy(dtype=np.float32).reshape(len(frame), 9, 64)
    assert np.array_equal(streamed, raw)


def test_memory_guard_scales_with_the_requirement() -> None:
    """R13 — the margin is a function of the need, not a fixed 16 GB for every dataset."""
    from mtlcheck import memory

    small = memory.tensor_bytes(96_326, 9, 64)
    large = memory.tensor_bytes(3_830_414, 9, 64)
    assert large / small > 39, "the two sizes should be far apart for this test to mean anything"

    # A machine with 4 GB free: fine for Alabama, not for Texas. The reference's fixed 16 GB
    # headroom refuses both.
    plenty = int(4 * 2**30)
    assert small * memory.OVERHEAD_FACTOR + memory.FLOOR_GB * 2**30 < plenty
    assert large * memory.OVERHEAD_FACTOR + memory.FLOOR_GB * 2**30 > plenty
