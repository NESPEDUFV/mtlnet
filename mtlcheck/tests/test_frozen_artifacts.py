"""TODA receita e TODO manifesto commitado resolvem para a identidade que tinham quando foram fixados.

Este teste substitui a vigilância instância-a-instância. Antes dele havia dois testes que pinavam
listas escritas à mão — 3 receitas num, 13 células noutro — e uma lista à mão só protege o que
alguém lembrou de colocar nela. Este percorre o repositório.

O que ele pega, e por que isso é a classe de erro mais cara aqui: um default em `config.py` que
alcança um artefato congelado. Aconteceu duas vezes em 2026-08-19, ambas a minutos de serem
executadas:

* mudar o default de `DataConfig.region_engine` moveu a resolução de `recipes/v18/cat.toml`, que
  não nomeia o campo. As células `cat` SELADAS viram stale, o `wave run` as retreina, e isso é uma
  segunda leitura do teste externo — o recurso mais caro do projeto.
* quase inverti o default de `Cell.save_predictions` pela mesma "harmonização". O resume re-executa
  uma célula que declara predições e não as tem, com o mesmo desfecho.

Quando este teste falhar, a pergunta NÃO é "atualizo o número?". É **"que default eu mexi, e ele
alcança um artefato que alguém já bancou?"**. Se alcança, o caminho é uma receita NOVA, não uma
edição — foi assim que a v19 nasceu.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import tomllib
from pathlib import Path

import pytest

from mtlcheck import paths
from mtlcheck.eval import analysis as analysis_mod
from mtlcheck.config import load_recipe, load_substrate_recipe
from mtlcheck.train import wave

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "tests/fixtures/frozen_artifacts.json"

STATE, SEED, SPLIT = "alabama", 0, 0


def _identities() -> dict[str, str]:
    """A identidade resolvida de cada artefato congelado do repositório."""
    out: dict[str, str] = {}
    for recipe in sorted(ROOT.glob("recipes/*/*.toml")):
        key = str(recipe.relative_to(ROOT))
        try:
            # DIGEST DE CONTEÚDO, não o nome do engine. Com o nome, mudar
            # `mae_poi_target_dim` de 8 para 7 — um campo que redefine o objetivo do pretexto —
            # não movia nada: verificado por mutação em 2026-08-19, o mutante passou.
            cfg = load_substrate_recipe(recipe)
            blob = json.dumps(dataclasses.asdict(cfg), sort_keys=True, default=str)
            out[key] = cfg.engine + "/" + hashlib.sha256(blob.encode()).hexdigest()[:12]
            continue
        except Exception:
            pass
        try:
            out[key] = load_recipe(recipe, state=STATE, seed=SEED, split_seed=SPLIT,
                                   inner_validation=True).science_fingerprint()[:12]
            continue
        except Exception:
            pass
        try:
            # Receita de ANÁLISE. Sem este ramo ela caía no `REFUSED:` abaixo, e o valor gravado era
            # o NOME DA EXCEÇÃO — independente do conteúdo do arquivo. `v19_headline.toml` estava
            # assim na fixture: parecia coberta, e editar δ não faria o alarme disparar. As três
            # leituras de ponte irreversíveis dependem desse fingerprint.
            out[key] = analysis_mod.load(recipe).fingerprint
        except Exception as exc:                              # receita que se recusa a carregar
            out[key] = f"REFUSED:{type(exc).__name__}"
    for manifest in sorted(ROOT.glob("studies/**/waves/**/*.toml")):
        key = str(manifest.relative_to(ROOT))
        study, cells = wave.load(manifest)
        prints = []
        for cell in cells:
            try:
                r = load_recipe(cell.recipe, state=cell.state, seed=cell.seed,
                                split_seed=cell.split_seed, **cell.overrides)
                prints.append(f"{r.cell_id}={r.science_fingerprint()[:12]}")
            except Exception as exc:
                prints.append(f"{cell.state}/{cell.seed}=REFUSED:{type(exc).__name__}")
        out[key] = f"{study}|" + ",".join(sorted(prints))
    return out


def test_the_walk_found_the_artifacts() -> None:
    """Sem isto, um glob quebrado faria o teste abaixo passar sem conferir nada."""
    found = _identities()
    assert sum(k.startswith("recipes/") for k in found) >= 8
    assert sum(k.startswith("studies/") for k in found) >= 15


@pytest.mark.skipif(not FROZEN.exists(), reason="baseline ainda não gravado")
def test_every_frozen_artifact_still_resolves_the_same() -> None:
    expected = json.loads(FROZEN.read_text())
    actual = _identities()

    moved = {k: (expected[k], actual[k]) for k in expected if k in actual and expected[k] != actual[k]}
    assert not moved, (
        "estes artefatos congelados mudaram de resolução:\n"
        + "\n".join(f"  {k}\n    era  {was}\n    virou {now}" for k, (was, now) in moved.items())
        + "\n\nA pergunta NÃO é 'atualizo o número'. É QUE DEFAULT VOCÊ MEXEU, e ele alcança um "
          "artefato que alguém já bancou? Se alcança, o caminho é uma receita NOVA — não uma edição.")

    gone = sorted(set(expected) - set(actual))
    assert not gone, (f"artefatos congelados sumiram: {gone}. Apagar uma receita citada por célula "
                      f"bancada quebra a proveniência dela; arquive em vez de apagar.")


def test_a_identidade_nao_depende_de_como_o_caminho_foi_grafado() -> None:
    """A mesma receita, três grafias, uma identidade.

    O caminho entra no `science_fingerprint`, e o `science_digest` hasheia nomes E valores. Grafá-lo
    como veio dava identidades diferentes conforme o chamador usasse relativo ou absoluto — e o
    absoluto carrega o caminho de montagem do repositório, então a identidade científica de uma
    receita mudava de máquina para máquina. Medido em 2026-08-24: `recipes/v19/cat.toml` dava
    `635f9f82598e` pelo relativo e `8489fe112ebd` pelo absoluto, com um terceiro valor no A40.

    O sintoma era o `test_frozen_artifacts` falhar só no A40 — um alarme que só passa na máquina onde
    o baseline foi gravado é um alarme que se aprende a ignorar, e este guarda as células seladas.
    """
    grafias = ["recipes/v19/cat.toml",
               "./recipes/v19/cat.toml",
               str(paths.repo_root() / "recipes/v19/cat.toml")]
    identidades = {load_recipe(g, state="alabama", seed=0, split_seed=0).science_fingerprint()
                   for g in grafias}
    assert len(identidades) == 1, f"três grafias, {len(identidades)} identidades: {identidades}"


def test_a_proveniencia_gravada_e_o_caminho_relativo_ao_repo() -> None:
    """E é o relativo que fica, porque é o que todo manifesto de wave grava."""
    r = load_recipe(str(paths.repo_root() / "recipes/v19/cat.toml"),
                    state="alabama", seed=0, split_seed=0)
    assert r.to_dict()["recipe"] == "recipes/v19/cat.toml"


def test_uma_receita_fora_do_repo_ainda_carrega(tmp_path) -> None:
    """Receita de teste ou de scratch mora fora da árvore; ela continua resolvendo."""
    alvo = tmp_path / "solta.toml"
    alvo.write_text((paths.repo_root() / "recipes/v19/cat.toml").read_text())
    r = load_recipe(str(alvo), state="alabama", seed=0, split_seed=0)
    assert r.to_dict()["recipe"] == str(alvo)


#: A identidade da receita que produziu as TRÊS leituras de ponte de 2026-08-24. Elas são
#: irreversíveis e a carregam gravada; `gates.assert_calibrates` compara por igualdade.
PONTE_V19 = "a3e2854771f0868d"


def test_a_receita_que_leu_a_ponte_nao_pode_se_mover() -> None:
    """Editar `v19_headline.toml` in-place torna as três leituras irreversíveis INÚTEIS.

    Elas gravam `"fingerprint": "a3e2854771f0868d"` e não podem ser refeitas — reler a ponte é uma
    segunda leitura do teste externo. Até 24-08 nada no repositório protegia este valor: a fixture
    congelada guardava a string `REFUSED:KeyError` para este arquivo, porque `_identities` não sabia
    carregar receita de análise e gravava o NOME DA EXCEÇÃO — um valor independente do conteúdo.
    Parecia cobertura e não era.

    Uma análise diferente é um arquivo NOVO que declara `accepts_bridge_from`, nunca uma edição.
    """
    assert analysis_mod.load(ROOT / "recipes/analysis/v19_headline.toml").fingerprint == PONTE_V19

    # TODA leitura gasta, onde quer que esteja, contra a receita que ELA MESMA nomeia. A primeira
    # versão fixava o caminho `studies/v19_defence/leitura` e o fingerprint da ponte -- o que
    # protegia aquela campanha e quebrou quando ela foi arquivada e outra tomou o lugar. O
    # invariante não é "toda leitura é da ponte"; é "nenhuma receita se moveu debaixo de uma
    # leitura que já aconteceu".
    payloads = sorted((ROOT / "studies").glob("**/leitura/*.json"))
    if not payloads:
        pytest.skip("nenhuma leitura nesta árvore")
    for payload in payloads:
        bloco = json.loads(payload.read_text())["analysis"]
        receita = ROOT / bloco["path"]
        assert receita.exists(), f"{payload.name} cita {bloco['path']}, que sumiu da árvore"
        agora = analysis_mod.load(receita).fingerprint
        assert bloco["fingerprint"] == agora, (
            f"{payload.parent.parent.name}/{payload.name} foi lido sob a análise "
            f"{bloco['fingerprint']} e {bloco['path']} resolve hoje para {agora}. A receita se "
            f"moveu debaixo de uma leitura gasta, e a leitura não pode ser refeita.")

    # E as duas campanhas usam receitas DISTINTAS, que é o que separa os dois estimandos.
    usadas = {json.loads(p.read_text())["analysis"]["fingerprint"] for p in payloads}
    assert PONTE_V19 in usadas, "a leitura da ponte sumiu da árvore"
    assert len(usadas) >= 2, "as duas campanhas deveriam citar receitas diferentes"


def test_a_receita_escalada_muda_a_compra_e_NADA_mais() -> None:
    """A escada do §12.7 só pode trocar a tabela de compra. Se ela mexer em δ, nos níveis, no
    bootstrap, na família, no combinador ou nos gates, ela deixa de computar a mesma inferência —
    e herdar a leitura gasta da antecessora passa a misturar dois estimandos."""
    s4 = ROOT / "recipes/analysis/v19_headline_s4.toml"
    if not s4.exists():
        pytest.skip("a receita escalada não está nesta árvore")
    a = tomllib.loads((ROOT / "recipes/analysis/v19_headline.toml").read_bytes().decode())
    b = tomllib.loads(s4.read_bytes().decode())

    assert set(a) == set(b), "a escada não acrescenta nem remove seções"
    for secao in sorted(set(a) - {"replicates", "analysis"}):
        assert a[secao] == b[secao], f"[{secao}] mudou: {a[secao]} contra {b[secao]}"
    assert b["analysis"]["accepts_bridge_from"] == [PONTE_V19]
    assert {e: b["replicates"][e] for e in ("alabama", "arizona", "istanbul")} == \
           {e: a["replicates"][e] for e in ("alabama", "arizona", "istanbul")}, \
        "a ponte não escala — ela já estava em quatro"
