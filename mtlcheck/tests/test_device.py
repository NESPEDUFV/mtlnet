"""O device resolvido, e o que ele recusa a fingir que fez."""
def test_um_botao_declarado_e_ignorado_vai_para_o_artefato() -> None:
    """O `science_fingerprint` grava `compile = true` mesmo onde o device não compila.

    Sem este registro o artefato afirma um botão que o run não usou e o único vestígio é uma linha
    de log, que não sobrevive à execução. Descoberto em 25-08 ao validar a escada em MPS: o
    `result.json` trazia `compile = true` e `tf32 = true` com `device = mps` e `warnings = []`.
    """
    from mtlcheck import device as dev

    spec = dev.resolve(dev.Precision.FP32, prefer="cpu", compile_requested=True, tf32_requested=True)
    assert not spec.can_compile and not spec.can_tf32
    assert len(spec.unhonoured) == 2
    assert any("compile" in w for w in spec.unhonoured)
    assert any("tf32" in w for w in spec.unhonoured)

    # O contrapeso: quem não pede não recebe aviso.
    limpo = dev.resolve(dev.Precision.FP32, prefer="cpu")
    assert limpo.unhonoured == ()
