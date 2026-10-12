"""T3.x helper — regenerate check2hgi embeddings with a non-canonical encoder.

Forwards into the args namespace consumed by `create_embedding`:
    --encoder {gcn,gat,resln,time2vec,rgcn}
        gcn       canonical CheckinEncoder
        gat       GATTimeEncoder (attention; T3.1)
        resln     ResidualLNEncoder (T3.2)
        time2vec  Time2VecCheckinEncoder (T3.4)
        rgcn      RGCNEncoder (relation-typed; T3.3 — requires --edge-type both)
    --gat-heads INT              (default 4; used if --encoder gat)
    --gat-no-edge-attr           (T3.1 fix 1)
    --encoder-dropout FLOAT      (default 0.0; used by gat/resln/time2vec/rgcn)
    --time2vec-dim INT           (default 8; used if --encoder time2vec)
    --rgcn-num-relations INT     (default 2; used if --encoder rgcn)
    --rgcn-num-bases STR         (default "2"; "none" = full per-relation matrices)
    --rgcn-aggr {sum,mean}       (default sum)
    --edge-type {user_sequence,same_poi,both}
                                 default user_sequence; T3.3 R-GCN requires both

Plus the canonical/T1.5 optimizer flags (v3c base = AdamW WD=5e-2):
    --scheduler {step,cosine,warmup_constant}
    --warmup-pct FLOAT
    --weight-decay FLOAT
    --eta-min-ratio FLOAT
    --epoch INT
"""

import argparse
import sys
from argparse import Namespace
from pathlib import Path

# Path layout: scripts/canonical_improvement/regen_emb_t3.py  →
#   parent[1]=canonical_improvement, parent[2]=scripts, parent[3]=repo_root.
# Pre-refactor (2026-05-17) the file lived in scripts/ and used 4 .parents
# — fixed in-place so the script runs from any worktree.
_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))

from configs.paths import Resources, EmbeddingEngine
from configs.model import InputsConfig
from embeddings.check2hgi.check2hgi import create_embedding
from data.inputs.builders import generate_next_input_from_checkins

STATE_TO_SHP = {
    "alabama": ("Alabama", Resources.TL_AL),
    "arizona": ("Arizona", Resources.TL_AZ),
    "florida": ("Florida", Resources.TL_FL),
    "georgia": ("Georgia", Resources.TL_GA),
    "california": ("California", Resources.TL_CA),
    "texas": ("Texas", Resources.TL_TX),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True, choices=list(STATE_TO_SHP))
    ap.add_argument("--encoder", default="resln",
                    choices=("gcn", "gat", "resln", "time2vec", "rgcn"),
                    help="v12 default 'resln' (ResidualLNEncoder, T3.2 STL-best "
                         "cat encoder; NO MTL benefit). Pass 'gcn' to rebuild "
                         "the v11 paper substrate. See "
                         "docs/results/CANONICAL_VERSIONS.md.")
    ap.add_argument("--gat-heads", type=int, default=4)
    ap.add_argument("--encoder-dropout", type=float, default=0.0)
    ap.add_argument("--gat-no-edge-attr", action="store_true",
                    help="T3.1 fix 1: drop edge_attr (temporal weight) from GAT attention "
                         "conditioning to break the user-sequence-time leak path.")
    ap.add_argument("--time2vec-dim", type=int, default=8,
                    help="T3.4: Time2Vec output dimension (replaces 4 sin/cos cols).")
    ap.add_argument("--time2vec-warm-start", action="store_true",
                    help="T3.4b: warm-start Time2Vec to recover canonical "
                         "sin/cos exactly, then let SGD deviate (mitigates "
                         "the −0.56 cat cost from random init).")
    # T4.3 — POI side-features
    ap.add_argument("--use-side-features", action="store_true",
                    help="T4.3: enable post-pool POI side-feature injection. "
                         "Requires output/check2hgi/{state}/poi_side_features.pt "
                         "(produced by scripts/canonical_improvement/compute_poi_side_features.py). "
                         "Will auto-precompute if missing.")
    ap.add_argument("--side-features-subset", default="no_covisit",
                    choices=("all", "popular", "hours", "covisit", "no_covisit"),
                    help="T4.3: which feature subset to use. Default 'no_covisit' "
                         "(popularity + hours, audit advisor blocker 1: covisit "
                         "carries +3-10pp leak by construction). Use 'covisit' or "
                         "'all' only for the held-out-fclass-split probe ablation.")
    ap.add_argument("--side-feature-hidden", type=int, default=16,
                    help="T4.3: hidden dim of the side-feature projection "
                         "before the concat. Total post-pool projection: "
                         "Linear(D + side_hidden → D).")
    # T4.1 — GraphMAE
    # Default λ=0.3 per INDEX.html T4-1 spec (sweep range {0.1, 0.3, 0.5});
    # audit advisor blocker 3: λ=1.0 over-dominates the contrastive losses.
    ap.add_argument("--mae-lambda", type=float, default=0.0,
                    help="T4.1: coefficient on the masked-recon SCE loss. "
                         "0 disables; spec range {0.1, 0.3, 0.5}; default "
                         "0.3 when enabled.")
    # T2.4 — DropEdge (lets us stack DropEdge with T3.2 ResLN via Hyp B)
    ap.add_argument("--drop-edge-rate", type=float, default=0.0,
                    help="T2.4: fraction of edges to drop per epoch (0 disables).")
    ap.add_argument("--symmetric-drop-edge", action="store_true",
                    help="T2.4 audit fix: drop unique undirected edges symmetrically "
                         "(Rong et al. 2020) instead of per-row independent Bernoulli.")
    ap.add_argument("--mae-mask-rate", type=float, default=0.5,
                    help="T4.1: fraction of check-in nodes whose input "
                         "features get replaced by the [MASK] token before "
                         "the recon encoder pass (default 0.5).")
    ap.add_argument("--mae-gamma", type=float, default=3.0,
                    help="T4.1: SCE exponent (GraphMAE paper recommends "
                         "1.0–4.0; default 3.0).")
    # T5.2a — Joint Node2Vec POI-POI skip-gram (4th boundary, native).
    # Defaults: --n2v-lambda 0.0 → head not built → canonical behavior preserved.
    ap.add_argument("--use-node2vec-poi", action="store_true",
                    help="T5.2a: enable joint Node2Vec POI-POI skip-gram "
                         "auxiliary loss. Builds a POI-level Delaunay graph "
                         "in preprocess (force_preprocess=True is added), runs "
                         "random walks during c2hgi training, and adds "
                         "λ_n2v · L_skipgram to the total loss. NO fclass L2 "
                         "regularizer (would be tautological leak).")
    ap.add_argument("--n2v-lambda", type=float, default=0.3,
                    help="T5.2a: coefficient on the skip-gram auxiliary loss. "
                         "Spec sweep range {0.1, 0.3, 1.0}; default 0.3 when "
                         "enabled. Ignored unless --use-node2vec-poi is set.")
    ap.add_argument("--n2v-walk-length", type=int, default=10,
                    help="T5.2a: Node2Vec walk length (default 10).")
    ap.add_argument("--n2v-num-walks", type=int, default=5,
                    help="T5.2a: walks per node (default 5).")
    ap.add_argument("--n2v-context-size", type=int, default=5,
                    help="T5.2a: skip-gram window size (default 5).")
    ap.add_argument("--n2v-p", type=float, default=1.0,
                    help="T5.2a: Node2Vec return parameter (default 1.0).")
    ap.add_argument("--n2v-q", type=float, default=1.0,
                    help="T5.2a: Node2Vec in-out parameter (default 1.0).")
    ap.add_argument("--n2v-num-negatives", type=int, default=5,
                    help="T5.2a: negative samples per skip-gram positive (default 5).")
    ap.add_argument("--n2v-share-table-with-poi-id", action="store_true",
                    help="T5.2a: when set AND T5.1 (per-POI ID embedding) is "
                         "also enabled, share the same POI embedding table "
                         "between T5.1 and the Node2Vec skip-gram head. Default "
                         "False keeps the tables fully separate (avoids coupling "
                         "T5.2a's signal with T5.1's optimization). Requires "
                         "--use-poi-id-embedding (else raises ValueError at "
                         "model-build time per audit blocker #2).")
    # T5.2a audit blocker #1 fix: alignment term between c2hgi pos_poi_emb
    # and the n2v_head.poi_table.weight. Without this, the skip-gram only
    # trains a private POI table that NEVER reaches the export path
    # (Checkin2POI / CheckinEncoder), so the "T5.2a effect" on downstream
    # MTL is identically zero by construction. Default 0.0 to preserve the
    # T5.2a-as-shipped behaviour bit-for-bit; set to 0.5 (audit recommended
    # baseline) to actually bridge skip-gram gradients into the encoder.
    ap.add_argument("--n2v-align-lambda", type=float, default=0.0,
                    help="T5.2a audit fix: cosine-alignment coefficient "
                         "between c2hgi pos_poi_emb and n2v_head.poi_table.weight. "
                         "Default 0.0 reproduces T5.2a as shipped (phantom-null "
                         "risk). Recommended: 0.5 when --use-node2vec-poi is on "
                         "and --use-poi-id-embedding is off. Ignored unless "
                         "--use-node2vec-poi is set.")
    # T5.3 — Multi-view co-training (cross-view POI alignment)
    # Defaults: --use-multiview OFF → canonical behaviour preserved bit-equiv.
    ap.add_argument("--use-multiview", action="store_true",
                    help="T5.3: enable multi-view co-training. Builds a View-2 "
                         "graph (same_poi-only edges, category-one-hot features) "
                         "alongside the canonical View-1 graph, trains a second "
                         "Check2HGI on it, and adds λ_x · L_cross(poi_v1, poi_v2) "
                         "to the total loss. ~2× compute (two encoders forward + "
                         "backward per step) unless --multiview-share-encoder is set.")
    ap.add_argument("--multiview-lambda", type=float, default=0.3,
                    help="T5.3: λ_x coefficient on the cross-view POI-level "
                         "alignment loss. Spec sweep {0.1, 0.3, 1.0}; default 0.3.")
    ap.add_argument("--multiview-loss", default="cosine",
                    choices=("cosine", "mse", "infonce"),
                    help="T5.3: cross-view loss form. cosine = (1 - cos(v1, v2)).mean() "
                         "(default, per spec). mse = symmetric stop-gradient MSE. "
                         "infonce = symmetric temperature-scaled cross-entropy.")
    ap.add_argument("--multiview-temperature", type=float, default=0.2,
                    help="T5.3: InfoNCE temperature (ignored for cosine / mse).")
    ap.add_argument("--multiview-share-encoder", action="store_true",
                    help="T5.3: share View 1's CheckinEncoder weights with "
                         "View 2 (only c2p/p2r/r2c discriminators + pooling heads "
                         "remain per-view). Halves encoder FLOPs but removes "
                         "the distillation signal at the encoder layer. "
                         "Default False (full 2× compute, full cross-view signal).")
    ap.add_argument("--multiview-export-view", default="v1",
                    choices=("v1", "v2", "ensemble"),
                    help="T5.3: which view's embeddings to export to downstream "
                         "MTL. v1 = canonical/cat-friendly (default, per spec). "
                         "v2 = category-only (diagnostic). ensemble = mean of v1/v2.")
    # T5.1 — Native learned POI ID embedding (additive post-pool).
    # Default opt-out. Importing HGI's POI2Vec to warm-start the table
    # is OUT OF SCOPE (merge-family) — init MUST be zero or small Gaussian.
    ap.add_argument("--use-poi-id-embedding", action="store_true",
                    help="T5.1: enable native learned per-POI identity slot "
                         "added to the Checkin2POI pool. Trained only by "
                         "c2hgi's 3 boundaries (NOT warm-started from POI2Vec). "
                         "Default OFF reproduces canonical c2hgi.")
    ap.add_argument("--poi-id-gamma", type=float, default=0.3,
                    help="T5.1: scalar gamma on the additive table. "
                         "Spec ablation: {0.1, 0.3, 1.0}. Default 0.3.")
    ap.add_argument("--poi-id-init", default="zero", choices=("zero", "gaussian"),
                    help="T5.1: init scheme for the per-POI table. "
                         "'zero' (default) gives strict cold-start neutrality; "
                         "'gaussian' uses N(0, 0.01) to give SGD a non-zero "
                         "starting gradient. POI2Vec warm-start is OUT OF SCOPE.")
    # T5.2b — Masked POI feature-aggregate reconstruction. Paired-falsification
    # counterpart to T4.1 (POI-level vs check-in-level). Defaults MUST preserve
    # canonical: --use-mae-poi off ⇒ no change to outputs / no new artefacts
    # built / no new path through Check2HGI.
    ap.add_argument("--use-mae-poi", action="store_true", default=False,
                    help="T5.2b: enable masked POI feature-aggregate "
                         "reconstruction (POI-level analogue to T4.1 GraphMAE).")
    ap.add_argument("--mae-poi-lambda", type=float, default=0.3,
                    help="T5.2b: coefficient on the masked-POI auxiliary loss "
                         "(spec sweep range {0.1, 0.3}; default 0.3 when "
                         "enabled). Ignored unless --use-mae-poi is set.")
    ap.add_argument("--mae-poi-mask-rate", type=float, default=0.15,
                    help="T5.2b: fraction of POIs whose pooled embedding is "
                         "zeroed-out at each step (default 0.15 per spec).")
    ap.add_argument("--mae-poi-target",
                    default="category_aggregate",
                    choices=("category_aggregate", "visit_count_log", "both"),
                    help="T5.2b: reconstruction target — per-POI mean category "
                         "one-hot (default), log visit count, or both concatenated.")
    ap.add_argument("--mae-poi-gamma", type=float, default=3.0,
                    help="T5.2b: SCE exponent (only used when loss=sce; "
                         "auto-switched to MSE for visit_count_log alone).")
    ap.add_argument("--mae-poi-aggr", default="mean", choices=("mean", "gcn"),
                    help="T5.2b: neighbour aggregation over POI Delaunay edges.")
    ap.add_argument("--mae-poi-loss-kind", default="sce", choices=("sce", "mse"),
                    help="T5.2b: reconstruction loss. SCE matches T4.1 family; "
                         "MSE recommended for visit_count_log alone.")
    ap.add_argument("--rgcn-num-relations", type=int, default=2,
                    help="T3.3: number of edge relation types for R-GCN.")
    ap.add_argument("--rgcn-num-bases", type=str, default="2",
                    help="T3.3: R-GCN basis-decomposition count; 'none' for full "
                         "per-relation matrices (param-heavy).")
    ap.add_argument("--rgcn-aggr", default="sum", choices=("sum", "mean"))
    ap.add_argument("--edge-type", default="user_sequence",
                    choices=("user_sequence", "same_poi", "both", "user_seq_delaunay"),
                    help="Preprocess edge construction. T3.3 R-GCN requires 'both' "
                         "and triggers force_preprocess=True (the cached canonical graph "
                         "lacks per-edge relation index). T4.4 uses "
                         "'user_seq_delaunay' for spatial-lifted GCN.")
    # T6.4 — Tier-6 loss-shape options. Defaults preserve canonical bit-for-bit.
    ap.add_argument("--p2r-use-infonce", action="store_true",
                    help="T6.4 / T2.2: replace JSD-style p2r loss with InfoNCE "
                         "over the full region pool (softmax cross-entropy with "
                         "poi_to_region as target).")
    ap.add_argument("--p2r-infonce-temperature", type=float, default=0.1,
                    help="T6.4 / T2.2: softmax temperature τ for InfoNCE at p2r "
                         "(smaller = harder; default 0.1).")
    ap.add_argument("--two-pass-corruption", action="store_true",
                    help="T6.4 / T2.3: perform an independent second feature-"
                         "corruption pass + encoder + pool + region aggregation, "
                         "and use its outputs as the negatives for p2r and r2c "
                         "(decoupling them from the c2p negative chain). +1 "
                         "encoder pass per step.")
    # T6.1 — POI↔POI co-visit InfoNCE 4th boundary. Default p2p-lambda=0 ⇒
    # canonical bit-identical (no extra forward op, no extra parameters, no
    # new preprocess output).
    ap.add_argument("--p2p-lambda", type=float, default=0.0,
                    help="T6.1: coefficient on the POI↔POI co-visit InfoNCE 4th "
                         "boundary. >0 enables the new objective (zero new "
                         "parameters; shares Checkin2POI pool with c2p/p2r). "
                         "Spec sweep range {0.05, 0.1, 0.2, 0.3}.")
    ap.add_argument("--p2p-temperature", type=float, default=0.1,
                    help="T6.1: softmax temperature τ for the POI↔POI InfoNCE "
                         "(default 0.1, matches T6.4 τ default).")
    ap.add_argument("--p2p-batch-size", type=int, default=1024,
                    help="T6.1: number of (anchor, positive) co-visit pairs "
                         "sampled per training step (default 1024). In-batch "
                         "negatives = batch_size - 1 per anchor.")
    ap.add_argument("--p2p-covisit-k", type=int, default=3,
                    help="T6.1: co-visit window size — for each check-in i, "
                         "consider j ∈ [i+1, i+k-1] as co-visit candidates when "
                         "same-user (default 3 = sequential pairs within 2 steps).")
    ap.add_argument("--p2p-hard-neg-only", action="store_true",
                    help="T6.1: harder variant — mask out in-batch negatives "
                         "from the SAME region as the anchor. Default False "
                         "(standard InfoNCE in-batch negatives). May regress "
                         "at small states with many POIs per region.")
    # T6.1 implementation-robustness options (advisor 2026-05-19). Defaults
    # match the original T6.1 sweep — flipping them tests whether the
    # original null was an implementation artefact (e.g., dedup throwing
    # away popularity signal, asymmetric loss losing half the gradient).
    ap.add_argument("--p2p-no-dedup", action="store_true",
                    help="T6.1 robustness: emit co-visit pairs WITH "
                         "multiplicity at preprocess time (one row per raw "
                         "co-visit adjacency instead of one row per unique "
                         "unordered pair). Uniform sampling of B pairs then "
                         "becomes weighted-by-multiplicity in expectation. "
                         "Forces force_preprocess=True since the cached pair "
                         "list differs.")
    ap.add_argument("--p2p-symmetric", action="store_true",
                    help="T6.1 robustness: average cross-entropy over both "
                         "directions of the similarity matrix (anchor→positive "
                         "AND positive→anchor) following SimCLR. Default False "
                         "matches the original asymmetric (anchor→positive "
                         "only) formulation.")
    # T6.2 — composite C3 edge weights. Default (1.0, 1.0) is canonical
    # bit-identical (no-op). Any ≠ 1.0 triggers force_preprocess to rebuild
    # the user_sequence edge weights with the composite scheme.
    ap.add_argument("--c3-alpha-delaunay", type=float, default=1.0,
                    help="T6.2: edge-weight multiplier for user_sequence edges "
                         "whose endpoint POIs are Delaunay-adjacent. Spec "
                         "sweep {1.5, 2.0}. Default 1.0 = no-op.")
    ap.add_argument("--c3-w-r", type=float, default=1.0,
                    help="T6.2: cross-region penalty — edge-weight multiplier "
                         "for user_sequence edges whose endpoint POIs are in "
                         "DIFFERENT regions. Spec sweep {0.3, 0.5}. Default "
                         "1.0 = no-op.")
    # T6.3 — low-rank per-POI bias at Checkin2POI attention-logit. Default off
    # ⇒ canonical bit-identical (no extra parameters built at __init__).
    ap.add_argument("--t63-enabled", action="store_true",
                    help="T6.3: enable rank-r per-POI bias at the Checkin2POI "
                         "attention LOGIT (not at input or pooled output). "
                         "Zero-init v ⇒ step-0 forward bit-identical to "
                         "canonical. Structural cousin of T5.1 (DEAD) — placed "
                         "differently and capacity-restricted.")
    ap.add_argument("--t63-rank", type=int, default=8,
                    help="T6.3: rank r of the per-POI bias. Spec sweep "
                         "{4, 8}. Default 8.")
    # T1.5 optimizer hygiene knobs (default = canonical Adam + StepLR γ=1; v3c base = AdamW WD=5e-2)
    ap.add_argument("--scheduler", default="step", choices=("step", "cosine", "warmup_constant"))
    ap.add_argument("--warmup-pct", type=float, default=0.0)
    ap.add_argument("--weight-decay", type=float, default=0.0)
    ap.add_argument("--eta-min-ratio", type=float, default=0.01)
    ap.add_argument("--epoch", type=int, default=500)
    args = ap.parse_args()

    # R-GCN requires the multi-relation graph. The cached canonical graph
    # (edge_type='user_sequence') has no per-edge relation index, so we must
    # force a fresh preprocess for R-GCN. (T3.3 advisor pre-launch audit.)
    # T5.2a / T5.2b also need a fresh preprocess to add the POI Delaunay
    # edge list and/or per-POI aggregate targets if the cache lacks them.
    # ``create_embedding`` additionally peeks at the cache and rebuilds on
    # demand, so passing force_preprocess here is belt-and-braces.
    _force_preprocess = (
        (args.encoder == "rgcn")
        or (args.edge_type != "user_sequence")
        or bool(args.use_node2vec_poi)
        or bool(args.use_mae_poi)
        or float(args.p2p_lambda) > 0.0   # T6.1: needs covisit_pairs cached
        # T6.1 robustness: dedup mode is encoded in the cached pair table,
        # so a no-dedup run must rebuild the cache even if covisit_pairs
        # is already present.
        or bool(args.p2p_no_dedup)
        # T6.2: composite C3 edge weights change the cached edge_weight
        # array; force_preprocess so the new weights take effect.
        or float(args.c3_alpha_delaunay) != 1.0
        or float(args.c3_w_r) != 1.0
    )

    # T5.2a — effective λ. When the flag is OFF, force λ=0 so default
    # (no flag) behavior is bit-equivalent to canonical.
    _n2v_lambda_eff = float(args.n2v_lambda) if args.use_node2vec_poi else 0.0

    name_camel, shapefile = STATE_TO_SHP[args.state]
    # NOTE (advisor 2026-05-15): num_layers is pinned to 2 here to match the
    # canonical CheckinEncoder depth used by every accepted Tier-1/Tier-2
    # variant. variants.py:86 (ResidualLNEncoder) defaults to 3 — DO NOT rely
    # on that default in any T3 recipe; the CLI value below is authoritative
    # so the GAT/ResLN/GCN comparison stays depth-controlled.
    # Tier-3 audit finding (2026-05-16): train_check2hgi now calls
    # torch.manual_seed(args.seed) for bit-reproducibility of the SSL encoder
    # init. Pull the seed from the runner's $SEED env var (set in
    # parallel_sweep_runner.sh line 55: SEED=${SEED:-42}). Without this,
    # cfg.seed would default to 42 inside check2hgi.py → all "multi-seed"
    # runs would get identical encoders, BREAKING the multi-seed claim.
    import os as _os
    _ssl_seed = int(_os.environ.get('SEED', '42'))

    cfg = Namespace(
        dim=InputsConfig.EMBEDDING_DIM,
        num_layers=2,
        seed=_ssl_seed,
        # T3.4 + T3.3 plumbing
        time2vec_dim=args.time2vec_dim,
        time2vec_warm_start=args.time2vec_warm_start,
        rgcn_num_relations=args.rgcn_num_relations,
        rgcn_num_bases=args.rgcn_num_bases,
        rgcn_aggr=args.rgcn_aggr,
        # T4.3 + T4.1 plumbing
        use_side_features=args.use_side_features,
        side_feature_hidden=args.side_feature_hidden,
        mae_lambda=args.mae_lambda,
        mae_mask_rate=args.mae_mask_rate,
        mae_gamma=args.mae_gamma,
        # T5.1 — Native learned POI ID embedding plumbing.
        use_poi_id_embedding=args.use_poi_id_embedding,
        poi_id_gamma=args.poi_id_gamma,
        poi_id_init=args.poi_id_init,
        # T5.2b plumbing — gated by --use-mae-poi. When OFF, mae_poi_lambda=0
        # ⇒ Check2HGI takes the canonical path bit-identically.
        mae_poi_lambda=(args.mae_poi_lambda if args.use_mae_poi else 0.0),
        mae_poi_mask_rate=args.mae_poi_mask_rate,
        mae_poi_gamma=args.mae_poi_gamma,
        mae_poi_target=args.mae_poi_target,
        mae_poi_aggr=args.mae_poi_aggr,
        mae_poi_loss_kind=args.mae_poi_loss_kind,
        # T2.4 + Hyp B plumbing
        drop_edge_rate=args.drop_edge_rate,
        symmetric_drop_edge=args.symmetric_drop_edge,
        # T5.2a plumbing — default-opt-out (n2v_lambda=0 when flag off)
        n2v_lambda=_n2v_lambda_eff,
        n2v_walk_length=args.n2v_walk_length,
        n2v_num_walks=args.n2v_num_walks,
        n2v_context_size=args.n2v_context_size,
        n2v_p=args.n2v_p,
        n2v_q=args.n2v_q,
        n2v_num_negatives=args.n2v_num_negatives,
        n2v_share_table_with_poi_id=args.n2v_share_table_with_poi_id,
        n2v_align_lambda=float(args.n2v_align_lambda) if args.use_node2vec_poi else 0.0,
        # T5.3 plumbing — default-opt-out (use_multiview=False preserves canonical)
        use_multiview=args.use_multiview,
        multiview_lambda=args.multiview_lambda,
        multiview_loss=args.multiview_loss,
        multiview_temperature=args.multiview_temperature,
        multiview_share_encoder=args.multiview_share_encoder,
        multiview_export_view=args.multiview_export_view,
        attention_head=4,
        alpha_c2p=0.4,
        alpha_p2r=0.3,
        alpha_r2c=0.3,
        lr=0.001,
        gamma=1.0,
        max_norm=0.9,
        epoch=args.epoch,
        mini_batch_threshold=5_000_000,
        batch_size=2**13,
        num_neighbors=10,
        device='cuda',
        shapefile=shapefile,
        force_preprocess=_force_preprocess,
        edge_type=args.edge_type,
        temporal_decay=3600.0,
        use_compile=True,
        use_amp=False,
        encoder=args.encoder,
        gat_heads=args.gat_heads,
        encoder_dropout=args.encoder_dropout,
        gat_use_edge_attr=not args.gat_no_edge_attr,
        scheduler=args.scheduler,
        warmup_pct=args.warmup_pct,
        weight_decay=args.weight_decay,
        eta_min_ratio=args.eta_min_ratio,
        # T6.4 plumbing
        p2r_use_infonce=args.p2r_use_infonce,
        p2r_infonce_temperature=args.p2r_infonce_temperature,
        two_pass_corruption=args.two_pass_corruption,
        # T6.1 plumbing
        p2p_lambda=float(args.p2p_lambda),
        p2p_temperature=float(args.p2p_temperature),
        p2p_batch_size=int(args.p2p_batch_size),
        p2p_covisit_k=int(args.p2p_covisit_k),
        p2p_hard_neg_only=bool(args.p2p_hard_neg_only),
        # T6.1 robustness options (advisor 2026-05-19)
        p2p_no_dedup=bool(args.p2p_no_dedup),
        p2p_symmetric=bool(args.p2p_symmetric),
        # T6.2 — composite C3 edge weights
        c3_alpha_delaunay=float(args.c3_alpha_delaunay),
        c3_w_r=float(args.c3_w_r),
        # T6.3 — low-rank POI side-channel at Checkin2POI attention-logit
        t63_enabled=bool(args.t63_enabled),
        t63_rank=int(args.t63_rank),
    )
    print(f"[T3-regen] state={args.state} encoder={args.encoder} "
          f"edge_type={args.edge_type} force_preprocess={_force_preprocess} "
          f"sched={args.scheduler} wd={args.weight_decay} epoch={args.epoch} "
          f"side_features={args.use_side_features} mae_lambda={args.mae_lambda} "
          f"n2v_lambda={_n2v_lambda_eff} "
          f"(use_node2vec_poi={bool(args.use_node2vec_poi)} "
          f"align_λ={float(getattr(args, 'n2v_align_lambda', 0.0) or 0.0)}) "
          f"multiview={bool(args.use_multiview)} "
          f"(λ_x={args.multiview_lambda} loss={args.multiview_loss} "
          f"share_enc={bool(args.multiview_share_encoder)} "
          f"export={args.multiview_export_view}) "
          f"poi_id={args.use_poi_id_embedding} γ={args.poi_id_gamma} "
          f"init={args.poi_id_init} "
          f"p2r_infonce={args.p2r_use_infonce} τ={args.p2r_infonce_temperature} "
          f"two_pass={args.two_pass_corruption} "
          f"p2p_lambda={args.p2p_lambda} τ_p2p={args.p2p_temperature} "
          f"k={args.p2p_covisit_k} batch={args.p2p_batch_size} "
          f"hard_neg_only={args.p2p_hard_neg_only} "
          f"no_dedup={args.p2p_no_dedup} symmetric={args.p2p_symmetric} "
          f"c3_alpha_delaunay={args.c3_alpha_delaunay} c3_w_r={args.c3_w_r} "
          f"t63_enabled={args.t63_enabled} t63_rank={args.t63_rank} "
          f"use_mae_poi={args.use_mae_poi} "
          f"mae_poi_lambda={args.mae_poi_lambda if args.use_mae_poi else 0.0} "
          f"mae_poi_target={args.mae_poi_target}",
          flush=True)

    # T4.3: pre-compute POI side-features if needed and not yet on disk.
    # Each subset gets its own filename so ablations don't clobber each other.
    if args.use_side_features:
        from pathlib import Path as _Path
        from configs.paths import IoPaths as _IoPaths
        _sf_path = _Path(_IoPaths.CHECK2HGI.get_state_dir(name_camel)) / "poi_side_features.pt"
        # NOTE: the encoder reads exactly poi_side_features.pt (canonical name).
        # We always (re)compute to ensure the on-disk tensor matches the
        # requested subset, since different subsets share the filename.
        print(f"[T4.3] (re)computing side features subset={args.side_features_subset} → {_sf_path}",
              flush=True)
        from subprocess import run as _run
        cmd = [sys.executable, str(_root / "scripts" / "canonical_improvement" / "compute_poi_side_features.py"),
               "--state", args.state,
               "--subset", args.side_features_subset]
        r = _run(cmd, check=False)
        if r.returncode != 0:
            raise RuntimeError(
                f"compute_poi_side_features.py failed (rc={r.returncode}). "
                f"Ensure preprocess cache exists at "
                f"output/check2hgi/{name_camel}/temp/checkin_graph.pt."
            )

    create_embedding(state=name_camel, args=cfg)
    print(f"[inputs] state={args.state} regenerating next-POI inputs", flush=True)
    generate_next_input_from_checkins(name_camel, EmbeddingEngine.CHECK2HGI)

    # C22 fix (2026-05-20): rebuild per-fold log_T at seed=42 to prevent stale
    # log_T silently surviving across regens. Tier 6 FL-MTL sweeps used May-6
    # stale log_T that inflated reg-Acc@10 by ~12 pp at MTL disjoint / ~8 pp at
    # STL. See docs/CONCERNS.md C22 and docs/results/mtl_protocol_fix/phase1_verdict.md.
    # Multi-seed callers must additionally invoke compute_region_transition.py
    # explicitly for each non-42 seed.
    print(f"[log_T] rebuilding per-fold log_T at seed=42 (C22 guardrail)", flush=True)
    from subprocess import run as _run
    cmd_logt = [sys.executable, str(_root / "scripts" / "compute_region_transition.py"),
                "--state", args.state, "--per-fold", "--seed", "42"]
    r = _run(cmd_logt, check=False)
    if r.returncode != 0:
        print(f"[log_T] WARNING: rebuild failed (rc={r.returncode}). "
              f"Per-fold log_T at output/check2hgi/{args.state}/region_transition_log_seed42_fold*.pt "
              f"may be STALE. Run compute_region_transition.py manually before training.",
              flush=True)
    print(f"[done] state={args.state}", flush=True)


if __name__ == "__main__":
    main()
