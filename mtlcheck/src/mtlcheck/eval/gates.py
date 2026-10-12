"""As guardas que decidem se uma leitura pode acontecer — e recusam ANTES de gastá-la.

Cada uma corresponde a uma regra do protocolo que, sem ela, valeria por acidente. Elas viviam em
`cli.py`, o que contrariava o mapa de `docs/README.md` e fazia com que um agente perguntando "por que
o `compare` recusou?" procurasse em `eval/` e não achasse nada.

A ordem em que `cli._run_family` as chama importa:

1. `assert_not_a_backdoor` — `--exploratory` não imprime célula selada não-lida;
2. `assert_replicates` — o conjunto de réplicas em disco é o que a receita pré-registra;
3. `assert_folds` — a célula cobre os folds do split canônico, não uma fração deles;
4. `bridge_band` — calibra a banda da ponte e aplica o gate de licença do §2, chamando
   `assert_calibrates` em cada payload oferecido.

**Nenhuma gasta leitura**: todas são anteriores a `headline.read_state`. É de propósito — o §12.4c
manda o gate ser aplicado ANTES de os estados grandes serem lidos, e uma licença reprovada que só
aparece embaixo de um número já gasto não recusa coisa nenhuma.

Elas recebem `state` e `bridge_reading` como valores, não um `Namespace`: a camada de avaliação não
deve conhecer o parser de argumentos.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from . import compare as compare_mod


def assert_not_a_backdoor(cells, state: str, confirmatory: bool) -> None:
    """`--exploratory` não pode ser a porta dos fundos para o teste externo.

    O bootstrap é determinístico pela semente da receita, então o exploratório sobre células SELADAS
    imprime exatamente os números que o confirmatório imprimiria — e não registra nada. Um flag
    digitado por engano gastaria um conjunto de forma invisível.

    Continua livre o que o exploratório existe para fazer: células não-seladas (desenvolvimento) e
    pares que o livro já registra como lidos (reprodução).
    """
    from . import ledger

    if confirmatory:
        return
    seladas = [c for c in cells if c.sealed and c.frame["state"].iloc[0] == state]
    # Sem identidade a célula escapava do filtro abaixo: a fechadura sem a porta.
    sem_identidade = sorted({str(c.meta.get("arm")) for c in seladas
                             if not c.science_fingerprint()})
    if sem_identidade:
        raise SystemExit(
            f"--exploratory sobre células SELADAS de {state} nos braços {sem_identidade}, e elas "
            f"não expõem identidade científica — não dá nem para conferir se já foram lidas. "
            f"Conserte a proveniência antes de olhar o número.")
    nao_lidas = sorted({fp for c in seladas
                        if (fp := c.science_fingerprint())
                        and ledger.was_read(fp, state) is None})
    if nao_lidas:
        raise SystemExit(
            f"--exploratory sobre células SELADAS de {state} que o livro não registra como lidas.\n"
            f"O bootstrap é determinístico: isto imprimiria exatamente o número da leitura "
            f"confirmatória, e não registraria nada. Se é para ler, leia — com --analysis. Se é "
            f"para explorar, explore sobre células não-seladas.\n"
            f"  identidades sem registro: {[fp[:12] for fp in nao_lidas]}")


def assert_replicates(cells, state: str, bracos: list[str], confirmatory: bool,
                     esperado: set[int] | None) -> None:
    """O conjunto de réplicas que a receita pré-registra para este estado."""
    if not confirmatory or not esperado:
        return
    for arm in bracos:
        # Das LINHAS, não do sidecar: o sidecar grava um `model_seed` só, o do primeiro fold.
        got = {int(v) for c in cells if c.meta.get("arm") == arm
               for v in c.frame["model_seed"].unique()}
        if got != esperado:
            raise SystemExit(
                f"{arm}/{state} tem réplicas {sorted(got)} e o §2 registra {sorted(esperado)}. O Δ é "
                f"a média sobre as réplicas, então um conjunto incompleto estima outra coisa.")


def assert_folds(cells, state: str, confirmatory: bool, folds: int) -> None:
    """Toda célula cobre os folds inteiros do split canônico.

    `--only-folds` é parâmetro de execução e não entra no fingerprint, e o resume da wave marca
    "feita" por result.json mais predições EXISTENTES, sem contar folds. Uma célula parcial entraria
    no OOF agrupado com uma fração dos usuários — outro estimando, sem sintoma no veredito.
    """
    if not confirmatory:
        return
    for cell in cells:
        arm = cell.meta.get("arm")
        for task in sorted({str(t) for t in cell.frame["task"].unique()}):
            vistos = {int(f) for f in cell.frame[cell.frame["task"] == task]["fold"].unique()}
            if vistos != set(range(folds)):
                raise SystemExit(
                    f"{arm}/{state}: a tarefa {task} cobre os folds {sorted(vistos)} e o split "
                    f"canônico tem {folds}. Uma célula parcial estima sobre uma fração dos "
                    f"usuários — outro estimando, sem sintoma no veredito.")


def assert_calibrates(payload: dict, caminho, receita) -> None:
    """Este payload pode calibrar ESTA análise?

    O hash do arquivo sozinho não serve: escalar a tabela de compra para S=4 — decisão que o próprio
    §2 MANDA tomar — produz uma receita nova, e as três leituras de ponte carimbadas com a antiga
    já foram gastas e não podem ser refeitas. Então a receita nova DECLARA de quais antecessoras
    aceita calibração (`accepts_bridge_from`, §12.7).

    Uma declaração sozinha seria fé. Por isso o que decide não é só o hash: os três parâmetros que
    o payload carrega — a margem, os níveis e a correção — são conferidos contra os desta receita.
    Uma "sucessora" que mexesse em δ e se declarasse compatível morre aqui, e o hash de bytes nunca
    olhou para esse eixo.
    """
    bloco = payload.get("analysis") or {}
    impressao = bloco.get("fingerprint")
    aceitos = {receita.fingerprint, *receita.accepts_bridge_from}
    if impressao not in aceitos:
        raise SystemExit(
            f"{caminho} foi produzido pela análise {impressao}, e esta aceita {sorted(aceitos)}. "
            f"Calibrar com outra receita mistura dois δ. Se ela É uma antecessora legítima, "
            f"declare-a em [analysis].accepts_bridge_from.")
    divergem = [f"{nome} {tinha!r} contra {agora!r}"
                for nome, tinha, agora in (("δ", bloco.get("delta"), receita.delta),
                                           ("níveis", bloco.get("levels"), list(receita.levels)),
                                           ("correção", bloco.get("correction"),
                                            receita.correction))
                if tinha is not None and tinha != agora]
    if divergem:
        raise SystemExit(
            f"{caminho} declara-se compatível pelo fingerprint, mas os parâmetros divergem: "
            f"{'; '.join(divergem)}. Uma antecessora só pode calibrar se computou a MESMA "
            f"inferência — a tabela de compra pode mudar, a margem não.")


def assert_ladder(cells, state: str, receita, confirmatory: bool,
                  raiz: str | None = None) -> dict | None:
    """§2a: as execuções que chegaram param a escada, ou a leitura é prematura.

    Sob `sd_source = "self"` a wave decide quantas execuções existem medindo a dispersão INTERNA. A
    leitura confere o outro lado: que o número em disco é um degrau da escada e que ele de fato
    resolve — senão alguém rodou a wave pela metade e está lendo o teste externo cedo demais, que é
    o gasto que não se desfaz.

    Devolve o degrau para o payload, ou `None` fora do modo confirmatório.
    """
    from . import pilot

    if receita.sd_source != "self" or not confirmatory:
        return None

    # POR BRAÇO. Unir os pares entre braços deixava passar joint com 3 execuções e cat com 2: o
    # `_align` intersecta em silêncio depois, e o Δ sai da média de 2 enquanto o payload carimba 3.
    por_arm: dict[str, set] = {}
    for c in cells:
        arm = str(c.meta.get("arm"))
        for _, linha in c.frame[["split_seed", "model_seed"]].drop_duplicates().iterrows():
            por_arm.setdefault(arm, set()).add((int(linha["split_seed"]), int(linha["model_seed"])))
    if len({frozenset(v) for v in por_arm.values()}) > 1:
        detalhe = " · ".join(f"{a}: {len(v)}" for a, v in sorted(por_arm.items()))
        raise SystemExit(
            f"{state}: os braços não têm as mesmas execuções ({detalhe}). O pareamento é POR "
            f"execução, e o alinhamento intersecta em silêncio — o Δ sairia da média das execuções "
            f"comuns enquanto o relatório carimba o número do braço mais completo.")
    execucoes = sorted(next(iter(por_arm.values()), set()))
    p = len(execucoes)
    if p - 1 < pilot.GL_MINIMO:
        raise SystemExit(
            f"{state} tem {p} execuções, e o §2a proíbe parar aí: com {p - 1} grau(s) de liberdade "
            f"não se estima dispersão nenhuma. O piso é triagem — a wave tinha de ter escalado. "
            f"Ler agora gasta o teste externo sobre um desenho que o próprio protocolo recusa.")
    if p not in pilot.ESCADA:
        raise SystemExit(
            f"{state} tem {p} execuções em disco e a escada do §2a tem os degraus "
            f"{list(pilot.ESCADA)}. Um número fora deles significa wave interrompida ou manifesto "
            f"editado à mão — e o Δ é a média sobre as execuções, então ler isto estima outra "
            f"coisa sem sintoma no veredito.")
    # Conjunto, não sequência: a ordem em que a wave rodou não é científica.
    esperado = pilot.sementes(p)
    if set(execucoes) != set(esperado):
        raise SystemExit(
            f"{state} tem as execuções {execucoes} e o degrau P={p} da escada é {esperado}. Os dois "
            f"botões andam juntos e a sequência é determinística; um par fora dela não é o desenho "
            f"que o §2a registra.")

    carimbo = _carimbo_da_escada(raiz, state, receita, p, execucoes)
    return {"executions": p, "pairs": [list(x) for x in execucoes], **carimbo}


def _carimbo_da_escada(raiz, state: str, receita, p: int, execucoes: list) -> dict:
    """O veredito que a wave gravou — sem ele, tudo acima confere a FORMA e não a DECISÃO.

    As três checagens anteriores aceitam qualquer truncamento que caia numa fronteira de degrau:
    uma wave morta logo depois da 3ª execução de uma subida que ia a P=4 deixa um disco idêntico ao
    de uma parada legítima em P=3. Idem um sync parcial truncado ali, e idem uma wave comprada
    contra outro δ — porque nada, até aqui, olhava a condição de parada.
    """
    import json
    from pathlib import Path

    # A RAIZ vem do CLI, que a recebeu do operador. Derivá-la das células exigiria uma chave de
    # sidecar que escritor nenhum declara — o contrato de `test_sidecar_contract` pega isso.
    destino = Path(raiz) / f"ladder_{state}.json" if raiz else None
    if destino is None or not destino.exists():
        raise SystemExit(
            f"{state}: as {p} execuções em disco têm a forma de um degrau, e não há `ladder_{state}"
            f".json` para dizer que a escada PAROU ali. Sem ele, uma wave morta numa fronteira de "
            f"degrau é indistinguível de uma resolvida, e este gate confere a forma do conjunto, "
            f"nunca a condição que o comprou. Re-rode a wave: com o resume, toda célula é pulada e "
            f"a escada regrava o veredito em minutos.")

    payload = json.loads(destino.read_text())
    if abs(float(payload["margem"]) - receita.delta) > 1e-12:
        raise SystemExit(
            f"{state}: a escada comprou as execuções contra δ={payload['margem']} e esta leitura usa "
            f"δ={receita.delta}. Uma margem maior para mais cedo — o desenho em disco não é o que "
            f"esta receita pediria.")
    gravadas = {tuple(x) for x in payload["execucoes"]}
    if gravadas != set(execucoes):
        raise SystemExit(
            f"{state}: o veredito registra {sorted(gravadas)} e o disco tem {execucoes}.")

    inacabados = sorted(t for t, v in payload["veredito"].items() if v["desfecho"] == "incompleto")
    if inacabados:
        raise SystemExit(
            f"{state}: a escada NÃO resolveu em {inacabados} — ela ainda ia escalar quando parou. "
            f"Ler agora gasta o teste externo sobre um desenho que o próprio §2a não fechou.")
    return {"ladder_outcome": {t: v["desfecho"] for t, v in sorted(payload["veredito"].items())},
            "ladder_margin": payload["margem"]}


def bridge_band(state: str, bridge_reading, receita, confirmatory: bool, *,
                tolerante: bool = False):
    """Valida as leituras de ponte e calibra a banda — ANTES de qualquer coisa ser computada.

    Antes ficava dentro do closure dos gates, que roda depois do veredito existir. Isso contradizia
    a §12.4c, que registra o gate de licença como aplicado ANTES da leitura dos grandes: uma licença
    reprovada não recusava nada, só saía impressa embaixo de um número já gasto.

    Os payloads vêm de arquivo escolhido pelo operador, então cada premissa é conferida. Nenhuma é
    paranoia: com agregação por máximo, omitir um estado-ponte só pode BAIXAR o sd, e um sd menor
    faz os gates dispararem menos e a licença passar mais fácil.
    """
    from . import escalation

    if receita.sd_source == "self":
        # A escada do §2a: o conjunto mediu a própria dispersão na validação interna e a wave já
        # parou onde ela mandou. Não há banda importada para calibrar, e portanto nada a conferir
        # aqui — o que a leitura confere é `assert_ladder`, sobre as execuções que chegaram.
        return None
    if state in receita.bridge_states or not confirmatory:
        return None
    if not bridge_reading:
        # Num ensaio a ausência é PENDÊNCIA e não erro: parar aqui esconderia se o resto do estado
        # está em ordem, que é justamente o que se quer saber antes de ir ler a ponte.
        if tolerante:
            return None
        raise SystemExit(
            f"{state} não é estado-ponte, e o §2 licencia o desenho dele contra a banda medida "
            f"na PONTE. Sem --bridge-reading os três gates de escalonamento não são computáveis, e "
            f"depois da leitura não há o que decidir.\n"
            f"Leia {', '.join(receita.bridge_states)} primeiro (--json), e passe os payloads.")

    por_tarefa: dict[str, dict[str, tuple[float, ...]]] = {}
    vistos: list[str] = []
    for caminho in bridge_reading:
        try:
            payload = json.loads(Path(caminho).read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"leitura de ponte ilegível em {caminho}: {exc}")
        estado = payload.get("state")
        if estado not in receita.bridge_states:
            raise SystemExit(f"{caminho} é do estado {estado!r}, que não está em bridge_states "
                             f"{list(receita.bridge_states)} — isso não calibra nada")
        if estado in vistos:
            raise SystemExit(f"{estado} aparece em duas leituras de ponte; a banda contaria o mesmo "
                             f"estado duas vezes")
        if not payload.get("confirmatory"):
            raise SystemExit(f"{caminho} é uma leitura EXPLORATÓRIA. A banda de réplica que licencia "
                             f"os grandes tem de sair de células seladas.")
        assert_calibrates(payload, caminho, receita)
        vistos.append(estado)
        for tarefa in payload.get("tasks", []):
            por_tarefa.setdefault(tarefa["task"], {})[estado] = (tuple(tarefa["seed_deltas"]),
                                                                 tuple(tarefa.get("seeds") or ()))

    faltando = sorted(set(receita.bridge_states) - set(vistos))
    if faltando:
        raise SystemExit(f"faltam as leituras de {faltando}. Com agregação por "
                         f"{receita.sd_aggregation}, uma ponte incompleta só pode subestimar a "
                         f"banda — os gates disparam menos e a licença passa mais fácil.")

    banda = {}
    for test in receita.tests:
        deltas = por_tarefa.get(test.task)
        if not deltas or set(deltas) != set(receita.bridge_states):
            raise SystemExit(f"as leituras de ponte não cobrem a tarefa {test.task!r} nos "
                             f"{len(receita.bridge_states)} estados")
        calibracao = escalation.calibrate(
            {e: d for e, (d, _) in deltas.items()}, aggregation=receita.sd_aggregation,
            seeds={e: s for e, (_, s) in deltas.items()}, folds=receita.folds)
        licenciado, motivo = escalation.licences_two_replicates(
            calibracao.sd, margin=receita.delta, ratio=receita.calibration_ratio)
        banda[test.task] = (calibracao, licenciado, motivo)

    # A licença responde "S=2 basta?". Uma vez que o estado esteja em S=4 a pergunta não tem mais
    # objeto: o §2 mandou comprar quatro e quatro foram compradas.
    reprovadas = sorted(t for t, (_, ok, _) in banda.items() if not ok)
    escalado = len(receita.replicates_by_state.get(state, ())) >= 4
    if reprovadas and not escalado:
        detalhe = " · ".join(f"{t}: {banda[t][2]}" for t in reprovadas)
        recado = (
            f"o gate de licenciamento do §2 REPROVA {state} em {reprovadas} ({detalhe}).\n"
            f"O §2 manda S=4 desde o início quando ele reprova, e a §12.4c registra que as sementes "
            f"{{1,100}} são treinadas ANTES da leitura deste estado.")
        if tolerante:
            # Num ensaio a recusa é a INFORMAÇÃO. Matar aqui esconderia o estado do resto do
            # estado, que é justamente o que se quer saber antes de comprar 27 h de GPU.
            print(f"  licença §2      ⚠ REPROVA em {reprovadas} ({detalhe}) — escale para S=4")
            return banda
        raise SystemExit(recado + " Recusando antes de gastá-la.")
    return banda


def as_dict(gates) -> dict:
    """Os campos MAIS os derivados: `asdict` não enxerga property, e `outcome` é o desfecho — a
    única coisa do bloco que alguém vai ler."""
    return {**dataclasses.asdict(gates), "fired": gates.fired, "outcome": gates.outcome}


def for_task(state: str, receita, banda, task: str, tiers) -> dict:
    """O desfecho dos gates do §2 para uma tarefa, com o envelope que os decidiu — e a banda do
    próprio estado ao lado dele (§12.9).

    Os gates auditam contra a banda da PONTE, medida nos três menores conjuntos. O diagnóstico
    `own_band` não decide nada: ele existe para que um leitor que encontre um carimbo `seed_limited`
    veja se ele veio da instabilidade da célula ou de um envelope importado de um conjunto uma ordem
    de grandeza menor. Medido em 24-08: em região o envelope é 0,3802 e a banda própria de Istambul
    é 0,0286 — 13×.
    """
    import statistics

    from . import escalation

    calibracao, licenciado, motivo = banda[task]
    proprios = tuple(tiers[compare_mod.NI_LEVEL].seed_deltas)
    propria = statistics.stdev(proprios) if len(proprios) > 1 else None
    return {"calibration": {"sd": calibracao.sd, "per_state": calibracao.per_state,
                            "aggregation": calibracao.aggregation},
            "own_band": {"sd": propria, "n_replicates": len(proprios),
                         "envelope_over_own": (calibracao.sd / propria
                                               if propria else None)},
            "licensed_for_two": licenciado, "licence_reason": motivo,
            "gates": as_dict(escalation.evaluate(
                state=state, task=task, tiers=tiers, sd=calibracao.sd,
                margin=receita.delta))}


__all__ = ["assert_ladder", "assert_not_a_backdoor", "assert_replicates", "assert_folds", "assert_calibrates", "bridge_band", "as_dict", "for_task"]
