"""Os manifestos retroativos descrevem experimentos que este código ainda resolve do mesmo jeito.

Um manifesto escrito DEPOIS da execução é uma alegação, não um registro. A alegação só vale se
resolver para os mesmos fingerprints que as células bancadas gravaram — senão ele descreve outro
experimento e é PIOR que manifesto nenhum, porque tem cara de proveniência.

A comparação contra as células bancadas mora na máquina que as tem (a A40) e roda como script. O que
este teste faz é a metade que viaja com o repo: cada manifesto carrega, cada célula resolve, e os
fingerprints são os que foram conferidos contra o banco em 2026-08-19. Se um default mudar e mover
um deles, isto falha — que é exatamente o alarme que se quer.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mtlcheck.config import load_recipe
from mtlcheck.train import wave

BASE_DIR = Path(__file__).resolve().parents[1]
CAMPAIGN = BASE_DIR / "studies/porting_validation/waves/campaign_2026_08_19"

#: (estudo, cell_id) -> science_fingerprint, conferido contra runs/ na A40 em 2026-08-19.
#: 13 de 16 conferiram na hora; as três de `final_az` estavam reconstruindo e entraram depois.
FROZEN = {
    ("al_full", "cat-alabama-p0s0"): "5913dfd73423",
    ("al_full", "reg-alabama-p0s0"): "95020a62a440",
    ("al_full", "joint-alabama-p0s0"): "1a8a2514f4b3",
    ("tri_v18region", "reg-alabama-p0s0"): "fd0ecf9f49c0",
    ("rs0_v18region", "reg-alabama-p0s0"): "fd0ecf9f49c0",
    ("rs1_v18region", "reg-alabama-p0s0"): "fd0ecf9f49c0",
    ("rs7_v18region", "reg-alabama-p0s0"): "fd0ecf9f49c0",
    ("fix3", "reg-alabama-p0s0"): "c7e4b3ddb25a",
    ("div1_only", "reg-alabama-p0s0"): "c7e4b3ddb25a",
    ("fix1_2", "reg-alabama-p0s0"): "c7e4b3ddb25a",
    ("final_al", "cat-alabama-p0s0"): "635f9f82598e",
    ("final_al", "reg-alabama-p0s0"): "c7e4b3ddb25a",
    ("final_al", "joint-alabama-p0s0"): "def6d0e5c393",
}


def _resolved_cells():
    for path in sorted(CAMPAIGN.glob("*.toml")):
        study, cells = wave.load(path)
        for cell in cells:
            resolved = load_recipe(cell.recipe, state=cell.state, seed=cell.seed,
                                   split_seed=cell.split_seed, **cell.overrides)
            yield study, resolved


def test_every_campaign_manifest_loads() -> None:
    studies = {study for study, _ in _resolved_cells()}
    assert len(list(CAMPAIGN.glob("*.toml"))) == 10
    assert {"al_full", "final_al", "final_az", "fix3", "fix1_2", "div1_only"} <= studies


@pytest.mark.parametrize("key,expected", sorted(FROZEN.items()))
def test_manifest_resolves_to_the_banked_fingerprint(key, expected) -> None:
    study, cell_id = key
    got = {(s, r.cell_id): r.science_fingerprint()[:12] for s, r in _resolved_cells()}
    assert got[(study, cell_id)] == expected, (
        f"{study}/{cell_id} resolvia para {expected} quando foi conferido contra a célula bancada, "
        f"e agora resolve para {got[(study, cell_id)]}. O manifesto deixou de descrever o "
        f"experimento que rodou — procure o default que mudou.")


def test_the_studies_that_differ_only_by_substrate_are_indistinguishable_here() -> None:
    """O limite do formato, fixado para não ser esquecido.

    `fix3`, `div1_only` e `fix1_2` são a MESMA célula sobre três substratos diferentes, e resolvem
    para o mesmo fingerprint. A wave não expressa a identidade do substrato
    (`docs/RUNNING_STUDIES.md` §4), então o que os separa está em
    `evidence/campaign_substrates.json` — e, para células novas, no campo `substrate` do result.json.
    """
    got = {(s, r.cell_id): r.science_fingerprint() for s, r in _resolved_cells()}
    three = {got[(s, "reg-alabama-p0s0")] for s in ("fix3", "div1_only", "fix1_2")}
    assert len(three) == 1, (
        "se estes passarem a diferir, a wave ganhou identidade de substrato e este teste — junto com "
        "o evidence/campaign_substrates.json — pode ser aposentado")


# ── a campanha v19_defence da PONTE (2026-08-21, arquivada em 25-08) ─────────────────────────────────────────────────────────

V19_DEFENCE = (Path(__file__).resolve().parents[1]
               / "studies/archive/v19_defence_bridge/waves/campaign.toml")
STUDIES = Path(__file__).resolve().parents[1] / "studies"


def _confirmatory_manifests() -> list[Path]:
    """Toda wave marcada `confirmatory = true`, onde quer que esteja.

    Varre por MARCA e não por caminho. A primeira versão apontava para o `campaign.toml` literal, o
    que protegia esta campanha e **nenhuma futura** — e a próxima pessoa não terá o aviso fresco.
    """
    import tomllib

    found = []
    for path in sorted(STUDIES.glob("**/waves/**/*.toml")):
        with path.open("rb") as fh:
            raw = tomllib.load(fh)
        if (raw.get("wave", {}) or {}).get("confirmatory"):
            found.append(path)
    return found


def test_the_marker_finds_the_campaign() -> None:
    """Sem isto, uma varredura que não acha nada faz o teste abaixo passar vazio."""
    manifests = _confirmatory_manifests()
    assert V19_DEFENCE in manifests, "a campanha perdeu a marca `confirmatory = true`"


@pytest.mark.parametrize("manifest", _confirmatory_manifests(), ids=lambda p: p.parent.parent.name)
def test_every_confirmatory_cell_declares_predictions(manifest) -> None:
    """Vale para QUALQUER wave confirmatória, presente ou futura."""
    _, cells = wave.load(manifest)
    omitted = [c.label for c in cells if not c.save_predictions]
    assert not omitted, (
        f"{manifest.name}: {len(omitted)} célula(s) sem `save_predictions = true`. Elas rodariam "
        f"sem gravar o fold externo, e o compare exigiria re-treinar. Primeiras: {omitted[:3]}")


def test_every_campaign_cell_declares_predictions_explicitly() -> None:
    """A omissão que teria custado ~34 h de GPU.

    O default de `Cell.save_predictions` é `False`, e está certo — inverter invalidaria toda célula
    bancada cujo manifesto omite o campo, inclusive as SELADAS. Mas isso significa que um manifesto
    que OMITE o campo roda sem gravar linha nenhuma do fold externo, e o `compare` depois exige
    re-treinar tudo.

    A primeira versão do manifesto da campanha omitiu, por analogia com o `mtlcheck train`, onde o
    comportamento é ligado por `--split-seed`. O caminho da wave não tem esse resolvedor.
    """
    study, cells = wave.load(V19_DEFENCE)
    assert study == "v19_defence"
    assert len(cells) == 54
    omitted = [c.label for c in cells if not c.save_predictions]
    assert not omitted, (
        f"{len(omitted)} célula(s) sem `save_predictions = true`: elas rodariam sem gravar o fold "
        f"externo, e o compare exigiria re-treinar. Primeiras: {omitted[:3]}")


def test_the_seed_counts_follow_the_pre_registered_rule() -> None:
    """4 réplicas nos estados-ponte, 2 nos grandes — `docs/plans/EVALUATION_PROTOCOL.md:75`.

    Não é preferência: nos grandes o desvio entre sementes é 20–50× menor que a componente de
    fold/usuário, então 4 encolheria a meia-largura em ≤0,06 pp e dobraria o wall-clock dominante.
    """
    from collections import Counter

    _, cells = wave.load(V19_DEFENCE)
    per_state = Counter(c.state for c in cells)
    for state in ("alabama", "arizona", "istanbul"):
        assert per_state[state] == 12, f"{state}: 3 famílias × 4 réplicas"
    for state in ("florida", "california", "texas"):
        assert per_state[state] == 6, f"{state}: 3 famílias × 2 réplicas"
    assert {c.seed for c in cells if c.state == "texas"} == {0, 7}


def test_the_partition_is_frozen_across_replicates() -> None:
    """`split_seed = 0` em toda parte: as sementes indexam RÉPLICAS, não repetições.

    Deixar a partição mover com a semente re-admite a componente de fold (~1,2 pp) na comparação
    pareada e torna o Tier A agrupado inexecutável — `predictions.assert_comparable` recusa células
    que atravessam mais de um `partition_hash`.
    """
    _, cells = wave.load(V19_DEFENCE)
    assert {c.split_seed for c in cells} == {0}

# ── a campanha v19_defence da PONTE, arquivada ──────────────────────────────────────────────────────────────────────
#
# As 54 células da leitura confirmatória. Até 24-08 NENHUMA identidade delas estava fixada em lugar
# nenhum: o que as protegia era um único assert sobre `split_seed`, e `runs/` vive na A40, fora
# desta árvore. Uma regressão no carregador apareceria lá — possivelmente já como retreino, que é
# uma segunda leitura do teste selado.
#
# Os valores não foram digitados: saíram do carregador e foram conferidos, um a um, contra o
# `science_fingerprint` que cada célula GRAVOU ao rodar. As 54 bateram. Isso é mais forte que pinar
# o que o carregador produz hoje — prova que ele ainda descreve o experimento que aconteceu.

V19_WAVES = BASE_DIR / "studies/archive/v19_defence_bridge/waves"

FROZEN_V19 = {
    "cat-alabama-p0s0": "635f9f82598e7987",
    "cat-alabama-p0s1": "0c46f69b27a98546",
    "cat-alabama-p0s100": "d987893e791c752b",
    "cat-alabama-p0s7": "4ee7da2ccfcf1d46",
    "cat-arizona-p0s0": "ac60c2cd0d226661",
    "cat-arizona-p0s1": "635362d15d88d5ef",
    "cat-arizona-p0s100": "df7e4301278c01cf",
    "cat-arizona-p0s7": "ffdf9ffaefdad425",
    "cat-california-p0s0": "0d5b9c9a2b4aa599",
    "cat-california-p0s7": "17145f2fc9b674cc",
    "cat-florida-p0s0": "7ad0c7ce5775631a",
    "cat-florida-p0s7": "4d33730ac1393daf",
    "cat-istanbul-p0s0": "68acbce9c91fd485",
    "cat-istanbul-p0s1": "5fb6321416f5f555",
    "cat-istanbul-p0s100": "e41111e813101300",
    "cat-istanbul-p0s7": "d87a935401ebc5a1",
    "cat-texas-p0s0": "9040f649115e41ce",
    "cat-texas-p0s7": "6dbbcc676156223f",
    "joint-alabama-p0s0": "def6d0e5c393ab5b",
    "joint-alabama-p0s1": "a10fd96634021c86",
    "joint-alabama-p0s100": "5094f6f1dbd42cd5",
    "joint-alabama-p0s7": "d97942d549c4024e",
    "joint-arizona-p0s0": "8fcbba8b6a8d2f6d",
    "joint-arizona-p0s1": "a6f2d72b8ac2df21",
    "joint-arizona-p0s100": "d33b4c4ca3b674e4",
    "joint-arizona-p0s7": "65daba414fcb934a",
    "joint-california-p0s0": "652032094fa8be23",
    "joint-california-p0s7": "ef46229e398c8876",
    "joint-florida-p0s0": "16ad7b2171951c69",
    "joint-florida-p0s7": "e32bfaa24daa97c6",
    "joint-istanbul-p0s0": "c84f55e4c333fdde",
    "joint-istanbul-p0s1": "5d0e043117f50647",
    "joint-istanbul-p0s100": "5ce8ceb56f6915ba",
    "joint-istanbul-p0s7": "ec1f2bc964272e03",
    "joint-texas-p0s0": "a5536555c104e39e",
    "joint-texas-p0s7": "fd170d3503405bf5",
    "reg-alabama-p0s0": "c7e4b3ddb25a88ca",
    "reg-alabama-p0s1": "ff301e926c74bb03",
    "reg-alabama-p0s100": "2d45f2d9c1f0ed54",
    "reg-alabama-p0s7": "0d9efe10dbcfe6a0",
    "reg-arizona-p0s0": "20b0f99dc67c59e0",
    "reg-arizona-p0s1": "2f9ce11940f15167",
    "reg-arizona-p0s100": "51cf3ad181c84410",
    "reg-arizona-p0s7": "4c1f61f61d307fd9",
    "reg-california-p0s0": "0538f6713bfe61af",
    "reg-california-p0s7": "2db517ac36e609a4",
    "reg-florida-p0s0": "c40e0850474d0a24",
    "reg-florida-p0s7": "a44f71f1fd33f6d2",
    "reg-istanbul-p0s0": "ef37ee416e93495e",
    "reg-istanbul-p0s1": "05fb1c617a7d79b4",
    "reg-istanbul-p0s100": "2c69c3db77d29f12",
    "reg-istanbul-p0s7": "f698cb4cfae3b80c",
    "reg-texas-p0s0": "64c5aeb208316be1",
    "reg-texas-p0s7": "6de326156636073b",
}


def _resolved_v19():
    for path in sorted(V19_WAVES.glob("slice_*.toml")):
        _, cells = wave.load(path)
        for cell in cells:
            yield load_recipe(cell.recipe, state=cell.state, seed=cell.seed,
                              split_seed=cell.split_seed, **cell.overrides)


def test_a_campanha_v19_tem_as_54_celulas() -> None:
    resolvidos = {r.cell_id for r in _resolved_v19()}
    assert len(resolvidos) == 54, f"{len(resolvidos)} células; a campanha tem 54"
    assert resolvidos == set(FROZEN_V19)


@pytest.mark.parametrize("cell_id", sorted(FROZEN_V19))
def test_a_celula_v19_resolve_para_a_identidade_que_ela_bancou(cell_id) -> None:
    """A identidade tem de sobreviver a qualquer mexida no carregador.

    Se falhar: um default mudou, o manifesto deixou de descrever o que rodou, e o resume da wave
    passaria a ver as células como stale. Retreinar uma célula selada é uma SEGUNDA leitura do teste
    externo — o dano não é perder GPU, é perder o lacre.
    """
    got = {r.cell_id: r.science_fingerprint() for r in _resolved_v19()}
    assert got[cell_id] == FROZEN_V19[cell_id], (
        f"{cell_id} gravou {FROZEN_V19[cell_id]} ao rodar e agora resolve para "
        f"{got[cell_id]}. Procure o default que mudou antes de tocar em qualquer wave.")
