

def test_o_mesmo_par_sob_OUTRO_estudo_e_um_evento_novo(tmp_path) -> None:
    """A colisão que teria feito o livro perder seis leituras.

    As células `(0,0)` da campanha nova resolvem para o MESMO `science_fingerprint` das da campanha
    da ponte — a receita de treino não mudou. Com a chave em `(fingerprint, state)`, `record` era
    idempotente e engolia a leitura nova: o livro afirmaria para sempre que aqueles pares foram
    lidos pela ponte, e uma reconciliação acharia 30 registros onde houve 36 células. Verificado nos
    seis pares de AL e IST em 25-08.
    """
    from mtlcheck.eval import ledger

    (tmp_path / "studies").mkdir()
    ledger.record("abc123", "alabama", study="v19_defence", recipe="r.toml", arms=("cat",),
                  root=tmp_path)
    ledger.record("abc123", "alabama", study="v19_ladder", recipe="r.toml", arms=("cat",),
                  root=tmp_path)
    livro = ledger.load(tmp_path)
    assert len(livro) == 2, "os dois eventos têm de estar no livro"
    assert {r.study for r in livro} == {"v19_defence", "v19_ladder"}

    # Idempotência DENTRO do estudo continua valendo.
    ledger.record("abc123", "alabama", study="v19_ladder", recipe="r.toml", arms=("cat",),
                  root=tmp_path)
    assert len(ledger.load(tmp_path)) == 2

    # E a pergunta CIENTÍFICA — "este teste externo já foi olhado?" — ignora o estudo.
    assert ledger.was_read("abc123", "alabama", root=tmp_path) is not None
    assert ledger.was_read("abc123", "alabama", study="outro", root=tmp_path) is None
