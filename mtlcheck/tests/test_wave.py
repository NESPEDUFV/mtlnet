"""The wave manifest and its executor, tested without a GPU.

A wave exists to stop the failure mode that produced this project's two worst defects: something
that must hold for every run, enforced nowhere in particular. So the tests are mostly about refusals
and about resume being honest.
"""

from __future__ import annotations

import json

import pathlib

import pytest

from mtlcheck.train import wave


def _manifest(tmp_path, body: str):
    path = tmp_path / "wave.toml"
    path.write_text(body)
    return path


def test_the_matrix_expands_to_one_cell_per_state_and_seed(tmp_path) -> None:
    path = _manifest(tmp_path, '''
[wave]
study = "s"

[[cell]]
split_seed = "per-seed"
recipe = "recipes/v18/cat.toml"
states = ["arizona", "istanbul"]
seeds = [0, 1]
''')
    study, cells = wave.load(path)
    assert study == "s"
    assert len(cells) == 4
    assert {(c.state, c.seed) for c in cells} == {("arizona", 0), ("arizona", 1),
                                                 ("istanbul", 0), ("istanbul", 1)}


def test_a_duplicated_cell_is_refused(tmp_path) -> None:
    """Two entries producing the same cell would race on one directory and one would win silently."""
    path = _manifest(tmp_path, '''
[wave]
study = "s"

[[cell]]
split_seed = "per-seed"
recipe = "r.toml"
states = ["arizona"]
seeds = [0]

[[cell]]
split_seed = "per-seed"
recipe = "r.toml"
states = ["arizona"]
seeds = [0]
''')
    with pytest.raises(ValueError, match="more than once"):
        wave.load(path)


def test_a_manifest_without_a_study_is_refused(tmp_path) -> None:
    with pytest.raises(ValueError, match="study"):
        wave.load(_manifest(tmp_path, '[wave]\n\n[[cell]]\nrecipe="r"\nstates=["a"]\nseeds=[0]\n'))


def test_a_cell_missing_a_key_names_the_key(tmp_path) -> None:
    path = _manifest(tmp_path, '[wave]\nstudy="s"\n\n[[cell]]\nrecipe="r"\nstates=["a"]\n')
    with pytest.raises(ValueError, match="seeds"):
        wave.load(path)


def test_one_failing_cell_does_not_sink_the_wave(tmp_path, monkeypatch) -> None:
    """A wave of 24 cells must not lose 23 results because the fourth raised."""
    path = _manifest(tmp_path, '''
[wave]
study = "s"

[[cell]]
split_seed = "per-seed"
recipe = "r.toml"
states = ["arizona", "istanbul"]
seeds = [0, 1]
''')

    def execute(cell, device):
        if cell.state == "istanbul" and cell.seed == 0:
            raise RuntimeError("boom")
        return tmp_path / cell.label, 0.30

    outcomes = wave.run(path, execute=execute, identify=_identify, resume=False)
    by_status = {o.status for o in outcomes}
    assert by_status == {"ran", "failed"}
    assert sum(o.status == "ran" for o in outcomes) == 3
    assert "boom" in next(o for o in outcomes if o.status == "failed").detail


#: O que `check2hgi verify` acharia no disco AGORA. Uma lista para que um teste possa trocá-lo
#: sem redefinir o resolvedor inteiro — é assim que se simula "o substrato foi reconstruído".
_SUBSTRATE_ON_DISK = [{}]


def _identify(cell):
    """Stand-in for the CLI's resolver: id, fingerprint, and the substrate identity on disk now.

    Keeping the fingerprint a function of the cell is what lets these tests exercise the staleness
    check at all — a constant would make every banked result look current.
    """
    from mtlcheck import paths
    base = paths.cell_id("cat", cell.state, cell.seed, cell.split_seed)
    return ((f"{base}-{cell.arm}" if cell.arm else base),
            f"fp{sorted(cell.overrides.items())}",
            _SUBSTRATE_ON_DISK[0])


def test_resume_skips_only_cells_whose_result_parses(tmp_path, monkeypatch) -> None:
    """A crashed cell leaves a directory behind; skipping on directory existence re-banks garbage."""
    from mtlcheck import paths

    monkeypatch.setenv("RUNS_ROOT", str(tmp_path / "runs"))
    path = _manifest(tmp_path, '''
[wave]
study = "s"

[[cell]]
split_seed = "per-seed"
recipe = "cat.toml"
states = ["arizona"]
seeds = [0, 1]
''')

    good = paths.run_dir("s", paths.cell_id("cat", "arizona", 0, 0))
    good.mkdir(parents=True)
    (good / "result.json").write_text(json.dumps({"science_fingerprint": "fp[]"}))

    broken = paths.run_dir("s", paths.cell_id("cat", "arizona", 1, 1))
    broken.mkdir(parents=True)
    (broken / "result.json").write_text("{ truncated")

    ran = []
    outcomes = wave.run(path, execute=lambda c, d: (ran.append(c.seed), (tmp_path, 0.1))[1],
                        identify=_identify, resume=True)

    assert [o.status for o in outcomes] == ["skipped", "ran"]
    assert ran == [1], "the cell with the unreadable result must be re-run"


def test_a_stale_fingerprint_invalidates_a_banked_cell(tmp_path, monkeypatch) -> None:
    """The check the docstring promised and the code never made.

    It read `payload["fingerprint"]` — the schema spells it `config_fingerprint` — and then compared
    it to nothing at all, so editing a recipe kept every cell it touched. A wave whose resume cannot
    see a config change is a wave that reports stale numbers under a new manifest.
    """
    from mtlcheck import paths

    monkeypatch.setenv("RUNS_ROOT", str(tmp_path / "runs"))
    path = _manifest(tmp_path, """
[wave]
study = "s"

[[cell]]
split_seed = "per-seed"
recipe = "cat.toml"
states = ["arizona"]
seeds = [0]
set = { epochs = 30 }
""")
    banked = paths.run_dir("s", paths.cell_id("cat", "arizona", 0, 0))
    banked.mkdir(parents=True)
    (banked / "result.json").write_text(json.dumps({"science_fingerprint": "fp[('epochs', 50)]"}))

    ran = []
    wave.run(path, execute=lambda c, d: (ran.append(c.seed), (tmp_path, 0.1))[1],
             identify=_identify, resume=True)
    assert ran == [0], "a cell banked under a different configuration must be re-run"


def test_a_predictions_cell_without_rows_is_re_run(tmp_path, monkeypatch) -> None:
    """result.json lands before predictions.parquet, so a crash between them is invisible."""
    from mtlcheck import paths

    monkeypatch.setenv("RUNS_ROOT", str(tmp_path / "runs"))
    path = _manifest(tmp_path, """
[wave]
study = "s"

[[cell]]
split_seed = "per-seed"
recipe = "cat.toml"
states = ["arizona"]
seeds = [0]
save_predictions = true
""")
    banked = paths.run_dir("s", paths.cell_id("cat", "arizona", 0, 0))
    banked.mkdir(parents=True)
    (banked / "result.json").write_text(json.dumps({"science_fingerprint": "fp[]"}))

    ran = []
    wave.run(path, execute=lambda c, d: (ran.append(c.seed), (tmp_path, 0.1))[1],
             identify=_identify, resume=True)
    assert ran == [0], "a confirmatory cell with no rows must not count as done"

    (banked / "predictions.parquet").write_bytes(b"")
    ran.clear()
    wave.run(path, execute=lambda c, d: (ran.append(c.seed), (tmp_path, 0.1))[1],
             identify=_identify, resume=True)
    assert ran == [], "with the rows present it is done"


def test_turning_telemetry_on_does_not_invalidate_a_banked_cell(tmp_path, monkeypatch) -> None:
    """The defect that would have spent a second read of the sealed outer test.

    grad_geometry, diagnostics, retain_checkpoints and keep_top_k decide what a run WRITES DOWN, not
    what it computes — yet all four sat inside the resume hash. Merely turning telemetry on rotated
    the fingerprint of all 36 banked bridge cells; `_already_done` returned None; the cell re-trained
    and `predictions.write` overwrote predictions.parquet. A re-run is not bit-identical, so that
    installs a DIFFERENT sealed read underneath a table already reported.
    """
    from mtlcheck import config as cfg

    base = cfg.load_recipe("recipes/v18/joint.toml", state="alabama", seed=0, split_seed=0,
                           inner_validation=True)
    loud = cfg.load_recipe("recipes/v18/joint.toml", state="alabama", seed=0, split_seed=0,
                           inner_validation=True, diagnostics=True, grad_geometry=False,
                           retain_checkpoints="every", keep_top_k=5)
    assert base.science_fingerprint() == loud.science_fingerprint(), "telemetry is not science"
    assert base.fingerprint() != loud.fingerprint(), "but provenance still records it"

    science = cfg.load_recipe("recipes/v18/joint.toml", state="alabama", seed=1, split_seed=0,
                              inner_validation=True)
    assert base.science_fingerprint() != science.science_fingerprint(), "a seed still invalidates"


def test_a_cell_banked_before_the_split_is_migrated_not_re_run(tmp_path, monkeypatch) -> None:
    """A result predating `science_fingerprint` must be re-hashed from the config IT recorded.

    Falling back to the old full `config_fingerprint` compares apples to oranges, so every
    historical cell reads stale — which for a sealed cell means re-training and a second outer read.
    """
    from mtlcheck import config as cfg, paths

    monkeypatch.setenv("RUNS_ROOT", str(tmp_path / "runs"))
    path = _manifest(tmp_path, """
[wave]
study = "s"

[[cell]]
recipe = "recipes/v18/joint.toml"
states = ["alabama"]
seeds = [0]
split_seed = 0
set = { inner_validation = true }
""")
    resolved = cfg.load_recipe("recipes/v18/joint.toml", state="alabama", seed=0, split_seed=0,
                               inner_validation=True)
    banked = paths.run_dir("s", resolved.cell_id)
    banked.mkdir(parents=True)
    # An OLD artifact: full fingerprint only, no science_fingerprint key.
    (banked / "result.json").write_text(json.dumps({
        "config_fingerprint": resolved.fingerprint(), "config": resolved.to_dict()}))

    ran = []
    wave.run(path, execute=lambda c, d: (ran.append(c.seed), (tmp_path, 0.1))[1],
             identify=lambda c: (resolved.cell_id, resolved.science_fingerprint(), {}),
             resume=True)
    assert ran == [], "a pre-split cell must be recognised, not re-trained"


# ── identidade do substrato (bug achado em 2026-08-19) ──────────────────────────────────────────

def _bank(tmp_path, monkeypatch, *, substrate):
    """Banca uma célula `cat/alabama/seed 0` com a proveniência de substrato dada."""
    import json

    from mtlcheck import paths
    monkeypatch.setenv("RUNS_ROOT", str(tmp_path / "runs"))
    cell_id = paths.cell_id("cat", "alabama", 0, 0)
    directory = paths.run_dir("estudo", cell_id)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "result.json").write_text(json.dumps({
        "science_fingerprint": "fp[]",
        "config": {"train": {}, "data": {}},
        "substrate": substrate,
    }))
    return directory


def _one_cell_wave(tmp_path):
    path = tmp_path / "w.toml"
    path.write_text('[wave]\nstudy = "estudo"\n\n[[cell]]\n'
                    'recipe = "recipes/v19/cat.toml"\nstates = ["alabama"]\nseeds = [0]\n'
                    'split_seed = 0\n')
    return path


def test_a_rebuilt_substrate_invalidates_a_banked_cell(tmp_path, monkeypatch) -> None:
    """O bug: o substrato é escolhido por ARTIFACTS_ROOT e a célula não o registrava, então
    reconstruí-lo e reexecutar a wave PULAVA tudo e reportava os números antigos como atuais."""
    from mtlcheck.train import wave

    _bank(tmp_path, monkeypatch, substrate={"checkin": {"identity": "aaaaaaaaaaaaaaaa"}})
    _SUBSTRATE_ON_DISK[0] = {"checkin": {"identity": "bbbbbbbbbbbbbbbb"}}
    ran = []
    outcomes = wave.run(_one_cell_wave(tmp_path),
                        execute=lambda c, d: (ran.append(c), (tmp_path, None))[1],
                        identify=_identify, resume=True)
    _SUBSTRATE_ON_DISK[0] = {}
    assert [o.status for o in outcomes] == ["ran"], "substrato trocado tem de invalidar a célula"
    assert len(ran) == 1


def test_the_same_substrate_still_skips(tmp_path, monkeypatch) -> None:
    """O contrapeso: se o substrato não mudou, a célula continua sendo pulada. Sem isto o teste
    acima passaria com uma implementação que invalida tudo."""
    from mtlcheck.train import wave

    _bank(tmp_path, monkeypatch, substrate={"checkin": {"identity": "aaaaaaaaaaaaaaaa"}})
    _SUBSTRATE_ON_DISK[0] = {"checkin": {"identity": "aaaaaaaaaaaaaaaa"}}
    outcomes = wave.run(_one_cell_wave(tmp_path),
                        execute=lambda c, d: pytest.fail("não devia rodar"),
                        identify=_identify, resume=True)
    _SUBSTRATE_ON_DISK[0] = {}
    assert [o.status for o in outcomes] == ["skipped"]


def test_a_celula_pulada_carrega_o_diretorio_dela(tmp_path, monkeypatch) -> None:
    """Sem `run_dir` na célula pulada, a escada do §2a mede o degrau errado.

    No degrau 2 o resume pula o piso inteiro — corretamente — e a dispersão do §2a lê os resultados
    a partir de `Outcome.run_dir`. Com `None` nas puladas ela enxergava só as células novas: media
    P=1 achando que media P=3. Antes do fail-closed isso parava a escada em SILÊNCIO, e ela nunca
    passaria de P=3 qualquer que fosse a dispersão — sem sintoma a jusante, porque em disco há três
    execuções e o gate da leitura aceita três. Achado pela escada em miniatura em 25-08.
    """
    from mtlcheck.train import wave

    _bank(tmp_path, monkeypatch, substrate={})
    outcomes = wave.run(_one_cell_wave(tmp_path),
                        execute=lambda c, d: pytest.fail("não devia rodar"),
                        identify=_identify, resume=True)
    assert [o.status for o in outcomes] == ["skipped"]
    assert outcomes[0].run_dir is not None, "a célula pulada some da dispersão da escada"
    assert (pathlib.Path(outcomes[0].run_dir) / "result.json").exists()


def test_a_cell_banked_before_the_field_existed_is_warned_about_not_re_run(tmp_path, monkeypatch,
                                                                          caplog) -> None:
    """A migração é assimétrica DE PROPÓSITO.

    Toda célula bancada antes de o campo existir cairia no ramo "não sei" — incluindo as SELADAS.
    Invalidá-las gastaria uma segunda leitura do conjunto de teste externo, que é o recurso mais
    caro do projeto. Então ausente avisa e não invalida; presente-e-diferente invalida.
    """
    import logging

    from mtlcheck.train import wave

    _bank(tmp_path, monkeypatch, substrate={})           # como as células de agosto
    _SUBSTRATE_ON_DISK[0] = {"checkin": {"identity": "bbbbbbbbbbbbbbbb"}}
    with caplog.at_level(logging.WARNING):
        outcomes = wave.run(_one_cell_wave(tmp_path),
                            execute=lambda c, d: pytest.fail("não devia rodar"),
                            identify=_identify, resume=True)
    _SUBSTRATE_ON_DISK[0] = {}
    assert [o.status for o in outcomes] == ["skipped"]
    assert "identidade do substrato" in caplog.text


def test_a_manifest_can_declare_its_substrate_and_refuses_a_different_one(tmp_path,
                                                                          monkeypatch) -> None:
    """Uma wave não constrói substrato e não vai construir. O que ela passa a fazer é RECUSAR.

    Sem isto, apontar ARTIFACTS_ROOT para o lugar errado produz números de outro substrato sob o nome
    deste estudo — que é a mesma família de erro do #20, um passo antes: lá o resume servia número
    velho, aqui a execução escreveria número novo e errado.
    """
    from mtlcheck.train import wave

    path = tmp_path / "w.toml"
    path.write_text('[wave]\nstudy = "estudo"\n\n'
                    '[substrate]\nrecipe = "recipes/v19/substrate.toml"\n'
                    '[substrate.identity]\ncheckin = "aaaaaaaaaaaaaaaa"\n\n'
                    '[[cell]]\nrecipe = "recipes/v19/cat.toml"\nstates = ["alabama"]\n'
                    'seeds = [0]\nsplit_seed = 0\n')

    _SUBSTRATE_ON_DISK[0] = {"checkin": {"identity": "bbbbbbbbbbbbbbbb"}}
    with pytest.raises(SystemExit, match="declara, para alabama, o substrato"):
        wave.run(path, execute=lambda c, d: pytest.fail("não devia rodar"),
                 identify=_identify, resume=False)
    _SUBSTRATE_ON_DISK[0] = {}


def test_um_substrato_sem_manifesto_recusa_em_vez_de_avisar(tmp_path, monkeypatch) -> None:
    """Declarar identidade e não poder conferir é PIOR que não declarar.

    Até 25-08 este ramo só avisava, e o buraco era concreto: o `ARTIFACTS_ROOT` de nome óbvio no A40
    era um andaime de symlinks para OUTRO engine, sem manifest.json. A wave teria rodado sobre o
    substrato errado sob o nome do estudo — com a garantia escrita no manifesto e ninguém a conferir.
    """
    from mtlcheck.train import wave

    path = tmp_path / "w.toml"
    path.write_text('[wave]\nstudy = "estudo"\n\n'
                    '[substrate]\n[substrate.identity]\ncheckin = "aaaaaaaaaaaaaaaa"\n\n'
                    '[[cell]]\nrecipe = "recipes/v19/cat.toml"\nstates = ["alabama"]\n'
                    'seeds = [0]\nsplit_seed = 0\n')

    _SUBSTRATE_ON_DISK[0] = {"checkin": {}}                 # existe, mas sem identidade
    with pytest.raises(SystemExit, match="não tem manifest.json"):
        wave.run(path, execute=lambda c, d: pytest.fail("não devia rodar"),
                 identify=_identify, resume=False)
    _SUBSTRATE_ON_DISK[0] = {}


def test_the_declared_substrate_matching_lets_the_wave_run(tmp_path, monkeypatch) -> None:
    """O contrapeso: declarar o substrato certo não pode impedir a execução. Sem este teste, uma
    implementação que recusa sempre passaria no de cima."""
    from mtlcheck.train import wave

    path = tmp_path / "w.toml"
    path.write_text('[wave]\nstudy = "estudo"\n\n'
                    '[substrate]\n[substrate.identity]\ncheckin = "aaaaaaaaaaaaaaaa"\n\n'
                    '[[cell]]\nrecipe = "recipes/v19/cat.toml"\nstates = ["alabama"]\n'
                    'seeds = [0]\nsplit_seed = 0\n')
    monkeypatch.setenv("RUNS_ROOT", str(tmp_path / "runs"))

    _SUBSTRATE_ON_DISK[0] = {"checkin": {"identity": "aaaaaaaaaaaaaaaa"}}
    ran = []
    outcomes = wave.run(path, execute=lambda c, d: (ran.append(c), (tmp_path, None))[1],
                        identify=_identify, resume=False)
    _SUBSTRATE_ON_DISK[0] = {}
    assert [o.status for o in outcomes] == ["ran"] and len(ran) == 1


def test_a_manifest_without_the_block_behaves_as_before(tmp_path, monkeypatch) -> None:
    """Todos os manifestos existentes omitem o bloco; omiti-lo não pode mudar nada."""
    from mtlcheck.train import wave

    path = tmp_path / "w.toml"
    path.write_text('[wave]\nstudy = "estudo"\n\n[[cell]]\n'
                    'recipe = "recipes/v19/cat.toml"\nstates = ["alabama"]\nseeds = [0]\n'
                    'split_seed = 0\n')
    monkeypatch.setenv("RUNS_ROOT", str(tmp_path / "runs"))
    assert wave.declared_substrate(path) == {}

    _SUBSTRATE_ON_DISK[0] = {"checkin": {"identity": "qualquer-coisa"}}
    outcomes = wave.run(path, execute=lambda c, d: (tmp_path, None),
                        identify=_identify, resume=False)
    _SUBSTRATE_ON_DISK[0] = {}
    assert [o.status for o in outcomes] == ["ran"]


def test_a_multi_state_manifest_checks_EVERY_state(tmp_path, monkeypatch) -> None:
    """A primeira versão conferia `cells[0]` e mais nada.

    Numa wave de um estado isso basta. Numa campanha de seis, cinco substratos passariam sem
    conferência nenhuma — e a wave anunciaria que confere. Pior que não conferir, porque parece
    proteção.
    """
    from mtlcheck.train import wave

    path = tmp_path / "w.toml"
    path.write_text('[wave]\nstudy = "estudo"\n\n'
                    '[substrate.identity.alabama]\ncheckin = "aaaaaaaaaaaaaaaa"\n'
                    '[substrate.identity.texas]\ncheckin = "tttttttttttttttt"\n\n'
                    '[[cell]]\nrecipe = "recipes/v19/cat.toml"\n'
                    'states = ["alabama", "texas"]\nseeds = [0]\nsplit_seed = 0\n')

    # Alabama bate; o Texas do disco é OUTRO. Só a conferência por estado pega isto.
    def identify(cell):
        from mtlcheck import paths
        on_disk = {"checkin": {"identity": "aaaaaaaaaaaaaaaa" if cell.state == "alabama"
                                           else "XXXXXXXXXXXXXXXX"}}
        return paths.cell_id("cat", cell.state, cell.seed, cell.split_seed), "fp", on_disk

    with pytest.raises(SystemExit, match="para texas"):
        wave.run(path, execute=lambda c, d: pytest.fail("não devia rodar"),
                 identify=identify, resume=False)


def test_a_state_without_a_declaration_warns_instead_of_passing_silently(tmp_path, caplog) -> None:
    """Declaração parcial é legítima — permite lançar por estado conforme os substratos fecham — mas
    o estado sem declaração tem de aparecer, senão a wave anuncia conferência que não fez."""
    import logging

    from mtlcheck.train import wave

    path = tmp_path / "w.toml"
    path.write_text('[wave]\nstudy = "estudo"\n\n'
                    '[substrate.identity.alabama]\ncheckin = "aaaaaaaaaaaaaaaa"\n\n'
                    '[[cell]]\nrecipe = "recipes/v19/cat.toml"\n'
                    'states = ["alabama", "texas"]\nseeds = [0]\nsplit_seed = 0\n')
    import os
    os.environ["RUNS_ROOT"] = str(tmp_path / "runs")

    def identify(cell):
        from mtlcheck import paths
        return (paths.cell_id("cat", cell.state, cell.seed, cell.split_seed), "fp",
                {"checkin": {"identity": "aaaaaaaaaaaaaaaa"}})

    with caplog.at_level(logging.WARNING):
        wave.run(path, execute=lambda c, d: (tmp_path, None), identify=identify, resume=False)
    assert "não declara substrato para texas" in caplog.text


# ── o desenho tem de ser declarado (§10.5) ──────────────────────────────────────────────────────

def test_uma_celula_que_nao_declara_a_particao_e_recusada(tmp_path) -> None:
    """Omitir dava REPETIÇÃO em silêncio, e quatro manifestos deste repo rodaram assim sem dizer.

    A diferença não é cosmética: com partição por semente, o desvio entre execuções soma sorteio e
    inicialização em 1 grau de liberdade, e nenhuma análise a jusante consegue separá-los depois.
    """
    path = _manifest(tmp_path, '''
[wave]
study = "s"

[[cell]]
recipe = "recipes/v18/cat.toml"
states = ["alabama"]
seeds = [0, 1, 7, 100]
''')
    with pytest.raises(ValueError, match="não declara split_seed"):
        wave.load(path)


def test_a_particao_fixa_faz_replicas_e_per_seed_faz_repeticoes(tmp_path) -> None:
    def carregar(linha):
        return wave.load(_manifest(tmp_path, f'''
[wave]
study = "s"

[[cell]]
recipe = "recipes/v18/cat.toml"
states = ["alabama"]
seeds = [0, 1, 7]
{linha}
'''))[1]

    assert {c.split_seed for c in carregar("split_seed = 0")} == {0}
    assert {c.split_seed for c in carregar('split_seed = "per-seed"')} == {0, 1, 7}


def test_a_particao_dentro_de_cell_set_e_recusada(tmp_path) -> None:
    """Ali ela vira override de receita e colide com o argumento nomeado, num TypeError opaco."""
    path = _manifest(tmp_path, '''
[wave]
study = "s"

[[cell]]
recipe = "recipes/v18/cat.toml"
states = ["alabama"]
seeds = [0]
set = { split_seed = 3 }
''')
    with pytest.raises(ValueError, match="campo da célula"):
        wave.load(path)


# ── o eixo de partição (`partitions`) ───────────────────────────────────────────────────────────

def test_partitions_faz_o_produto_cartesiano_com_as_sementes(tmp_path) -> None:
    """O eixo de partição como eixo de primeira classe da wave.

    Antes disto, medir o eixo exigia um manifesto separado por coluna — foi assim que o §10.4 rodou
    (`s10_4_partition_axis.toml`, uma wave inteira só para `split_seed = 7`). `partitions = [0, 7]`
    declara as duas colunas num manifesto só, e cada (partição, semente) é uma célula própria.
    """
    path = _manifest(tmp_path, '''
[wave]
study = "s"

[[cell]]
recipe = "recipes/v19/cat.toml"
states = ["alabama"]
seeds = [0, 7]
partitions = [0, 7]
''')
    _, cells = wave.load(path)
    assert len(cells) == 4
    assert {(c.split_seed, c.seed) for c in cells} == {(0, 0), (0, 7), (7, 0), (7, 7)}


def test_uma_lista_de_uma_particao_so_equivale_ao_split_seed_fixo(tmp_path) -> None:
    """`partitions = [7]` e `split_seed = 7` têm de produzir células idênticas — se divergissem, a
    mesma matriz teria duas identidades conforme a grafia do manifesto."""
    def carregar(linha):
        return wave.load(_manifest(tmp_path, f'''
[wave]
study = "s"

[[cell]]
recipe = "recipes/v19/cat.toml"
states = ["alabama"]
seeds = [0, 7]
{linha}
'''))[1]

    assert carregar("partitions = [7]") == carregar("split_seed = 7")


def test_declarar_split_seed_e_partitions_juntos_e_recusado(tmp_path) -> None:
    """São o mesmo eixo dito duas vezes, e as duas declarações podem discordar — aí qual valeria?
    Nenhum dos dois é recusado pela guarda que já existia; os dois juntos, por esta."""
    path = _manifest(tmp_path, '''
[wave]
study = "s"

[[cell]]
recipe = "recipes/v19/cat.toml"
states = ["alabama"]
seeds = [0]
split_seed = 0
partitions = [0, 7]
''')
    with pytest.raises(ValueError, match="split_seed E partitions"):
        wave.load(path)


def test_partitions_vazio_ou_nao_inteiro_e_recusado(tmp_path) -> None:
    """Lista vazia declararia um eixo sem colunas; `"per-seed"` e escalares só existem na forma
    `split_seed`, e aceitá-los aqui em silêncio confundiria os dois desenhos de novo."""
    for linha in ("partitions = []", 'partitions = ["per-seed"]', "partitions = 7",
                  "partitions = [0, true]"):
        path = _manifest(tmp_path, f'''
[wave]
study = "s"

[[cell]]
recipe = "recipes/v19/cat.toml"
states = ["alabama"]
seeds = [0]
{linha}
''')
        with pytest.raises(ValueError, match="lista não-vazia de inteiros"):
            wave.load(path)


def test_partitions_com_particao_repetida_e_recusado(tmp_path) -> None:
    """`[0, 7, 0]` declararia a coluna 0 duas vezes: as células duplicadas correriam para o mesmo
    diretório e uma sobrescreveria a outra em silêncio."""
    path = _manifest(tmp_path, '''
[wave]
study = "s"

[[cell]]
recipe = "recipes/v19/cat.toml"
states = ["alabama"]
seeds = [0]
partitions = [0, 7, 0]
''')
    with pytest.raises(ValueError, match="repete partições"):
        wave.load(path)


def test_partitions_dentro_de_cell_set_e_recusado(tmp_path) -> None:
    """Mesma recusa do split_seed em [cell.set]: é campo da célula, não override de receita."""
    path = _manifest(tmp_path, '''
[wave]
study = "s"

[[cell]]
recipe = "recipes/v19/cat.toml"
states = ["alabama"]
seeds = [0]
split_seed = 0
set = { partitions = [0, 7] }
''')
    with pytest.raises(ValueError, match="campo da célula"):
        wave.load(path)


def test_a_guarda_de_duplicata_ve_atraves_do_eixo_de_particao(tmp_path) -> None:
    """A mesma célula grafada via `partitions` num bloco e via `split_seed` noutro é UMA célula, e
    tem de cair na recusa de duplicata — senão dois blocos correm para um diretório só."""
    path = _manifest(tmp_path, '''
[wave]
study = "s"

[[cell]]
recipe = "recipes/v19/cat.toml"
states = ["alabama"]
seeds = [0]
partitions = [0, 7]

[[cell]]
recipe = "recipes/v19/cat.toml"
states = ["alabama"]
seeds = [0]
split_seed = 7
''')
    with pytest.raises(ValueError, match="more than once"):
        wave.load(path)


def test_uma_celula_do_eixo_resolve_para_o_cell_id_com_a_particao(tmp_path) -> None:
    """A partição declarada via `partitions` entra na identidade pelo MESMO campo `split_seed` —
    `p{partição}s{semente}` — então duas colunas nunca dividem diretório, e uma célula do eixo com
    partição igual à de uma célula bancada resolve para a MESMA identidade (as 54 seladas ficam
    onde estão; `tests/test_campaign_manifests.py` pina isso pelo fingerprint)."""
    from mtlcheck.config import load_recipe

    path = _manifest(tmp_path, '''
[wave]
study = "s"

[[cell]]
recipe = "recipes/v19/cat.toml"
states = ["alabama"]
seeds = [0]
partitions = [0, 7]
''')
    _, cells = wave.load(path)
    resolvidos = {load_recipe(c.recipe, state=c.state, seed=c.seed,
                              split_seed=c.split_seed, **c.overrides).cell_id for c in cells}
    assert resolvidos == {"cat-alabama-p0s0", "cat-alabama-p7s0"}
