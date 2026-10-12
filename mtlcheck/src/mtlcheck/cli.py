"""Command-line entry points.

    mtlcheck check2hgi build --recipe recipes/v18/substrate.toml --state alabama
    mtlcheck train --recipe recipes/v18/cat.toml --state alabama --seed 0
    mtlcheck wave run studies/<x>/waves/<y>.toml
    mtlcheck score <run-dir>

Deliberately argparse, deliberately thin: the CLI resolves a configuration and hands it to a
library function. No science happens in this file, and none happens in a shell script — the
reference implementation kept its experiment matrix in 30+ shell drivers, one of which leaked an
`export` between cells and silently changed the precision of eight banked results.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import os
import sys
from pathlib import Path

from . import config as cfg
from . import device as dev
from . import paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mtlcheck", description=__doc__.split("\n")[0])
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    _add_check2hgi(sub)
    _add_data(sub)
    _add_train(sub)
    _add_wave(sub)
    _add_score(sub)
    _add_compare(sub)

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    return args.handler(args)


# ---------------------------------------------------------------- check2hgi

def _add_data(sub) -> None:
    """`mtlcheck data` — o que precisa existir antes de qualquer build."""
    p = sub.add_parser("data", help="baixar ou inventariar os dados primários")
    p.add_argument("action", choices=("check", "fetch"))
    p.add_argument("--state", default=None, choices=cfg.DATASETS,
                   help="baixa a geometria deste estado (TIGER/Line do Census)")
    p.add_argument("--city", default=None,
                   help="baixa esta cidade do Massive-STEPS (HuggingFace)")
    p.add_argument("--gowalla", action="store_true",
                   help="baixa o Gowalla BRUTO do SNAP — a matéria-prima, não os parquets por estado")
    p.add_argument("--all-shapefiles", action="store_true",
                   help="baixa a geometria de todos os estados que têm URL oficial")
    p.add_argument("--force", action="store_true", help="rebaixa mesmo se já estiver em disco")
    p.set_defaults(handler=_run_data)


def _run_data(args) -> int:
    from . import data_fetch

    log = logging.getLogger("mtlcheck.data")
    if args.action == "check":
        missing = data_fetch.check([args.state] if args.state else None)
        if not missing:
            print("tudo em disco.")
            return 0
        print(f"{len(missing)} pendência(s):\n")
        for item in missing:
            print(f"  · {item}\n")
        return 1

    did = False
    if args.all_shapefiles:
        for state in cfg.DATASETS:
            try:
                data_fetch.fetch_shapefile(state, force=args.force)
            except SystemExit as exc:
                log.warning("%s: %s", state, exc)
        did = True
    elif args.state:
        data_fetch.fetch_shapefile(args.state, force=args.force); did = True
    if args.city:
        data_fetch.fetch_city(args.city, force=args.force); did = True
    if args.gowalla:
        data_fetch.fetch_gowalla(force=args.force); did = True
    if not did:
        raise SystemExit("nada a fazer: passe --state, --city, --gowalla ou --all-shapefiles")
    return 0


def _add_check2hgi(sub) -> None:
    p = sub.add_parser("check2hgi", help="build a substrate (layer 1)")
    p.add_argument("action", choices=("build", "verify"))
    p.add_argument("--recipe", required=True)
    p.add_argument("--state", required=True, choices=cfg.DATASETS)
    p.add_argument("--device", default=None)
    p.add_argument("--out", default=None,
                   help="substrate directory (default: the artifacts root for engine/state)")
    p.add_argument("--corpus", default=None, help="override the corpus parquet")
    p.add_argument("--seed", type=int, default=None, help="override the recipe's repr_seed")
    p.add_argument("--epochs", type=int, default=None)
    p.add_argument("--no-deterministic", action="store_true",
                   help="reproduce the reference's non-reproducibility (see R16)")
    # The spatial scaffolding this project does not rebuild. Explicit arguments rather than derived
    # paths, so a run cannot quietly borrow another engine's artifacts.
    p.add_argument("--shapefile", default=None,
                   help="OPCIONAL — resolvido pelo estado quando omitido; passe para sobrepor. "
                        "census-tract shapefile; derives the region scaffolding here instead of "
                        "reading a preprocessed artifact")
    p.add_argument("--hierarchy", default=None,
                   help="preprocessed graph holding placeid_to_idx / poi_to_region / adjacency / "
                        "area / similarity — the deferred region spatial join")
    # Optional now: absent, the place graph and the code book are computed from the corpus and
    # written into the substrate's own temp/. Supplied, the HGI artifacts are read instead — which
    # is how a build reproduces against them. Either way the manifest carries a content digest, so
    # "which POI2Vec was this anchored to?" is answerable from the artifact rather than from a path
    # that may since have been overwritten (C22).
    p.add_argument("--poi2vec", default=None,
                   help="read HGI's POI2Vec csv instead of training the code book here")
    p.add_argument("--delaunay-places", default=None, help="read HGI's pois.csv instead")
    p.add_argument("--delaunay-edges", default=None, help="read HGI's edges.csv instead")
    p.set_defaults(handler=_run_check2hgi)


def _run_check2hgi(args) -> int:
    # Before torch loads. cuBLAS reads this when it initialises, so setting it later is too late and
    # the determinism guarantee silently degrades to a warning.
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

    import torch

    from .substrate import pipeline

    recipe = cfg.load_substrate_recipe(args.recipe)
    if args.seed is not None:
        recipe = dataclasses.replace(recipe, repr_seed=args.seed)
    if args.epochs is not None:
        recipe = dataclasses.replace(recipe, epochs=args.epochs)

    out_dir = Path(args.out) if args.out else paths.substrate_dir(recipe.engine, args.state)

    if args.action == "verify":
        return _verify_substrate(out_dir)

    # The spatial scaffolding is now BUILT here when it is not supplied — `--poi2vec` and the two
    # `--delaunay-*` flags read the old HGI engine's artifacts instead, which is how a build
    # reproduces against them. Only the region join still needs an argument.
    log = logging.getLogger("mtlcheck.substrate")

    # v19.1: `--shapefile` deixou de ser obrigatório. Sem ele, o shapefile do estado é RESOLVIDO
    # pelo nome (`paths.state_shapefile`) — antes era o único argumento não descobrível do sistema,
    # e exigia saber o código FIPS do estado. O flag continua funcionando como override.
    shapefile = args.shapefile
    if shapefile is None and args.hierarchy is None:
        try:
            shapefile = str(paths.state_shapefile(args.state))
        except (ValueError, FileNotFoundError) as exc:
            raise SystemExit(f"{exc}\n\nOu passe --shapefile explicitamente, ou --hierarchy para "
                             f"ler um join pré-processado; ver docs/ARCHITECTURE.md 1.1.") from None
        log.info("shapefile resolvido para %s: %s", args.state, shapefile)
    supplied = [v for v in (args.delaunay_places, args.delaunay_edges) if v is not None]
    if len(supplied) == 1:
        raise SystemExit("--delaunay-places and --delaunay-edges go together: pass both to read the "
                         "HGI artifacts, or neither to compute the place graph from the corpus.")

    device = torch.device(args.device) if args.device else dev._auto_device()
    manifest = pipeline.build(
        args.state, recipe,
        hierarchy_path=Path(args.hierarchy) if args.hierarchy else None,
        shapefile=Path(shapefile) if shapefile else None,
        poi2vec_path=Path(args.poi2vec) if args.poi2vec else None,
        delaunay_places_path=Path(args.delaunay_places) if args.delaunay_places else None,
        delaunay_edges_path=Path(args.delaunay_edges) if args.delaunay_edges else None,
        out_dir=out_dir, device=device,
        corpus_path=Path(args.corpus) if args.corpus else None,
        deterministic=not args.no_deterministic)

    training = manifest["training"]
    print(f"{args.state}/{recipe.engine}: loss {training['best_loss']:.5f} @{training['best_epoch']} "
          f"· seed {training['seed']} · {training['seconds']:.0f}s -> {out_dir}")
    return 0


def _verify_substrate(out_dir) -> int:
    """Check a substrate directory against its own manifest, without rebuilding it."""
    out_dir = Path(out_dir)
    manifest_path = out_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"no manifest at {manifest_path}", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text())
    problems: list[str] = []

    # v19: um layout só. Antes existiam dois — o substrato de região era bidirecional e escrevia só
    # o nível de região, e verificá-lo contra o layout de check-in produzia seis problemas espúrios.
    # Um substrato bancado dessa época ainda traz `checkin_level` no manifesto e vai falhar aqui;
    # isso é intencional, ele descreve uma forma que este código não constrói mais.
    expected = ["embeddings.parquet", "poi_embeddings.parquet", "region_embeddings.parquet",
                "input/next.parquet", "input/next_region.parquet", "temp/sequences_next.parquet",
                "place_index.parquet", "poi_to_region.parquet"]
    problems += [f"missing {name}" for name in expected if not (out_dir / name).exists()]

    if "checkin_level" in manifest:
        problems.append("este manifesto é de um substrato de região da era v18 (bidirecional, sem "
                        "nível de check-in); v19 constrói um substrato só — reconstrua-o")
    if not manifest.get("graph", {}).get("forward_only"):
        problems.append("the manifest says the graph was NOT forward-only — the inputs may be leaked")
    if manifest.get("training", {}).get("seed") is None:
        problems.append("no seed recorded: this substrate cannot be rebuilt")
    switches = manifest.get("switches", {})
    if not switches.get("deterministic_requested", switches.get("deterministic")):
        problems.append("built non-deterministically: rebuilding will not reproduce it (R16)")
    elif not switches.get("deterministic_achieved", True):
        problems.append("determinism was requested but NOT achieved (cuBLAS was already "
                        "initialised) — rebuilding may not reproduce it")

    rows = manifest.get("counts", {})
    if (out_dir / "input/next.parquet").exists():
        import pyarrow.parquet as pq
        actual = pq.ParquetFile(out_dir / "input" / "next.parquet").metadata.num_rows
        if rows.get("windows") not in (None, actual):
            problems.append(f"manifest claims {rows['windows']} windows, the table has {actual}")

    for problem in problems:
        print(f"  ✗ {problem}", file=sys.stderr)
    if problems:
        return 1
    print(f"{out_dir}: {rows.get('windows')} windows · {rows.get('regions')} regions · "
          f"seed {manifest['training']['seed']} · fingerprint "
          f"{manifest['training'].get('init_fingerprint', '?')} · ok")
    return 0


# ---------------------------------------------------------------- train

def _add_train(sub) -> None:
    p = sub.add_parser("train", help="train one cell (layer 3)")
    p.add_argument("--recipe", required=True, help="a frozen recipe under recipes/")
    p.add_argument("--state", required=True, choices=cfg.DATASETS)
    p.add_argument("--seed", type=int, required=True,
                   help="the MODEL seed: initialisation and shuffling, on a fixed partition")
    p.add_argument("--split-seed", type=int, default=None,
                   help="the PARTITION seed: which fold membership is drawn. Distinct from --seed "
                        "(NOMENCLATURE §1); required by --save-predictions")
    p.add_argument("--set", dest="overrides", action="append", default=[], metavar="KEY=VALUE",
                   help="override a recipe field; repeatable")
    p.add_argument("--no-grad-probe", dest="grad_probe", action="store_false", default=True,
                   help="turn the gradient-geometry probe OFF (joint only; on by default, ~14%% of "
                        "wall at the smallest state, less at larger ones)")
    # LIGADO por padrão sempre que a partição é explícita. Guardar as linhas do fold externo NÃO é
    # "ler o teste": a época já foi escolhida no inner-val, e o que fica em disco são PREDIÇÕES, não
    # um escore. Transformá-las em número é o `mtlcheck compare`, e é ESSE o ato racionado.
    #
    # O default era desligado, e o custo disso era real: as execuções de 19-08 não guardaram as
    # linhas, então ler o teste sobre elas exige RETREINAR. Guardar custa uma passada de validação
    # por fold e ~700 KB por célula; não guardar custa a execução inteira de novo.
    #
    # Sem `--split-seed` fica desligado com aviso, em vez de abortar: uma execução de depuração não
    # precisa da disciplina de duas sementes, e exigi-la ali só empurraria as pessoas para `--study
    # scratch` permanente.
    p.add_argument("--confirmatory", action="store_true",
                   help="pontua o fold EXTERNO ao fim e imprime o número final. Livre para um par "
                        "(receita, conjunto) que já teve `compare`; RECUSADO para um par novo, "
                        "porque aí seria a primeira leitura do teste — ver eval/ledger.py")
    p.add_argument("--save-predictions", dest="save_predictions", action="store_true", default=None,
                   help="persistir as predições por linha do fold externo (contrato de persistência "
                        "do protocolo). LIGADO por padrão quando há --split-seed")
    p.add_argument("--no-save-predictions", dest="save_predictions", action="store_false",
                   help="não persistir as predições — economiza uma passada de validação por fold")
    p.add_argument("--only-folds", default=None,
                   help="comma-separated fold ids of the canonical 5-split")
    p.add_argument("--study", default="adhoc", help="which study's runs/ directory to write into")
    p.add_argument("--device", default=None, choices=("cuda", "mps", "cpu"))
    p.add_argument("--dry-run", action="store_true",
                   help="resolve and print the configuration, then stop")
    p.set_defaults(handler=_run_train)


def _run_train(args) -> int:
    overrides = cfg.parse_set(args.overrides)
    overrides.update(state=args.state, seed=args.seed)
    if not args.grad_probe:
        overrides["grad_geometry"] = False
    if args.split_seed is not None:
        overrides["split_seed"] = args.split_seed
    resolved = cfg.load_recipe(args.recipe, **overrides)

    spec = dev.resolve(
        resolved.train.precision,
        prefer=args.device,
        compile_requested=resolved.train.compile,
        tf32_requested=resolved.train.tf32,
    )

    log = logging.getLogger("mtlcheck.train")
    log.info("cell %s · %s", resolved.cell_id, dev.describe(spec))
    log.info("config %s from %s", resolved.fingerprint(), resolved.recipe)

    if getattr(args, "confirmatory", False):
        _assert_reproduction_not_first_read(resolved, log)

    if args.dry_run:
        json.dump(resolved.to_dict(), sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    run_dir, _ = _train_cell(resolved, study=args.study, spec=spec,
                             only_folds=args.only_folds,
                             capture_predictions=args.save_predictions)
    if getattr(args, "confirmatory", False):
        _report_outer(resolved, run_dir, log)
    return 0


def _assert_reproduction_not_first_read(resolved, log) -> None:
    """`--confirmatory` só reproduz o que já foi lido. Um par novo é recusado ANTES do treino.

    A checagem vem antes porque recusar depois de horas de GPU é a mesma informação pelo pior preço.
    """
    from .eval import ledger

    fingerprint = resolved.science_fingerprint()
    entry = ledger.was_read(fingerprint, resolved.train.state)
    if entry is None:
        raise SystemExit(
            f"--confirmatory recusado: o par (receita {fingerprint[:12]}, {resolved.train.state}) "
            f"NUNCA teve o teste externo lido, então isto seria a PRIMEIRA leitura — e primeira "
            f"leitura é o ato racionado, que passa pelo `mtlcheck compare` com a família inteira e "
            f"a correção de multiplicidade.\n\n"
            f"  · para desenvolver, rode sem o flag: sai a validação interna, que não gasta nada;\n"
            f"  · para gastar a leitura deste par de propósito: treine, depois `mtlcheck compare`.\n\n"
            f"⚠ ATENÇÃO — 'ausente do livro' NÃO significa 'nunca lido'. O livro começou a existir em "
            f"2026-08-21; a leitura selada de alabama/arizona/istanbul aconteceu em 2026-08-18, sob "
            f"receitas v18, e NÃO está registrada porque aquelas células antecedem o campo de "
            f"fingerprint e preenchê-las exigiria inventar identidades. Antes de tratar este par "
            f"como novo, confira studies/porting_validation/SEALED_BRIDGE_READ.md.\n\n"
            f"Ver docs/POR_QUE_O_TESTE_ESPERA.md.")
    log.info("confirmatory: reproduzindo o par lido em %s (estudo %s) — não gasta leitura",
             entry.on, entry.study)


def _report_outer(resolved, run_dir, log) -> None:
    """O número final, do fold externo, impresso ao fim da execução."""
    from .eval import estimands, predictions as predictions_mod

    path = run_dir / "predictions.parquet"
    if not path.exists():
        log.warning("confirmatory: sem predictions.parquet em %s — nada a pontuar", run_dir)
        return
    import pandas as pd

    frame = pd.read_parquet(path)
    tasks = ("cat", "reg") if resolved.train.family.value == "joint" else (resolved.train.family.value,)
    print()
    print(f"=== TESTE EXTERNO · {resolved.cell_id} ===")
    for task in tasks:
        rows = frame[frame["task"] == task] if "task" in frame.columns else frame
        value = estimands.pooled_metric(rows, task)
        label = "macro-F1" if task == "cat" else "Acc@10"
        print(f"  {task:5s} {label:9s} {value * 100:.4f}   (OOF agrupado, fold externo)")
    print("  ⚠ reprodução de um par já lido; o veredito com IC e TOST sai do `mtlcheck compare`.")


def _cell_extra(resolved, *, study: str, arm: str, inputs, eval_stream: str) -> dict:
    """O sidecar de uma célula de predições — a metade que o chamador traz.

    Função e não dicionário embutido para que um teste possa montá-lo pelo MESMO código da produção.
    Enquanto era embutido, o único jeito de um teste escrever uma célula era inventar um `extra`
    paralelo — e o paralelo divergia, o que fez a suíte ficar verde sobre um caminho quebrado.
    """
    train_cfg = resolved.train
    return {
        # Conferido no CONSUMO (`predictions.assert_comparable`) — guarda em tempo de criação é
        # disciplina, e disciplina falha.
        "lineage": {
            "produced_by": "wave" if _wave_manifest_path[0] else "train",
            "manifest": _wave_manifest_path[0] or None,
            "substrate": inputs.provenance,
        },
        "study": study,
        "arm": arm or train_cfg.family.value,
        "family": train_cfg.family.value,
        "engine": train_cfg.engine,
        "recipe": str(resolved.recipe),
        "selection_stream": eval_stream,
        "inner_validation": bool(resolved.data.inner_validation),
        "inner_split_seed": int(resolved.data.inner_split_seed),
        "inner_splits": int(resolved.data.inner_splits),
        "n_categories": int(inputs.n_categories),
        "n_regions": int(inputs.n_regions),
        "keep_top_k": int(train_cfg.keep_top_k),
        "config_fingerprint": resolved.fingerprint(),
        # A identidade que o livro de leituras usa; a completa inclui telemetria. Ver `ledger.py`.
        "science_fingerprint": resolved.science_fingerprint(),
    }


def _train_cell(resolved, *, study: str, spec=None, device: str | None = None,
                only_folds: str | None = None, arm: str = "",
                capture_predictions: bool | None = None):
    """Train one cell and write its result. Returns (run_dir, metric or None).

    Shared by `train` and by `wave`, deliberately: the reference ran its matrix through shell
    drivers, so a cell inside a wave and the same cell run alone were different code paths, and one
    of them leaked an environment variable into the next.
    """
    from .config import TaskFamily
    from .data import dataset, splits
    from .train import result as result_mod
    from .train import runner

    log = logging.getLogger("mtlcheck.train")
    if spec is None:
        spec = dev.resolve(resolved.train.precision, prefer=device,
                           compile_requested=resolved.train.compile,
                           tf32_requested=resolved.train.tf32)

    # NOT `cfg` — that name is the config MODULE at file scope, and shadowing it here would make
    # every later module reference resolve to a TrainConfig.
    train_cfg = resolved.train
    joint = train_cfg.family is TaskFamily.JOINT
    inputs = dataset.load(train_cfg.state, train_cfg.engine, resolved.data,
                          need_region_tower=joint or train_cfg.family is TaskFamily.REG)
    # Two factors, two knobs. Falling back to the model seed keeps legacy cells running, but a
    # confirmatory cell (`capture_predictions`) refuses it below rather than banking a sidecar whose
    # two seed columns are secretly one number.
    partition_seed = (resolved.data.split_seed if resolved.data.split_seed is not None
                      else train_cfg.seed)
    if capture_predictions is None:
        # O default: ligado quando a partição é explícita. Ver a nota no argumento.
        capture_predictions = resolved.data.split_seed is not None
        if not capture_predictions:
            log.warning("sem --split-seed: as predições do fold externo NÃO serão guardadas, então "
                        "ler o teste sobre esta execução exigiria retreiná-la. Passe --split-seed "
                        "para bancar a matéria-prima.")
    if capture_predictions and resolved.data.split_seed is None:
        raise SystemExit(
            "--save-predictions needs an explicit --split-seed: without it the partition and the "
            "model initialisation carry the same integer, and the banked sidecar would report two "
            "experimental factors that cannot be told apart (NOMENCLATURE §1).")
    folds = splits.build(inputs.y_category, inputs.userid, split_seed=partition_seed,
                         n_splits=resolved.data.n_splits)
    splits.assert_user_disjoint(folds, inputs.userid)
    if resolved.data.inner_validation:
        folds = splits.build_inner(folds, inputs.y_category, inputs.userid,
                                   inner_split_seed=resolved.data.inner_split_seed,
                                   inner_splits=resolved.data.inner_splits)

    wanted = _selected_folds(only_folds, len(folds))
    fold_results = []
    captured = []
    # Resolved BEFORE the loop, because retained weights are written per fold as it goes: a cell
    # that dies at fold 4 keeps folds 0-3 rather than losing the lot.
    run_directory = paths.run_dir(study, f"{resolved.cell_id}-{arm}" if arm else resolved.cell_id)
    for fold in folds:
        if fold.index not in wanted:
            continue
        train = runner.train_joint_fold if joint else runner.train_fold
        outcome = train(resolved, inputs, fold, spec, capture_predictions=capture_predictions,
                        run_dir=run_directory)
        fold_results.append(outcome)
        if capture_predictions and outcome.rows is not None:
            captured += _fold_predictions(resolved, inputs, fold, outcome, folds, joint=joint)
        log.info("fold %d/%d done in %.0fs", fold.index + 1, len(folds), outcome.wall_seconds)

    aggregate = ({} if joint else runner.evaluate_folds(fold_results))
    cell = result_mod.build(resolved, fold_results, aggregate,
                            substrate=inputs.provenance, warnings=list(spec.unhonoured))

    # Predictions FIRST, then result.json. The wave's resume treats result.json as the done-marker,
    # so writing it before the rows meant a crash in between produced a cell that resumes forever
    # with no rows — Tier A silently loses that arm and only retraining recovers it. Ordering the
    # writes so the marker lands last makes the incomplete state re-runnable by construction, and
    # the resume check below it is the belt to this braces.
    if captured:
        from .eval import predictions as predictions_mod
        # Everything a later reader needs and cannot recover from the rows. `inner_split_seed`
        # because it is a second partition nobody would guess; the vocabulary sizes because macro-F1
        # and top-k are both denominators over them, and a comparison across two sizes is not one.
        predictions_mod.write(run_directory, captured,
                              extra=_cell_extra(resolved, study=study, arm=arm, inputs=inputs,
                                                eval_stream=fold_results[0].eval_stream))

    from .train import checkpoints as ckpt_mod
    ckpt_mod.write_manifest(
        run_directory, [r.checkpoints for r in fold_results],
        policy=train_cfg.retain_checkpoints,
        extra={"cell_id": resolved.cell_id, "config_fingerprint": resolved.fingerprint()})

    written = cell.write(run_directory)
    log.info("wrote %s", written)

    # Human-facing artifacts and the index, written ONCE after the folds — never inside the loop,
    # which is what made the reference's tracking layer its largest training slowdown.
    from .train import records, report as report_mod
    report_mod.write(run_directory, resolved, fold_results, aggregate,
                     seal_outer=capture_predictions)

    records.record(paths.runs_root(), study, resolved, aggregate,
                   run_dir=run_directory, wall_seconds=sum(r.wall_seconds for r in fold_results),
                   arm=arm, eval_stream=fold_results[0].eval_stream)
    if aggregate:
        log.info("%s: %.4f +/- %.4f over %d folds (lane: %s)", aggregate["metric"],
                 aggregate["mean"] * 100, aggregate["std"] * 100, aggregate["n_folds"],
                 aggregate["lane"])
    return run_directory, (aggregate.get("mean") if aggregate else None)


def _fold_predictions(resolved, inputs, fold, outcome, folds, *, joint: bool = False):
    """Assemble one fold's rows for the persistence contract.

    `userid` and `window_id` come from the fold's own validation indices, in the order the loader
    produced them — validation never shuffles, so row i of the metrics is row i of `fold.val`. That
    alignment is the whole contract: a mismatch here would attribute one user's prediction to
    another and no downstream check could see it.
    """
    import numpy as np

    from .config import TaskFamily
    from .eval import predictions as predictions_mod

    cfg = resolved.train
    val = np.asarray(fold.val)
    rows = outcome.rows

    def build(task: str, rows_for_task: dict, epoch: int):
        if len(val) != len(rows_for_task["y_true"]):
            raise ValueError(f"fold {fold.index} {task}: {len(val)} validation rows but "
                             f"{len(rows_for_task['y_true'])} predictions — something reordered")
        labels = inputs.y_region if task == "reg" else inputs.y_category
        train_labels = frozenset(int(v) for v in np.unique(labels[np.asarray(fold.train)]))
        return predictions_mod.FoldPredictions(
            state=cfg.state, arm=cfg.family.value, task=task,
            split_seed=int(resolved.data.split_seed),
            partition_hash=predictions_mod.partition_hash(folds),
            model_seed=cfg.seed, fold=fold.index, selected_epoch=int(epoch),
            userid=inputs.userid[val], window_id=val,
            y_true=rows_for_task["y_true"], y_pred=rows_for_task["y_pred"],
            rank_of_true=rows_for_task["rank_of_true"], train_labels=train_labels,
            **{k: rows_for_task[k] for k in predictions_mod.DISTRIBUTION_COLUMNS
               if k in rows_for_task},
            # Sealed exactly when an inner-validation split chose the checkpoint. Read from the fold
            # rather than from a flag, so the claim cannot drift from what actually happened.
            sealed=fold.sealed)

    if joint:
        # ONE checkpoint, two tasks, the same selected epoch on both — which is the property that
        # makes "one model, one forward, N tasks" a claim about a model rather than about a pair.
        epoch = rows["epoch"]
        return [build("cat", rows["cat"], epoch), build("reg", rows["reg"], epoch)]

    is_region = cfg.family is TaskFamily.REG
    return [build("reg" if is_region else "cat", rows, int(outcome.selection["epoch"]))]


def _selected_folds(spec: str | None, n_folds: int) -> set[int]:
    """`--only-folds 1,3` selects folds of the CANONICAL split, 1-based on the CLI.

    The split is always built at its full size, so fold k is the same fold whether it runs alone or
    in sequence. Building a smaller split instead would redraw every fold.
    """
    if spec is None:
        return set(range(n_folds))
    chosen = {int(part) - 1 for part in spec.split(",") if part.strip()}
    invalid = {c + 1 for c in chosen if not 0 <= c < n_folds}
    if invalid:
        # ValueError, not SystemExit: inside a wave this runs per cell, and `wave.run` contains an
        # Exception so one bad cell cannot sink the matrix. SystemExit derives from BaseException,
        # so a single malformed `folds` entry killed all 36.
        raise ValueError(f"--only-folds {sorted(invalid)} out of range for a {n_folds}-fold split")
    return chosen


# ---------------------------------------------------------------- wave

def _add_wave(sub) -> None:
    p = sub.add_parser("wave", help="run many cells from a declarative manifest")
    p.add_argument("action", choices=("run", "status", "plan"))
    p.add_argument("manifest")
    p.add_argument("--lane", default="local", choices=("local", "modal"))
    p.add_argument("--device", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-resume", action="store_true",
                   help="re-run cells that already have a result")
    p.add_argument("--margin", type=float, default=_MARGEM_PADRAO,
                   help="δ em pp; a escada do §2a para quando a meia-largura projetada cai abaixo "
                        "dela. Só é lido com `partitions = \"pilot\"`")
    p.add_argument("--preflight", action="store_true",
                   help="roda SÓ o piso da escada e para, reportando o piso de ruído do estimador e "
                        "quais degraus são alcançáveis. É a checagem barata que responde 'esta "
                        "campanha pode resolver?' antes de comprometer as horas")
    p.set_defaults(handler=_run_wave)


def _run_wave(args) -> int:
    from .train import wave as wave_mod

    if args.action == "plan":
        study, cells = wave_mod.load(args.manifest)
        print(f"{study}: {len(cells)} cells")
        for cell in cells:
            print(f"  {cell.label}" + (f"  {cell.overrides}" if cell.overrides else ""))
        return 0

    if args.action == "status":
        return _wave_status(args.manifest)

    if args.lane == "modal":
        raise SystemExit("the modal lane is not implemented; run with --lane local")

    _wave_manifest_path[0] = args.manifest
    if wave_mod.is_pilot(args.manifest) and not args.dry_run:
        # §2a: o manifesto declara o piso e a escada decide o resto medindo a dispersão INTERNA.
        margem = _margem_da_escada(args)
        if args.preflight:
            return _preflight_escada(args, margem)
        outcomes = wave_mod.run_ladder(args.manifest, execute=_execute_cell,
                                       identify=_identify_cell, dispersao=_dispersao_interna,
                                       margem=margem, device=args.device,
                                       resume=not args.no_resume, ruido=_ruido_interno)
    else:
        outcomes = wave_mod.run(args.manifest, execute=_execute_cell, identify=_identify_cell,
                                device=args.device,
                                resume=not args.no_resume, dry_run=args.dry_run)
    return 1 if any(o.status == "failed" for o in outcomes) else 0


#: O default de `--margin`. Serve para distinguir "não passou" de "passou o mesmo valor".
_MARGEM_PADRAO = 0.4

def _margem_da_escada(args) -> float:
    """O δ da escada sai da receita de análise que o manifesto declara, não do `--margin`.

    O `--margin` continua existindo para exploração, e passá-lo junto de uma receita declarada é
    recusado: dois pré-registros do mesmo número, discordando em silêncio, é a situação que o
    arquivo congelado existe para impedir.
    """
    from .eval import analysis as analysis_mod
    from .train import wave as wave_mod

    caminho = wave_mod.declared_analysis(args.manifest)
    if caminho is None:
        logger = logging.getLogger("mtlcheck.train.wave")
        logger.warning("%s não declara `analysis` em [wave]; a escada usa --margin=%s, que é um "
                       "default de CLI e não pré-registro", args.manifest, args.margin)
        return args.margin
    receita = analysis_mod.load(caminho)
    if args.margin != _MARGEM_PADRAO and args.margin != receita.delta:
        raise SystemExit(
            f"{args.manifest} declara analysis={caminho} com δ={receita.delta}, e a linha de comando "
            f"passou --margin {args.margin}. Rodar assim compraria execuções contra uma margem que "
            f"a leitura não vai usar. Tire o --margin, ou aponte para outra receita.")
    logging.getLogger("mtlcheck.train.wave").info(
        "escada §2a: δ=%s, de %s (%s)", receita.delta, caminho, receita.fingerprint)
    return receita.delta


def _dispersao_interna(outcomes) -> dict:
    """O delta pareado por execução, medido na VALIDAÇÃO INTERNA — a entrada da escada do §2a.

    Interna e não externa de propósito: a escada decide quantas execuções existem ANTES da leitura
    única, e olhar o teste externo para decidir isso o gastaria. É a distinção que faz da escalada
    uma adaptação sobre parâmetro de perturbação (Kieser & Friede 2000; FDA 2019).

    Lê `result.json`, não predições: o bloco `selection` de cada fold carrega a métrica na época
    escolhida, que é exatamente o número da validação interna.
    """
    import json
    import statistics
    from collections import defaultdict

    def metrica(run_dir, arm: str, task: str):
        caminho = Path(run_dir) / "result.json"
        if not caminho.exists():
            return None
        folds = json.loads(caminho.read_text()).get("folds") or []
        vals = []
        for fo in folds:
            sel = fo.get("selection") or {}
            if arm == "joint":
                bloco = sel.get("joint_best") or {}
                campo = "cat_f1" if task == "cat" else "top10_indist"
                if campo in bloco:
                    vals.append(bloco[campo] * 100)
            elif arm == "reg":
                bloco = sel.get("joint_convention") or {}
                if "top10_indist" in bloco:
                    vals.append(bloco["top10_indist"] * 100)
            elif sel.get("metric") == "f1":
                vals.append(sel["value"] * 100)
        # Fail-closed na CONTAGEM. Um fold sem `joint_best` -- o gate `min_best_epoch` pode devolver
        # `joint = None` -- encolhia a série em silêncio, e a média saía sobre 4 folds enquanto a
        # guarda do `run_ladder` conferia execuções, não folds. Nos 180 folds de AL e IST está 5/5;
        # faltam quatro conjuntos.
        if vals and len(vals) != len(folds):
            raise SystemExit(
                f"{caminho}: o braço {arm}/{task} tem {len(vals)} folds com bloco `selection` de "
                f"{len(folds)} folds. A escada mediria a dispersão sobre uma amostra menor sem nada "
                f"falhar. Confira `min_best_epoch` e o seletor desta célula.")
        return vals or None

    # (state, execução) → braço → métrica por tarefa
    por_exec: dict = defaultdict(dict)
    for o in outcomes:
        if o.run_dir is None:
            continue
        chave = (o.cell.state, (o.cell.split_seed, o.cell.seed))
        for task in ("cat", "reg"):
            serie = metrica(o.run_dir, o.cell.arm or _familia_de(o.cell), task)
            if serie is not None:
                por_exec[chave][(o.cell.arm or _familia_de(o.cell), task)] = serie

    saida: dict = defaultdict(list)
    for (state, _execucao), bracos in sorted(por_exec.items()):
        for task in ("cat", "reg"):
            sj, sd_ = bracos.get(("joint", task)), bracos.get((task, task))
            j = statistics.fmean(sj) if sj else None
            d = statistics.fmean(sd_) if sd_ else None
            if j is not None and d is not None:
                saida[(state, task)].append(j - d)
    return dict(saida)


def _preflight_escada(args, margem: float) -> int:
    """Roda o PISO e para, dizendo se esta campanha pode resolver antes de ela comprometer as horas.

    Existe porque em 25-08 dois conjuntos subiram ao teto e o motivo -- o ruído do estimador
    excedendo o limiar dos degraus baixos -- era computável em minutos e ninguém tinha perguntado.
    Três coisas que já eram checáveis separadamente, agora numa invocação: a identidade do substrato,
    o piso de ruído contra os limiares, e o caminho de leitura.
    """
    from .eval import pilot
    from .train import wave as wave_mod

    log = logging.getLogger("mtlcheck.train.wave")
    log.info("PREFLIGHT: rodando só o piso (%d execuções) e parando", pilot.ESCADA[0])
    feitos = wave_mod.run_ladder(args.manifest, execute=_execute_cell, identify=_identify_cell,
                                 dispersao=_dispersao_interna, margem=margem, device=args.device,
                                 resume=not args.no_resume, escada=(pilot.ESCADA[0],),
                                 ruido=_ruido_interno)
    if any(o.status == "failed" for o in feitos):
        return 1

    piso = _ruido_interno(feitos)
    if not piso:
        log.error("PREFLIGHT: não deu para estimar o ruído — algum braço não produziu série por fold")
        return 1

    print(f"\nPREFLIGHT · δ={margem}")
    print(f"  {'degrau':>8}  {'sd que resolve':>15}")
    for p_ in pilot.ESCADA:
        print(f"  {'P=' + str(p_):>8}  {pilot.sd_maximo(p_, margem=margem):>15.4f}")
    print()
    bloqueado = False
    for (state, task), r in sorted(piso.items()):
        possiveis = [p_ for p_ in pilot.ESCADA if r <= pilot.sd_maximo(p_, margem=margem)]
        alvo = f"o mais barato alcançável é P={possiveis[0]}" if possiveis else "NENHUM degrau é alcançável"
        marca = "  " if possiveis and possiveis[0] <= pilot.ESCADA[1] else "⚠ "
        bloqueado |= not possiveis or possiveis[0] > pilot.ESCADA[1]
        print(f"  {marca}{state}/{task}: ruído do estimador {r:.4f} → {alvo}")
    print()
    if bloqueado:
        print("  ⚠ O RUÍDO DO MEDIDOR JÁ DECIDE O DESFECHO. A escada vai comprar execuções contra a")
        print("    dispersão do próprio estimador, e o degrau final está determinado por aritmética")
        print("    antes de a dispersão verdadeira importar. Ver EVALUATION_PROTOCOL §2a.")
    else:
        print("  o piso de ruído deixa os degraus baixos alcançáveis — a escada pode resolver cedo.")
    print("\n  Nada além do piso foi rodado. Ensaie a leitura antes de soltar a campanha:")
    print(f"    mtlcheck compare <runs>/<estudo> --analysis <receita> --state <conjunto> --dry-run")
    return 0


def _ruido_interno(outcomes) -> dict:
    """Quanto do que a escada mede é ruído do PRÓPRIO medidor, e não sensibilidade à partição.

    Dentro de uma execução o delta varia entre os folds; essa dispersão sobre √n_folds estima o
    erro-padrão da média daquela execução. Se ele se aproxima da dispersão ENTRE execuções, a escada
    está comprando execuções para vencer o ruído do estimador.

    Não entra na regra de parada — a regra é pré-registrada e usa o σ̂ observado. Isto é diagnóstico,
    e existe porque em 25-08 dois conjuntos subiram ao teto e ninguém sabia o porquê até depois de
    duas horas de GPU. Com a validação interna a 10 % dos usuários e uma métrica de região sobre
    ~1 100 classes, o piso de ruído sozinho já excedia o limiar dos degraus 2, 3 e 4: o teto estava
    decidido por aritmética antes da primeira execução terminar.

    ⚠ Devolve apenas DISPERSÃO. A média dos deltas nunca sai daqui — a dispensa de correção de α do
    §2a depende de a regra ser cega ao efeito, e isso vale para todo diagnóstico.
    """
    import json
    import math
    import statistics
    from collections import defaultdict

    def serie(run_dir, arm: str, task: str):
        caminho = Path(run_dir) / "result.json"
        if not caminho.exists():
            return None
        vals = []
        for fo in json.loads(caminho.read_text()).get("folds") or []:
            sel = fo.get("selection") or {}
            if arm == "joint":
                bloco = sel.get("joint_best") or {}
                campo = "cat_f1" if task == "cat" else "top10_indist"
                if campo in bloco:
                    vals.append(bloco[campo] * 100)
            elif arm == "reg":
                bloco = sel.get("joint_convention") or {}
                if "top10_indist" in bloco:
                    vals.append(bloco["top10_indist"] * 100)
            elif sel.get("metric") == "f1":
                vals.append(sel["value"] * 100)
        return vals or None

    por_exec: dict = defaultdict(dict)
    for o in outcomes:
        if o.run_dir is None:
            continue
        arm = o.cell.arm or _familia_de(o.cell)
        for task in ("cat", "reg"):
            s_ = serie(o.run_dir, arm, task)
            if s_:
                por_exec[(o.cell.state, (o.cell.split_seed, o.cell.seed))][(arm, task)] = s_

    saida: dict = defaultdict(list)
    for (state, _), bracos in sorted(por_exec.items()):
        for task in ("cat", "reg"):
            sj, sd_ = bracos.get(("joint", task)), bracos.get((task, task))
            if not sj or not sd_ or len(sj) != len(sd_) or len(sj) < 2:
                continue
            por_fold = [a - b for a, b in zip(sj, sd_)]
            saida[(state, task)].append(statistics.stdev(por_fold) / math.sqrt(len(por_fold)))
    return {k: statistics.fmean(v) for k, v in saida.items() if v}


def _familia_de(cell) -> str:
    """A família de uma célula, do nome da receita — `recipes/v19/joint.toml` → `joint`."""
    return Path(cell.recipe).stem


def _execute_cell(cell, device):
    """Run one wave cell in THIS process. Returns (run_dir, metric or None).

    Goes through the same `_train_cell` the single-cell CLI uses, so a cell run inside a wave and the
    same cell run alone are the same code — which is the property the reference lost when its matrix
    lived in shell.
    """
    from .train import wave as wave_mod

    study, _ = wave_mod.load(_wave_manifest_path[0])
    resolved = _resolve_cell(cell)
    return _train_cell(resolved, study=study, device=device, only_folds=cell.folds,
                       arm=cell.arm, capture_predictions=cell.save_predictions)


def _identify_cell(cell) -> tuple[str, str, dict]:
    """A cell's run-directory name, config fingerprint and SUBSTRATE identity, without running it.

    Resolving the recipe here (rather than guessing from its filename) is what makes the resume
    check real: the directory comes from the FAMILY and both seeds, and the fingerprint is the one
    the manifest resolves to right now.

    The third element is what the substrate on disk looks like AT THIS MOMENT, so resume can compare
    it against what the banked cell recorded. Reading a manifest is cheap and torch-free, which is
    why it happens here rather than inside the wave.
    """
    from .substrate import identity as substrate_identity

    resolved = _resolve_cell(cell)
    base = resolved.cell_id
    current = {"checkin": substrate_identity.of(paths.substrate_dir(resolved.train.engine, cell.state))}
    if resolved.train.family is not cfg.TaskFamily.CAT:
        current["region"] = substrate_identity.of(
            paths.substrate_dir(resolved.data.region_engine, cell.state))
    return ((f"{base}-{cell.arm}" if cell.arm else base), resolved.science_fingerprint(), current)


def _resolve_cell(cell):
    return cfg.load_recipe(cell.recipe, state=cell.state, seed=cell.seed,
                           split_seed=cell.split_seed, **cell.overrides)


# Set by _run_wave before executing; the manifest names the study every cell writes under.
_wave_manifest_path: list[str] = [""]


def _wave_status(manifest: str) -> int:
    from .train import wave as wave_mod

    study, cells = wave_mod.load(manifest)
    done = missing = 0
    for cell in cells:
        cell_id, _, _ = _identify_cell(cell)
        result = paths.run_dir(study, cell_id)
        if (result / "result.json").exists():
            done += 1
        else:
            missing += 1
            print(f"  missing {cell.label}")
    print(f"{study}: {done}/{len(cells)} cells banked")
    return 0 if missing == 0 else 1


# ---------------------------------------------------------------- score

def _add_score(sub) -> None:
    p = sub.add_parser("score", help="re-score a finished run (CPU only)")
    p.add_argument("run_dir")
    p.add_argument("--compare", nargs=2, metavar=("ARM_A", "ARM_B"),
                   help="paired comparison between two families over their shared cells")
    p.add_argument("--state", default=None, help="restrict the comparison to one state")
    p.add_argument("--json", action="store_true", help="emit the summary as json")
    p.set_defaults(handler=_run_score)


def _run_score(args) -> int:
    from .train import score as score_mod

    banked = score_mod.collect(args.run_dir)
    if not banked:
        print(f"no result.json under {args.run_dir}", file=sys.stderr)
        return 1

    summary = score_mod.summarise(banked)
    perf = score_mod.performance(banked)

    if args.json:
        json.dump({"summary": summary, "performance": perf}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    print(f"{len(banked)} cells under {args.run_dir}\n")
    print(f"{'arm':28} {'metric':>10} {'± réplicas':>11} {'S':>3}  réplicas")
    for name, row in summary.items():
        print(f"{name:28} {row['mean']:>10.4f} {row['std_over_seeds']:>9.4f} "
              f"{row['n_seeds']:>3}  {row['seeds']}")

    print(f"\nwall: {perf['total_wall_seconds'] / 60:.1f} min total "
          f"({perf['total_train_seconds'] / 60:.1f} train, {perf['total_val_seconds'] / 60:.1f} val)")
    for row in perf["cells"]:
        share = row["unaccounted_share"]
        print(f"  {row['cell']:34} {row['wall_seconds']:>7.0f}s"
              + (f"  peak {row['peak_memory_gb']:>5.2f} GB" if row["has_diagnostics"] else "")
              + (f"  unaccounted {share * 100:>4.1f}%" if share is not None else "  (no diagnostics)")
              + (f"  best ep {row['mean_best_epoch']:.1f}" if row["mean_best_epoch"] else ""))

    if args.compare:
        arm_a, arm_b = args.compare
        result = score_mod.compare(banked, arm_a, arm_b, state=args.state)
        print(f"\n{result.describe()}")
        for warning in result.warnings:
            print(f"  ! {warning}")
    return 0


# ---------------------------------------------------------------- compare (stage 2)

def _add_compare(sub) -> None:
    """Stage 2 — the only place an OUTER-test number is ever computed.

    Deliberately not part of `score`, and deliberately a separate command. Stage 1 writes rows and
    no outer metric, so a wave cannot print the thing a reader must not see early; asking for the
    number is then a dated, logged act rather than a side effect of training. `score` still reports
    the inner-validation selection numbers and the wall-clock, which is what it is for.
    """
    p = sub.add_parser("compare", help="Tier A over banked predictions (reads the OUTER test)")
    p.add_argument("run_root", help="a study directory holding prediction cells")
    p.add_argument("--analysis", default=None,
                   help="receita de análise congelada (recipes/analysis/*.toml). Lê a FAMÍLIA "
                        "manchete do estado numa invocação, com Holm e a co-primária. Obrigatória "
                        "no modo confirmatório — δ e os níveis são pré-registro, não flag")
    p.add_argument("--arm-a", default=None, help="the reference arm, e.g. cat")
    p.add_argument("--arm-b", default=None, help="the arm under test, e.g. joint")
    p.add_argument("--task", default=None, choices=("cat", "reg"))
    p.add_argument("--state", required=True, choices=cfg.DATASETS)
    p.add_argument("--margin", type=float, default=0.4, help="the pre-specified margin, in pp")
    p.add_argument("--level", type=float, default=0.95,
                   help="two-sided interval coverage: 0.90 for the registered TOST")
    p.add_argument("--replicates", type=int, default=10_000)
    p.add_argument("--permutations", type=int, default=10_000)
    p.add_argument("--bridge-reading", action="append", default=[], metavar="JSON",
                   help="payload de uma leitura de estado-ponte. Obrigatório para os estados "
                        "grandes: os gates de S=2 do §2 saem da banda de réplica da ponte, então a "
                        "ordem ponte→grandes é dependência, não preferência")
    p.add_argument("--exploratory", action="store_true",
                   help="allow unsealed cells; the result is not confirmatory and says so")
    p.add_argument("--dry-run", action="store_true",
                   help="roda TODAS as guardas e não computa veredito nenhum. É como se confere que "
                        "a leitura vai passar antes de gastá-la")
    p.add_argument("--json", action="store_true")
    p.set_defaults(handler=_run_compare)

    p = sub.add_parser("conjunction",
                       help="§4a: em quantos conjuntos o efeito se sustenta (não lê parquet)")
    p.add_argument("payloads", nargs="+", metavar="JSON",
                   help="os payloads de `compare --json`, um por conjunto")
    p.add_argument("--analysis", required=True,
                   help="a MESMA receita congelada que produziu os payloads")
    p.add_argument("--json", action="store_true")
    p.set_defaults(handler=_run_conjunction)


def _assert_mode(args) -> None:
    """Ou receita de análise, ou os flags soltos — e o modo confirmatório exige a receita.

    Sem isto, `--margin 1.0` na leitura irreversível sairia com cara de resultado. Os flags soltos
    continuam existindo para a exploração de uma célula, que é o uso em que a margem é uma pergunta
    e não um pré-registro.
    """
    soltos = [nome for nome in ("arm_a", "arm_b", "task") if getattr(args, nome) is not None]
    padroes = {"margin": 0.4, "level": 0.95, "replicates": 10_000, "permutations": 10_000}
    soltos += [nome for nome, padrao in padroes.items() if getattr(args, nome) != padrao]
    if args.analysis and soltos:
        raise SystemExit(f"--analysis já declara a família e os parâmetros; {sorted(set(soltos))} "
                         f"seriam silenciosamente ignorados, e quem os digitou acreditaria que "
                         f"valeram")
    if args.analysis:
        return
    if not args.exploratory:
        raise SystemExit(
            "leitura confirmatória exige --analysis com uma receita congelada.\n"
            "δ, os níveis 90/95, os replicates e a composição da família são PRÉ-REGISTRO "
            "(EVALUATION_PROTOCOL §2, §3, §5) — como flag de linha de comando eles viram escolha de "
            "quem digita, e um `--margin 1.0` sai com cara de resultado.\n"
            "  · para a leitura da v19 sob a escada do §2a:  "
            "--analysis recipes/analysis/v19_ladder.toml\n"
            "  · a `v19_headline.toml` é a receita da PONTE, congelada para a campanha "
            "arquivada — sob a escada ela é recusada adiante\n"
            "  · para explorar uma célula: --exploratory com --arm-a/--arm-b/--task")
    faltando = [f"--{nome.replace('_', '-')}" for nome in ("arm_a", "arm_b", "task")
                if getattr(args, nome) is None]
    if faltando:
        raise SystemExit(f"sem --analysis, o modo exploratório precisa de {faltando}")


def _cells_for(cells, arm: str, state: str, task: str, confirmatory: bool,
               marginal: bool = False):
    """As células de um braço num estado, com as guardas de consumo já aplicadas.

    `marginal` tem de chegar aqui. A recusa de múltiplas partições é correta sob o estimando
    CONDICIONAL e é exatamente o desenho sob o marginal — e passá-la só no chamador de fora deixava
    a leitura da escada bloqueada por dentro, com a mensagem certa apontando para a saída certa.
    """
    from .eval import predictions as predictions_mod

    chosen = [c for c in cells if c.meta.get("arm") == arm and c.frame["state"].iloc[0] == state]
    if not chosen:
        available = sorted({c.meta.get("arm", "?") for c in cells})
        raise SystemExit(f"no cells for arm {arm!r} at {state}; have {available}")
    predictions_mod.assert_comparable(chosen, confirmatory=confirmatory,
                                      marginal=marginal)
    # §1: o canário de vazamento, POR FOLD, com os train_labels daquele fold. Recusa, não
    # rebaixamento — a regra diz "fails the run", e disse isso ANTES do lacre.
    if task == "reg":
        from .eval import leak_canary
        canarios = [c for cell in chosen
                    for c in leak_canary.per_fold(cell.frame, cell.meta, task="reg",
                                                  strict=confirmatory)]
        leak_canary.assert_no_leak(canarios, confirmatory=confirmatory)
    return chosen


def _run_family(args, cells) -> int:
    """A leitura da família manchete de UM estado — o modo confirmatório.

    Um estado por invocação e não os seis, porque os gates de S=2 dependem da banda de réplica
    medida na ponte: ler os grandes junto com ela torna os gates incomputáveis no momento em que
    eles decidem.
    """
    from .eval import gates
    import pandas as pd

    from .eval import analysis as analysis_mod, headline, predictions as predictions_mod

    receita = analysis_mod.load(args.analysis)
    confirmatory = not args.exploratory
    # Uma célula ilegível some da comparação em silêncio, e o Δ é a média das réplicas: perder uma
    # muda o estimando. `collect` já loga alto; aqui vira recusa.
    if confirmatory and getattr(predictions_mod.collect, "skipped", None):
        raise SystemExit(f"células ilegíveis sob {args.run_root}: "
                         f"{predictions_mod.collect.skipped}. Uma célula ausente muda o estimando "
                         f"sem mudar nada visível no veredito.")

    def frame_for(test):
        def rows(arm):
            chosen = _cells_for(cells, arm, args.state, test.task, confirmatory,
                                marginal=receita.sd_source == "self")
            frame = pd.concat([c.frame for c in chosen], ignore_index=True)
            return frame[frame["task"] == test.task]
        return rows(test.arm_a), rows(test.arm_b)

    def train_labels_for(test):
        return {arm: _train_labels(cells, arm, args.state)
                for arm in (test.arm_a, test.arm_b)}

    bracos = sorted({arm for test in receita.tests for arm in (test.arm_a, test.arm_b)})
    presentes = {c.meta.get("arm") for c in cells if c.frame["state"].iloc[0] == args.state}
    ausentes = [arm for arm in bracos if arm not in presentes]
    if ausentes:
        raise SystemExit(f"no cells for arm {ausentes[0]!r} at {args.state}; "
                         f"have {sorted(a for a in presentes if a)}")

    da_familia = [c for c in cells if c.meta.get("arm") in bracos
                  and c.frame["state"].iloc[0] == args.state]
    # Sobre a UNIÃO dos braços: `_cells_for` confere um braço por vez, e uma partição por braço
    # passaria em ambos. Pareado sobre partições diferentes readmite o componente de fold de ~1,2 pp
    # num teste de margem 0,4 — o §2 chama isso de fail-closed.
    predictions_mod.assert_comparable(da_familia, confirmatory=confirmatory,
                                      marginal=receita.sd_source == "self")
    gates.assert_not_a_backdoor(da_familia, args.state, confirmatory)
    escada = gates.assert_ladder(da_familia, args.state, receita, confirmatory,
                                 raiz=args.run_root)
    gates.assert_replicates(da_familia, args.state, bracos, confirmatory,
                     set(receita.replicates_by_state.get(args.state, ())))
    gates.assert_folds(da_familia, args.state, confirmatory, receita.folds)

    registravel = {arm: _identidades(cells, arm, args.state) for arm in bracos}
    if confirmatory:
        orfaos = sorted(arm for arm, ident in registravel.items() if not ident)
        if orfaos:
            raise SystemExit(
                f"os braços {orfaos} em {args.state} não expõem identidade científica, então esta "
                f"leitura não poderia entrar no livro. Recusando ANTES de computar o veredito.")

    banda = gates.bridge_band(args.state, args.bridge_reading, receita, confirmatory,
                         tolerante=getattr(args, "dry_run", False))
    if getattr(args, "dry_run", False):
        return _dry_run(args, receita, da_familia, registravel, bracos, banda, frame_for)

    leitura = headline.read_state(state=args.state, analysis=receita, frame_for=frame_for,
                                  train_labels_for=train_labels_for)
    # `escalonamento`, e não `gates`: rebindar o nome do módulo importado funcionava só porque o
    # lado direito avalia antes, e qualquer `gates.algo()` acrescentado abaixo explodiria.
    escalonamento = (None if banda is None
                     else {r.task: gates.for_task(args.state, receita, banda, r.task, r.tiers)
                           for r in leitura.tasks})
    payload = _family_payload(leitura, receita, confirmatory, escalonamento, escada)

    # Registra ANTES de imprimir: a leitura já aconteceu quando o veredito existe, e uma exceção de
    # formatação deixaria um estado gasto e não registrado.
    if confirmatory:
        _record_reads(registravel, args.state, Path(args.run_root).name, tuple(bracos))

    if args.json:
        json.dump(payload, sys.stdout, indent=2, default=float)
        sys.stdout.write("\n")
    else:
        _print_family(leitura, receita, confirmatory, escalonamento)
    return 0



def _run_conjunction(args) -> int:
    """§4a sobre estados JÁ lidos. Não abre parquet, então não gasta leitura nenhuma."""
    from .eval import analysis as analysis_mod, conjunction as conj

    receita = analysis_mod.load(args.analysis)
    payloads = conj.read_payloads(args.payloads)
    resultados = conj.compose(payloads, receita)

    if args.json:
        json.dump({"analysis": {"name": receita.name, "fingerprint": receita.fingerprint,
                                "combiner": receita.conjunction},
                   "states": [p["state"] for p in payloads],
                   "conjunctions": [dataclasses.asdict(c) for c in resultados]},
                  sys.stdout, indent=2, default=float)
        sys.stdout.write("\n")
        return 0

    estados = ", ".join(p["state"] for p in payloads)
    print(f"§4a · {len(payloads)} conjuntos ({estados}) · combinador {receita.conjunction} "
          f"· receita {receita.fingerprint}")
    for c in resultados:
        print(c.describe())
    for c in conj.excede_o_marginal(resultados):
        print(f"  ⚠ {c.task}/{c.family}: u* = {c.u} passa do marginal {c.marginal}. Em NI isto é "
              f"defeito (os dois saem do mesmo endpoint); em superioridade é a folga das duas "
              f"condições que o §3 exige do veredito e o p não carrega.")
    print("\n  u* é quantos conjuntos a afirmação CONJUNTA sustenta; a coluna marginal é quantos\n"
          "  a sustentam um a um. A folga entre as duas é o preço de afirmar as duas coisas juntas.")
    if receita.conjunction == "bonferroni":
        print("  Bonferroni porque a precondição de sobreposição de usuários do §4a falhou "
              "(§12.6c):\n  os conjuntos não são independentes, e Simes exigiria que fossem.")
    return 0


def _dry_run(args, receita, cells, registravel: dict, bracos: list[str], banda,
             frame_for) -> int:
    """Tudo que a leitura exige, conferido sem computar nada.

    Chega aqui depois de cada guarda do caminho real ter passado — receita validada, partição única
    sobre a união dos braços, lacre, linhagem, réplicas, identidade, e a exigência da ponte nos
    estados grandes. O que ele NÃO faz é tocar uma linha para virar número, que é o ato racionado.
    """
    print(f"{args.state} · ensaio de {receita.name} ({receita.fingerprint})")
    print(f"  receita        {receita.path}")
    print(f"  δ={receita.delta} · níveis {receita.ni_level}/{receita.superiority_level} · "
          f"{receita.replicates} replicates · {receita.permutations} permutations · "
          f"correção {receita.correction}")
    for test in receita.tests:
        print(f"  família        {test.label}")
    hashes = sorted({c.meta["partition_hash"] for c in cells})
    if receita.sd_source == "self":
        # Sob a escada há uma partição POR EXECUÇÃO, e anunciar "uma para os N braços" sobre um
        # conjunto de seis era o ensaio afirmando o desenho errado com o número certo ao lado.
        print(f"  partições      {len(hashes)}, uma por execução: "
              f"{', '.join(h[:8] for h in hashes)}")
    else:
        print(f"  partição       {hashes[0]} (uma para os {len(bracos)} braços)")
    for arm in bracos:
        sementes = sorted({int(v) for c in cells if c.meta.get("arm") == arm
                           for v in c.frame["model_seed"].unique()})
        linhas = sum(len(c.frame) for c in cells if c.meta.get("arm") == arm)
        print(f"  {arm:6s}         réplicas {sementes} · {linhas} linhas · "
              f"identidades {[fp[:12] for fp in sorted(registravel[arm])]}")
    rotulos = {arm: len(_train_labels(cells, arm, args.state)) for arm in bracos}
    print(f"  train_labels   {rotulos} (o canário do §1 precisa deles por tarefa e fold)")
    # O canário do §1 mora no `frame_for`, que a leitura real chama e o ensaio não chamava — um
    # estado com vazamento passava o ensaio e era recusado no meio da leitura, com metade computada.
    for test in receita.tests:
        frame_for(test)
    print("  canário §1     avaliado por fold nos dois braços, não disparou")

    if receita.sd_source == "self":
        # A escada do §2a substituiu a ponte: o conjunto mediu a própria dispersão. Sem este ramo o
        # ensaio caía no `else` e imprimia "PENDENTE — exige --bridge-reading", que sob a escada é
        # uma regra morta anunciada como bloqueio.
        pares = sorted({(int(a), int(b)) for c in cells
                        for a, b in zip(c.frame["split_seed"], c.frame["model_seed"])})
        print(f"  escada §2a     P={len(pares)} execuções {pares}")
        pendente = False
    elif args.state in receita.bridge_states:
        print("  ponte          este estado É a ponte — mede a banda que os grandes consomem")
        pendente = False
    elif banda is not None:
        for task, (calibracao, licenciado, motivo) in sorted(banda.items()):
            print(f"  ponte {task:4s}     {calibracao.describe()} · licencia S=2: {licenciado} "
                  f"({motivo})")
        pendente = False
    else:
        print("  ponte          ⚠ PENDENTE — este estado exige --bridge-reading (§2). Os dados "
              "estão em ordem; falta ler AL/AZ/IST antes.")
        pendente = True

    print(f"\n  {'GUARDAS DE DADOS PASSAM, FALTA A PONTE' if pendente else 'TODAS AS GUARDAS PASSAM'}"
          f". Nada foi lido — remova --dry-run para gastar a leitura.")
    return 0


def _train_labels(cells, arm: str, state: str) -> dict[str, list[int]]:
    saida: dict[str, list[int]] = {}
    for cell in cells:
        if cell.meta.get("arm") == arm and cell.frame["state"].iloc[0] == state:
            saida.update(cell.meta.get("train_labels") or {})
    return saida


def _family_payload(leitura, receita, confirmatory: bool, gates: dict | None = None,
                    escada: dict | None = None) -> dict:
    from .eval import compare as compare_mod

    return {
        "state": leitura.state, "confirmatory": confirmatory,
        "analysis": {"name": receita.name, "path": receita.path,
                     "fingerprint": receita.fingerprint, "delta": receita.delta,
                     "levels": list(receita.levels), "correction": receita.correction},
        "co_primary": {"verdict": leitura.co_primary, "reason": leitura.co_primary_reason},
        "escalation": gates, "ladder": escada,
        "tasks": [{
            "task": r.task, "arm_a": r.test.arm_a, "arm_b": r.test.arm_b,
            "pooled": r.pooled, "delta": r.tiers[0.90].delta,
            "bca_90": list(r.tiers[0.90].bca), "bca_95": list(r.tiers[0.95].bca),
            "percentile_90": list(r.tiers[0.90].percentile),
            "half_width_90": r.tiers[0.90].half_width,
            "p_ni": r.p_ni, "p_ni_adjusted": r.p_ni_adjusted, "alpha_local": r.alpha_local,
            "p_studentized": r.tiers[0.90].p_permutation,
            "p_unstudentized": r.tiers[0.90].p_permutation_raw,
            "verdict": r.verdict, "verdict_marginal": r.marginal.verdict,
            "delta_critical": dataclasses.asdict(r.critical),
            "tost_claimable": r.marginal.tost_claimable,
            "within_rerun_floor": r.marginal.within_rerun_floor,
            # §10.2: a única banda que encolhe com P. O intervalo manchete continua sendo o
            # bootstrap por usuário; esta vai AO LADO, e a escolha de qual é manchete foi feita
            # antes de qualquer leitura.
            "execution_band": compare_mod.banda_por_execucao(
                list(r.tiers[0.90].seed_deltas), margem=receita.delta),
            "sensitivity": r.sensitivity, "seed_deltas": list(r.tiers[0.90].seed_deltas),
            "seeds": list(r.tiers[0.90].seeds), "n_users": r.tiers[0.90].n_users,
            "intervals_disagree": r.tiers[0.90].intervals_disagree,
            "diagnostics": r.diagnostics, "warnings": r.tiers[0.90].warnings,
        } for r in leitura.tasks],
    }


def _print_family(leitura, receita, confirmatory: bool, gates: dict | None = None) -> None:
    print(f"{leitura.state} · família {receita.name} ({receita.fingerprint})"
          + ("" if confirmatory else "  [EXPLORATÓRIO]"))
    for r in leitura.tasks:
        print(f"  pooled {r.test.arm_a} {r.pooled[r.test.arm_a]:.4f} · "
              f"{r.test.arm_b} {r.pooled[r.test.arm_b]:.4f}")
        print(r.describe())
        print(f"      {r.marginal.describe()}")
        print("      sensibilidade: " + " · ".join(f"δ={m}: {v}" for m, v in r.sensitivity.items()))
        c = r.critical
        print(f"      δ crítico: não-inferior acima de {c.non_inferiority:+.4f} · inferior abaixo "
              f"de {c.inferiority:+.4f} · TOST a partir de {c.tost:.4f}")
        from .eval import compare as _cmp
        banda = _cmp.banda_por_execucao(list(r.tiers[0.90].seed_deltas), margem=receita.delta)
        if banda:
            print(f"      eixo de execução (§10.2): ±{banda['meia_largura']:.4f} sobre "
                  f"{banda['execucoes']} execuções ({banda['graus_de_liberdade']} gl) — a única "
                  f"banda que encolhe com P; a manchete acima é o bootstrap por usuário")
        diag = r.diagnostics
        print(f"      meia-largura {diag['half_width']:.4f} contra projetado "
              f"{diag['half_width_projected']} · MDE@{diag['mde_power']:.0%} {diag['mde']:.4f} · "
              f"ganho do pareamento {diag['pairing_gain']:.1f}×")
        if "min_users_per_class" in diag:
            print(f"      mínimo de usuários por classe: {diag['min_users_per_class']}")
            for linha in diag["per_class"]:
                print(f"        classe {linha['class']}: {linha['delta']:+.4f} pp "
                      f"({linha['f1_a']:.4f} → {linha['f1_b']:.4f}, {linha['users']} usuários)")
        for arm, valores in diag.get("region", {}).items():
            print(f"      {arm}: ood_fraction {valores['ood_fraction']:.4f} · "
                  f"ood_hit_rate {valores['ood_hit_rate']:.4f} · "
                  f"full {valores['top10_full']:.4f} · indist {valores['top10_acc_indist']:.4f}")
        if r.tiers[0.90].intervals_disagree:
            print("      ⚠ percentil e BCa discordam — a distribuição do bootstrap é assimétrica")
        if gates and r.task in gates:
            g = gates[r.task]
            print(f"      S=2 licenciado: {g['licensed_for_two']} ({g['licence_reason']})")
            print(f"      gates: {g['gates']['outcome']} · sinal "
                  f"{g['gates']['sign_disagreement']} · dispersão "
                  f"{g['gates']['spread_exceeded']} · veredito {g['gates']['verdict_shifts']}")
    print(f"  CO-PRIMÁRIA: {leitura.co_primary.upper()} — {leitura.co_primary_reason}")


def _record_reads(registravel: dict, state: str, study: str, arms: tuple[str, ...]) -> None:
    from .eval import ledger

    for identidades in registravel.values():
        for fingerprint, recipe in sorted(identidades.items()):
            ledger.record(fingerprint, state, study=study, recipe=recipe, arms=arms)
    gravado = {r.key() for r in ledger.load()}
    faltando = sorted(arm for arm, ident in registravel.items()
                      if any((fp, state, study) not in gravado for fp in ident))
    if faltando:
        raise SystemExit(
            f"A LEITURA FOI IMPRESSA ACIMA E OS BRAÇOS {faltando} NÃO ENTRARAM NO LIVRO. O teste "
            f"externo de {state} está gasto e o registro não sobreviveu. Registre à mão em "
            f"{ledger.LEDGER} antes de qualquer outra coisa.")


def _run_compare(args) -> int:
    from .eval import gates
    import pandas as pd

    from .eval import compare as compare_mod
    from .eval import estimands, predictions as predictions_mod

    _assert_mode(args)
    cells = predictions_mod.collect(args.run_root)
    if not cells:
        print(f"no prediction cells under {args.run_root}", file=sys.stderr)
        return 1
    if args.analysis:
        return _run_family(args, cells)

    def rows_for(arm: str) -> pd.DataFrame:
        chosen = _cells_for(cells, arm, args.state, args.task, not args.exploratory)
        frame = pd.concat([c.frame for c in chosen], ignore_index=True)
        return frame[frame["task"] == args.task]

    gates.assert_not_a_backdoor([c for c in cells if c.meta.get("arm") in (args.arm_a, args.arm_b)],
                           args.state, not args.exploratory)
    frame_a, frame_b = rows_for(args.arm_a), rows_for(args.arm_b)
    if frame_a.empty or frame_b.empty:
        raise SystemExit(f"task {args.task!r} has no rows in one of the arms")
    predictions_mod.assert_comparable(
        [c for c in cells if c.meta.get("arm") in (args.arm_a, args.arm_b)
         and c.frame["state"].iloc[0] == args.state],
        confirmatory=not args.exploratory)

    # Antes de existir número: uma célula sem identidade é recusada sem gastar a leitura.
    registravel = {arm: _identidades(cells, arm, args.state)
                   for arm in (args.arm_a, args.arm_b)}
    if not args.exploratory:
        orfaos = sorted(arm for arm, ident in registravel.items() if not ident)
        if orfaos:
            raise SystemExit(
                f"os braços {orfaos} em {args.state} não expõem identidade científica (nem no "
                f"sidecar, nem no result.json ao lado), então esta leitura não poderia entrar no "
                f"livro — e o livro é o que impede lê-la uma segunda vez como se fosse a primeira.\n"
                f"Recusando ANTES de computar o veredito: assim a leitura não é gasta.\n"
                f"Conserte a proveniência das células, ou passe --exploratory e assuma que o "
                f"número não é confirmatório.")

    tier = compare_mod.tier_a(frame_a, frame_b, task=args.task, level=args.level,
                              replicates=args.replicates, permutations=args.permutations)
    verdict = compare_mod.equivalence_from(tier, margin=args.margin)
    pooled = {arm: estimands.pooled_metric(frame, args.task) * 100
              for arm, frame in ((args.arm_a, frame_a), (args.arm_b, frame_b))}

    # Obrigatória no §3, e no payload também: quem usa `--json` monta a tabela.
    sensibilidade = {str(m): compare_mod.equivalence_from(tier, margin=m).verdict
                     for m in (0.2, 0.4, 1.0)}
    payload = {
        "state": args.state, "task": args.task, "arm_a": args.arm_a, "arm_b": args.arm_b,
        "confirmatory": not args.exploratory,
        "pooled": pooled, "delta": tier.delta, "level": tier.level,
        "percentile": list(tier.percentile), "bca": list(tier.bca),
        "p_studentized": tier.p_permutation, "p_unstudentized": tier.p_permutation_raw,
        "n_users": tier.n_users, "n_replicates_fit": tier.n_replicates_fit,
        "margin": args.margin, "verdict": verdict.verdict,
        "within_rerun_floor": verdict.within_rerun_floor,
        "sensitivity": sensibilidade,
        "warnings": tier.warnings,
    }
    if args.json:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"{args.state} · {args.task} · {args.arm_b} vs {args.arm_a}"
              + ("" if payload["confirmatory"] else "  [EXPLORATORY — unsealed cells]"))
        print(f"  pooled out-of-fold: {args.arm_a} {pooled[args.arm_a]:.4f} · "
              f"{args.arm_b} {pooled[args.arm_b]:.4f}")
        print(f"  {tier.describe()}")
        print(f"  {verdict.describe()}")
        for warning in tier.warnings:
            print(f"  ! {warning}")
        print("  sensitivity: " + " · ".join(f"δ={m}: {v}" for m, v in sensibilidade.items()))

    # A leitura ACABOU de acontecer — registra. Só aqui, e só no modo confirmatório: quem gasta a
    # leitura é quem lê, e registrar antes de ler declararia gasto o que não foi.
    if not args.exploratory:
        _record_reads(registravel, args.state, Path(args.run_root).name,
                      (args.arm_a, args.arm_b))

    return 0


def _identidades(cells, arm: str, state: str) -> dict[str, str]:
    """As identidades científicas de um braço num estado, mapeadas para a receita que as produziu.

    A receita é só o rótulo humano da entrada do livro; quem identifica é o fingerprint.
    """
    saida = {}
    for cell in cells:
        if cell.meta.get("arm") != arm or cell.frame["state"].iloc[0] != state:
            continue
        fingerprint = cell.science_fingerprint()
        if fingerprint:
            saida[fingerprint] = str(cell.meta.get("recipe") or _recipe_of(cell) or "?")
    return saida


def _recipe_of(cell) -> str | None:
    """O caminho da receita, do `result.json` ao lado das predições. Recuo legado, como o
    fingerprint: as células de antes de 23-08 não têm a chave no sidecar."""
    if cell.directory is None:
        return None
    path = Path(cell.directory) / "result.json"
    if not path.exists():
        return None
    return (json.loads(path.read_text()).get("config") or {}).get("recipe")


if __name__ == "__main__":
    raise SystemExit(main())
